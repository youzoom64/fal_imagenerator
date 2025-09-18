"""画像生成処理ハンドラー"""
import threading
import os
from ...utils.file_utils import save_image_from_url

class GenerationHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.model_manager = main_window.model_manager
        self.image_generator = main_window.image_generator
    
    def start_generation(self):
        """画像生成を開始"""
        # バリデーション
        if not self.main_window.api_frame.get_api_key():
            self.main_window.update_status("エラー: APIキーが設定されていません")
            return
        
        prompt = self.main_window.prompt_frame.get_prompt()
        if not prompt:
            self.main_window.update_status("エラー: プロンプトを入力してください")
            return
        
        # プロンプトを履歴に保存
        if self.config_manager.get("auto_save_prompts", True):
            self.main_window.prompt_frame.save_to_history()
        
        # image-to-imageモードの場合、画像が選択されているかチェック
        if self.main_window.current_mode == "image-to-image":
            if not self.main_window.image_input_frame.has_image():
                self.main_window.update_status("エラー: 変換元の画像を選択してください")
                return
        
        # UI状態を変更
        self.main_window.generate_button.config(state="disabled")
        self.main_window.progress.start()
        
        selected_model = self.main_window.model_frame.get_selected_model_endpoint()
        safety_status = "有効" if self.main_window.settings_frame.safety_checker_var.get() else "無効"
        mode_text = "画像変換中..." if self.main_window.current_mode == "image-to-image" else "画像生成中..."
        self.main_window.update_status(f"{mode_text} (モデル: {selected_model}, 安全性フィルター: {safety_status})")
        
        # 別スレッドで画像生成実行
        thread = threading.Thread(target=self.generate_image)
        thread.daemon = True
        thread.start()
    
    def generate_image(self):
        """画像生成の実行"""
        try:
            prompt = self.main_window.prompt_frame.get_prompt()
            negative_prompt = self.main_window.prompt_frame.get_negative_prompt()
            selected_model = self.main_window.model_frame.get_selected_model_endpoint()
            generation_settings = self.main_window.settings_frame.get_generation_settings()
            
            if self.main_window.current_mode == "text-to-image":
                # text-to-image生成
                image_size_params = self.main_window.size_frame.get_image_size_params()
                
                generation_params = self.image_generator.build_text_to_image_params(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=generation_settings["num_inference_steps"],
                    guidance_scale=generation_settings["guidance_scale"],
                    num_images=generation_settings["num_images"],
                    enable_safety_checker=generation_settings["enable_safety_checker"],
                    image_size_params=image_size_params,
                    seed=generation_settings["seed"]
                )
            # image-to-image変換部分の修正
            else:
                # image-to-image変換
                # 画像を取得（パスまたはPILオブジェクト）
                image_path = self.main_window.image_input_frame.get_image_path()
                if not image_path:
                    # クリップボード画像の場合
                    temp_path = self.main_window.image_input_frame.save_temp_image()
                    upload_result = self.image_generator.upload_image_to_fal_sync(temp_path)
                else:
                    upload_result = self.image_generator.upload_image_to_fal_sync(image_path)
                
                if not upload_result["success"]:
                    self.main_window.root.after(0, lambda: self.handle_generation_error(upload_result["error"]))
                    return
                
                image_url = upload_result["url"]
                
                generation_params = self.image_generator.build_image_to_image_params(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image_url=image_url,
                    strength=generation_settings["strength"],
                    num_inference_steps=generation_settings["num_inference_steps"],
                    guidance_scale=generation_settings["guidance_scale"],
                    num_images=generation_settings["num_images"],
                    enable_safety_checker=generation_settings["enable_safety_checker"],
                    seed=generation_settings["seed"]
                )
            
            # 画像生成実行
            result = self.image_generator.generate(
                api_key=self.main_window.api_frame.get_api_key(),
                model_endpoint=selected_model,
                generation_params=generation_params
            )
            
            if result["success"]:
                self.main_window.root.after(0, lambda: self.handle_generation_success(result["data"]))
            else:
                self.main_window.root.after(0, lambda: self.handle_generation_error(result["error"]))
                
        except Exception as e:
            self.main_window.root.after(0, lambda: self.handle_generation_error(str(e)))  

    def handle_generation_success(self, result):
        """画像生成成功時の処理"""
        try:
            saved_files = []
            
            # 各画像を保存
            for i, image_data in enumerate(result['images']):
                filename = self.image_generator.generate_filename(i, self.main_window.current_mode)
                filepath = os.path.join(self.image_generator.get_output_dir(), filename)
                
                save_result = save_image_from_url(image_data['url'], filepath)
                if save_result["success"]:
                    saved_files.append(filename)
                else:
                    self.handle_generation_error(f"画像保存エラー: {save_result['error']}")
                    return
            
            # 結果表示
            self.main_window.result_frame.display_images(result['images'], saved_files)
            
            # ステータス更新
            safety_status = "フィルター有効" if self.main_window.settings_frame.safety_checker_var.get() else "フィルター無効"
            mode_text = "変換完了" if self.main_window.current_mode == "image-to-image" else "生成完了"
            status_msg = f"{mode_text}！ {len(result['images'])}枚自動保存 ({safety_status}): {', '.join(saved_files)}"
            self.main_window.update_status(status_msg)
            
        except Exception as e:
            self.handle_generation_error(str(e))
        finally:
            self.main_window.progress.stop()
            self.main_window.generate_button.config(state="normal")
    
    def handle_generation_error(self, error_message):
        """画像生成エラー時の処理"""
        self.main_window.progress.stop()
        self.main_window.generate_button.config(state="normal")
        self.main_window.update_status(f"エラー: {error_message}")