"""UI操作処理ハンドラー（自動保存対応）"""
import tkinter as tk
from ...utils.system_utils import open_folder

class UIHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.model_manager = main_window.model_manager
        self.image_generator = main_window.image_generator
    
    def setup_layout(self):
        """レイアウトを設定"""
        row = 0
        
        # コンポーネントの配置
        self.main_window.api_frame.frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        self.main_window.mode_frame.frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        self.main_window.model_frame.frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        self.main_window.prompt_frame.frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # 画像入力フレーム（image-to-image用、初期は非表示）
        self.main_window.image_input_row = row
        row += 1
        
        # サイズ設定フレーム
        self.main_window.size_frame.frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.main_window.size_row = row
        row += 1
        
        self.main_window.settings_frame.frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        self.main_window.button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        self.main_window.progress.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        self.main_window.status_label.grid(row=row, column=0, columnspan=2, pady=(0, 10))
        row += 1
        
        self.main_window.result_frame.frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # グリッドの重みを設定
        self.main_window.main_frame.columnconfigure(1, weight=1)
        self.main_window.main_frame.rowconfigure(row, weight=1)  # 結果フレームが拡張可能
        
        # 初期モード設定
        self.on_mode_change(self.main_window.current_mode)
    
    def setup_bindings(self):
        """イベントバインディングを設定"""
        # 設定変更時の自動保存バインディング
        self.setup_auto_save_bindings()
        
        # 初回のモデル変更イベントを発火
        self.on_model_change(self.main_window.model_frame.get_selected_model_endpoint())
    
    def setup_auto_save_bindings(self):
        """自動保存のためのイベントバインディングを設定（エラーハンドリング強化）"""
        try:
            # プロンプトテキスト変更時（少し遅延を入れる）
            def delayed_save(event=None):
                if hasattr(self, '_save_after_id'):
                    self.main_window.root.after_cancel(self._save_after_id)
                self._save_after_id = self.main_window.root.after(1000, self.on_setting_change)
            
            self.main_window.prompt_frame.prompt_text.bind('<KeyRelease>', delayed_save)
            self.main_window.prompt_frame.negative_prompt_text.bind('<KeyRelease>', delayed_save)
            
            # 変数変更の監視を安全に設定
            def safe_trace(var, callback):
                try:
                    var.trace_add('write', lambda *args: self.safe_on_setting_change())
                except:
                    # 古いバージョンのTkinter用
                    try:
                        var.trace('w', lambda *args: self.safe_on_setting_change())
                    except:
                        pass
            
            # スピンボックス変更時
            safe_trace(self.main_window.settings_frame.inference_steps_var, self.safe_on_setting_change)
            safe_trace(self.main_window.settings_frame.guidance_scale_var, self.safe_on_setting_change)
            safe_trace(self.main_window.settings_frame.num_images_var, self.safe_on_setting_change)
            safe_trace(self.main_window.settings_frame.strength_var, self.safe_on_setting_change)
            
            # チェックボックス変更時
            safe_trace(self.main_window.settings_frame.safety_checker_var, self.safe_on_setting_change)
            
            # サイズ設定変更時
            safe_trace(self.main_window.size_frame.use_custom_size_var, self.safe_on_setting_change)
            safe_trace(self.main_window.size_frame.image_size_var, self.safe_on_setting_change)
            safe_trace(self.main_window.size_frame.custom_width_var, self.safe_on_setting_change)
            safe_trace(self.main_window.size_frame.custom_height_var, self.safe_on_setting_change)
            
        except Exception as e:
            print(f"自動保存バインディングエラー: {e}")

    def safe_on_setting_change(self, *args):
        """安全な設定変更ハンドラー"""
        try:
            # 少し遅延してから保存（連続変更に対応）
            if hasattr(self, '_auto_save_after_id'):
                self.main_window.root.after_cancel(self._auto_save_after_id)
            self._auto_save_after_id = self.main_window.root.after(2000, self.auto_save_current_settings)
        except Exception as e:
            print(f"設定変更処理エラー: {e}")

    def on_setting_change(self, *args):
        """設定変更時の自動保存（安全版）"""
        self.safe_on_setting_change(*args)
    
    def auto_save_current_settings(self):
        """現在の設定を自動保存（遅延実行）- エラーハンドリング強化"""
        try:
            # 値を安全に取得する関数
            def safe_get_value(var, default_value, var_type=str):
                try:
                    if var_type == float:
                        val = var.get()
                        return val if val != "" else default_value
                    elif var_type == int:
                        val = var.get()
                        return val if val != "" else default_value
                    else:
                        return var.get()
                except:
                    return default_value
            settings_to_save = {
                "default_prompt": safe_get_value(tk.StringVar(), self.main_window.prompt_frame.get_prompt()),
                "default_negative_prompt": safe_get_value(tk.StringVar(), self.main_window.prompt_frame.get_negative_prompt()),
                "default_model": self.main_window.model_frame.get_selected_model_endpoint(),
                "default_image_size": safe_get_value(self.main_window.size_frame.image_size_var, "landscape_4_3"),
                "default_custom_width": safe_get_value(self.main_window.size_frame.custom_width_var, 1024, int),
                "default_custom_height": safe_get_value(self.main_window.size_frame.custom_height_var, 768, int),
                "default_use_custom_size": safe_get_value(self.main_window.size_frame.use_custom_size_var, False, bool),
                "default_inference_steps": safe_get_value(self.main_window.settings_frame.inference_steps_var, 28, int),
                "default_guidance_scale": safe_get_value(self.main_window.settings_frame.guidance_scale_var, 3.5, float),
                "default_num_images": safe_get_value(self.main_window.settings_frame.num_images_var, 1, int),
                "enable_safety_checker": safe_get_value(self.main_window.settings_frame.safety_checker_var, True, bool),
                "default_strength": safe_get_value(self.main_window.settings_frame.strength_var, 0.95, float)
            }
            
            self.config_manager.update(settings_to_save)
        except Exception as e:
            # エラーが発生した場合はサイレントに処理
            print(f"設定自動保存エラー: {e}")
    
    def on_mode_change(self, mode):
        """モード変更時の処理"""
        self.main_window.current_mode = mode
        
        # モードを設定に保存
        self.config_manager.set("last_mode", mode)
        
        # 各コンポーネントにモードを通知
        self.main_window.model_frame.set_mode(mode)
        self.main_window.settings_frame.set_mode(mode)
        
        if mode == "image-to-image":
            # 画像入力フレームを表示
            self.main_window.image_input_frame.frame.grid(row=self.main_window.image_input_row, column=0, columnspan=2, 
                                            sticky=(tk.W, tk.E), pady=(0, 10))
            # サイズ設定フレームを非表示（image-to-imageでは元画像のサイズが基準）
            self.main_window.size_frame.frame.grid_remove()
            
            # ボタンテキストを更新
            self.main_window.generate_button.configure(text="画像変換開始")
            
            # ウィンドウタイトルを更新
            self.main_window.root.title("FAL.ai Image Generator - Image-to-Image Mode")
        else:
            # 画像入力フレームを非表示
            self.main_window.image_input_frame.frame.grid_remove()
            # サイズ設定フレームを表示
            self.main_window.size_frame.frame.grid(row=self.main_window.size_row, column=0, columnspan=2, 
                                     sticky=(tk.W, tk.E), pady=(0, 10))
            
            # ボタンテキストを更新
            self.main_window.generate_button.configure(text="画像生成開始")
            
            # ウィンドウタイトルを更新
            self.main_window.root.title("FAL.ai Image Generator - Text-to-Image Mode")
        
        self.main_window.update_status(f"モード変更: {mode} - 自動保存先: {self.image_generator.get_output_dir()}")
    
    def on_model_change(self, model_endpoint, event=None):
        """モデル変更時の処理"""
        # 設定フレームの制約を更新
        self.main_window.settings_frame.update_model_constraints(model_endpoint)
        
        # モデル選択を設定に保存
        self.config_manager.set("default_model", model_endpoint)
        
        # ステータス更新
        model_name = self.main_window.model_frame.get_selected_model_display_name()
        model_params = self.model_manager.get_model_parameters(model_endpoint)
        max_steps = model_params.get("max_inference_steps", 50)
        
        if event is not None:
            self.main_window.update_status(f"モデル選択: {model_name} (最大ステップ数: {max_steps}) - 自動保存先: {self.image_generator.get_output_dir()}")
    
    def save_current_settings(self):
        """現在の設定を手動保存"""
        settings_to_save = {
            "api_key": self.main_window.api_frame.get_api_key(),
            "default_model": self.main_window.model_frame.get_selected_model_endpoint(),
            "default_prompt": self.main_window.prompt_frame.get_prompt(),
            "default_negative_prompt": self.main_window.prompt_frame.get_negative_prompt(),
            "default_image_size": self.main_window.size_frame.image_size_var.get(),
            "default_custom_width": self.main_window.size_frame.custom_width_var.get(),
            "default_custom_height": self.main_window.size_frame.custom_height_var.get(),
            "default_use_custom_size": self.main_window.size_frame.use_custom_size_var.get(),
            "default_inference_steps": self.main_window.settings_frame.inference_steps_var.get(),
            "default_guidance_scale": self.main_window.settings_frame.guidance_scale_var.get(),
            "default_num_images": self.main_window.settings_frame.num_images_var.get(),
            "enable_safety_checker": self.main_window.settings_frame.safety_checker_var.get(),
            "default_strength": self.main_window.settings_frame.strength_var.get(),
            "last_mode": self.main_window.current_mode
        }
        
        self.config_manager.update(settings_to_save)
        self.config_manager.save_config()  # 即座に保存
        self.main_window.update_status("設定を手動保存しました")
    
    def open_output_folder(self):
        """出力フォルダを開く"""
        if open_folder(self.image_generator.get_output_dir()):
            self.main_window.update_status("出力フォルダを開きました")
        else:
            self.main_window.update_status("出力フォルダを開けませんでした")