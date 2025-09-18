import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import threading
import requests
import fal_client
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser

class FluxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FAL.ai Image Generator")
        self.root.geometry("800x1000")
        self.root.resizable(True, True)
        
        # 利用可能なモデル定義
        self.available_models = {
            "FLUX.1 [dev] - 高品質バランス型": "fal-ai/flux/dev",
            "FLUX.1 [schnell] - 高速生成": "fal-ai/flux/schnell", 
            "FLUX.1 Pro v1.1 - 最高品質": "fal-ai/flux-pro/v1.1",
            "FLUX.1 Pro Ultra - 2K対応": "fal-ai/flux-pro/v1.1-ultra",
            "Recraft V3 - ベクターアート特化": "fal-ai/recraft-v3",
            "Stable Diffusion 3.5 Large - 汎用高品質": "fal-ai/stable-diffusion-v35-large",
            "Ideogram V3 - タイポグラフィ特化": "fal-ai/ideogram/v3",
            "FLUX with LoRA - カスタマイゼーション": "fal-ai/flux-lora",
            "Fast SDXL - 高速SDXL": "fal-ai/fast-sdxl",
            "Qwen Image - テキスト編集特化": "fal-ai/qwen-image"
        }
        
        # モデルごとのパラメータ制限を定義
        self.model_parameters = {
            "fal-ai/flux/dev": {"max_inference_steps": 28, "default_inference_steps": 28, "default_guidance_scale": 3.5},
            "fal-ai/flux/schnell": {"max_inference_steps": 4, "default_inference_steps": 4, "default_guidance_scale": 3.5},
            "fal-ai/flux-pro/v1.1": {"max_inference_steps": 25, "default_inference_steps": 25, "default_guidance_scale": 3.5},
            "fal-ai/flux-pro/v1.1-ultra": {"max_inference_steps": 25, "default_inference_steps": 25, "default_guidance_scale": 3.5},
            "fal-ai/recraft-v3": {"max_inference_steps": 12, "default_inference_steps": 12, "default_guidance_scale": 7.5},
            "fal-ai/stable-diffusion-v35-large": {"max_inference_steps": 50, "default_inference_steps": 28, "default_guidance_scale": 7.5},
            "fal-ai/ideogram/v3": {"max_inference_steps": 12, "default_inference_steps": 12, "default_guidance_scale": 7.5},
            "fal-ai/flux-lora": {"max_inference_steps": 28, "default_inference_steps": 28, "default_guidance_scale": 3.5},
            "fal-ai/fast-sdxl": {"max_inference_steps": 8, "default_inference_steps": 5, "default_guidance_scale": 2.0},
            "fal-ai/qwen-image": {"max_inference_steps": 20, "default_inference_steps": 20, "default_guidance_scale": 7.5}
        }
        
        # 自動保存ディレクトリを作成
        self.output_dir = "generated_images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 設定を読み込み
        self.load_config()
        
        # UIを作成
        self.create_ui()
        
        # 生成された画像のリスト
        self.generated_images = []
        
    def load_config(self):
        """config.jsonから設定を読み込み"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "api_key": "",
                "default_model": "fal-ai/flux/dev",
                "default_prompt": "A beautiful landscape with mountains and cherry blossoms",
                "default_image_size": "landscape_4_3",
                "default_custom_width": 1024,
                "default_custom_height": 768,
                "default_inference_steps": 28,
                "default_guidance_scale": 3.5,
                "default_num_images": 1,
                "default_use_custom_size": False,
                "enable_safety_checker": False
            }
            self.save_config()
    
    def save_config(self):
        """設定をconfig.jsonに保存"""
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def create_ui(self):
        """UIを作成"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # APIキー設定フレーム
        api_frame = ttk.LabelFrame(main_frame, text="API設定", padding="5")
        api_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(api_frame, text="APIキー:").grid(row=0, column=0, sticky=tk.W)
        self.api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=60, show="*")
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(api_frame, text="保存", command=self.save_api_key).grid(row=0, column=2, padx=(5, 0))
        
        # モデル選択フレーム
        model_frame = ttk.LabelFrame(main_frame, text="モデル選択", padding="5")
        model_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(model_frame, text="モデル:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_var = tk.StringVar()
        default_model_key = self.get_model_display_name(self.config.get("default_model", "fal-ai/flux/dev"))
        self.model_var.set(default_model_key)
        
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                       values=list(self.available_models.keys()), 
                                       state="readonly", width=50)
        self.model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)
        
        # プロンプト入力フレーム
        prompt_frame = ttk.LabelFrame(main_frame, text="プロンプト", padding="5")
        prompt_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=10, width=80)
        self.prompt_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.prompt_text.insert(tk.END, self.config.get("default_prompt", ""))
        
        # 画像サイズ設定フレーム
        size_frame = ttk.LabelFrame(main_frame, text="画像サイズ設定", padding="5")
        size_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.use_custom_size_var = tk.BooleanVar(value=self.config.get("default_use_custom_size", False))
        preset_radio = ttk.Radiobutton(size_frame, text="プリセットを使用", variable=self.use_custom_size_var, 
                                      value=False, command=self.on_size_mode_change)
        preset_radio.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        custom_radio = ttk.Radiobutton(size_frame, text="カスタムサイズ (px)", variable=self.use_custom_size_var, 
                                      value=True, command=self.on_size_mode_change)
        custom_radio.grid(row=0, column=1, sticky=tk.W, padx=(20, 0), pady=2)
        
        # プリセットサイズ
        self.preset_frame = ttk.Frame(size_frame)
        self.preset_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.preset_frame, text="プリセット:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.image_size_var = tk.StringVar(value=self.config.get("default_image_size", "landscape_4_3"))
        image_size_combo = ttk.Combobox(self.preset_frame, textvariable=self.image_size_var, 
                                       values=["square_hd", "landscape_4_3", "landscape_16_9", "portrait_4_3", "portrait_16_9"])
        image_size_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # カスタムサイズ
        self.custom_frame = ttk.Frame(size_frame)
        self.custom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.custom_frame, text="幅:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.custom_width_var = tk.IntVar(value=self.config.get("default_custom_width", 1024))
        width_spin = ttk.Spinbox(self.custom_frame, from_=64, to=2048, increment=64, 
                                textvariable=self.custom_width_var, width=10)
        width_spin.grid(row=0, column=1, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(self.custom_frame, text="px    高さ:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.custom_height_var = tk.IntVar(value=self.config.get("default_custom_height", 768))
        height_spin = ttk.Spinbox(self.custom_frame, from_=64, to=2048, increment=64, 
                                 textvariable=self.custom_height_var, width=10)
        height_spin.grid(row=0, column=3, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(self.custom_frame, text="px").grid(row=0, column=4, sticky=tk.W)
        
        # 設定フレーム
        settings_frame = ttk.LabelFrame(main_frame, text="生成設定", padding="5")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 推論ステップ数
        ttk.Label(settings_frame, text="推論ステップ数:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.inference_steps_var = tk.IntVar(value=self.config.get("default_inference_steps", 28))
        
        initial_model = self.get_selected_model_endpoint()
        max_steps = self.model_parameters.get(initial_model, {}).get("max_inference_steps", 50)
        
        self.inference_steps_spin = ttk.Spinbox(settings_frame, from_=1, to=max_steps, 
                                               textvariable=self.inference_steps_var, width=10)
        self.inference_steps_spin.grid(row=0, column=1, sticky=tk.W, padx=(5, 10))
        
        self.max_steps_label = ttk.Label(settings_frame, text=f"(最大: {max_steps})", foreground="gray")
        self.max_steps_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # ガイダンススケール
        ttk.Label(settings_frame, text="ガイダンススケール:").grid(row=0, column=3, sticky=tk.W, pady=2)
        self.guidance_scale_var = tk.DoubleVar(value=self.config.get("default_guidance_scale", 3.5))
        guidance_scale_spin = ttk.Spinbox(settings_frame, from_=1.0, to=20.0, increment=0.5, 
                                         textvariable=self.guidance_scale_var, width=10)
        guidance_scale_spin.grid(row=0, column=4, sticky=tk.W, padx=(5, 0))
        
        # 画像枚数
        ttk.Label(settings_frame, text="画像枚数:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.num_images_var = tk.IntVar(value=self.config.get("default_num_images", 1))
        num_images_spin = ttk.Spinbox(settings_frame, from_=1, to=4, textvariable=self.num_images_var, width=10)
        num_images_spin.grid(row=1, column=1, sticky=tk.W, padx=(5, 20))
        
        # シード値
        ttk.Label(settings_frame, text="シード値:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.seed_var = tk.StringVar()
        seed_entry = ttk.Entry(settings_frame, textvariable=self.seed_var, width=15)
        seed_entry.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), columnspan=2)
        
        # 安全性フィルター設定
        ttk.Label(settings_frame, text="安全性フィルター:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.safety_checker_var = tk.BooleanVar(value=self.config.get("enable_safety_checker", False))
        safety_check = ttk.Checkbutton(settings_frame, text="有効", variable=self.safety_checker_var)
        safety_check.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # 生成ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.generate_button = ttk.Button(button_frame, text="画像生成開始", command=self.start_generation)
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="設定を保存", command=self.save_current_settings).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="フォルダを開く", command=self.open_output_folder).pack(side=tk.LEFT, padx=(10, 0))
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ステータスラベル
        self.status_var = tk.StringVar(value=f"準備完了 (自動保存先: {self.output_dir})")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        
        # 結果表示フレーム
        result_frame = ttk.LabelFrame(main_frame, text="生成結果", padding="5")
        result_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 画像表示用のキャンバスとスクロールバー
        canvas_frame = ttk.Frame(result_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.result_canvas = tk.Canvas(canvas_frame, height=300)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.result_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.result_canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        
        self.result_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.result_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.result_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ボタンフレーム
        button_result_frame = ttk.Frame(result_frame)
        button_result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(button_result_frame, text="結果をクリア", command=self.clear_results).pack(side=tk.LEFT)
        
        # 初期状態設定
        self.on_size_mode_change()
        self.on_model_change()
        
        # グリッドの重みを設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        api_frame.columnconfigure(1, weight=1)
        model_frame.columnconfigure(1, weight=1)
        prompt_frame.columnconfigure(0, weight=1)
    
    def get_model_display_name(self, model_endpoint):
        for display_name, endpoint in self.available_models.items():
            if endpoint == model_endpoint:
                return display_name
        return list(self.available_models.keys())[0]
    
    def get_selected_model_endpoint(self):
        selected_display_name = self.model_var.get()
        return self.available_models.get(selected_display_name, "fal-ai/flux/dev")
    
    def on_model_change(self, event=None):
        selected_endpoint = self.get_selected_model_endpoint()
        model_params = self.model_parameters.get(selected_endpoint, {})
        
        max_steps = model_params.get("max_inference_steps", 50)
        default_steps = model_params.get("default_inference_steps", 28)
        
        if hasattr(self, 'inference_steps_spin'):
            self.inference_steps_spin.configure(to=max_steps)
        
        if hasattr(self, 'max_steps_label'):
            self.max_steps_label.configure(text=f"(最大: {max_steps})")
        
        if self.inference_steps_var.get() > max_steps:
            self.inference_steps_var.set(min(default_steps, max_steps))
        
        if event is not None:
            default_guidance = model_params.get("default_guidance_scale", 3.5)
            self.guidance_scale_var.set(default_guidance)
        
        model_name = [k for k, v in self.available_models.items() if v == selected_endpoint][0]
        self.status_var.set(f"モデル選択: {model_name} (最大ステップ数: {max_steps}) - 自動保存先: {self.output_dir}")
    
    def on_size_mode_change(self):
        if self.use_custom_size_var.get():
            for widget in self.preset_frame.winfo_children():
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state="disabled")
            for widget in self.custom_frame.winfo_children():
                if isinstance(widget, ttk.Spinbox):
                    widget.configure(state="normal")
        else:
            for widget in self.preset_frame.winfo_children():
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state="readonly")
            for widget in self.custom_frame.winfo_children():
                if isinstance(widget, ttk.Spinbox):
                    widget.configure(state="disabled")
    
    def save_api_key(self):
        self.config["api_key"] = self.api_key_var.get()
        self.save_config()
    
    def save_current_settings(self):
        self.config.update({
            "api_key": self.api_key_var.get(),
            "default_model": self.get_selected_model_endpoint(),
            "default_prompt": self.prompt_text.get("1.0", tk.END).strip(),
            "default_image_size": self.image_size_var.get(),
            "default_custom_width": self.custom_width_var.get(),
            "default_custom_height": self.custom_height_var.get(),
            "default_use_custom_size": self.use_custom_size_var.get(),
            "default_inference_steps": self.inference_steps_var.get(),
            "default_guidance_scale": self.guidance_scale_var.get(),
            "default_num_images": self.num_images_var.get(),
            "enable_safety_checker": self.safety_checker_var.get()
        })
        self.save_config()
    
    def open_output_folder(self):
        """出力フォルダを開く"""
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{os.path.abspath(self.output_dir)}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", self.output_dir])
        else:  # Linux
            subprocess.Popen(["xdg-open", self.output_dir])
    
    def start_generation(self):
        if not self.api_key_var.get():
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            return
        
        self.generate_button.config(state="disabled")
        self.progress.start()
        selected_model = self.get_selected_model_endpoint()
        safety_status = "有効" if self.safety_checker_var.get() else "無効"
        self.status_var.set(f"画像生成中... (モデル: {selected_model}, 安全性フィルター: {safety_status})")
        
        thread = threading.Thread(target=self.generate_image)
        thread.daemon = True
        thread.start()
    
    def generate_image(self):
        try:
            os.environ["FAL_KEY"] = self.api_key_var.get()
            
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            selected_model = self.get_selected_model_endpoint()
            
            arguments = {
                "prompt": prompt,
                "num_inference_steps": self.inference_steps_var.get(),
                "guidance_scale": self.guidance_scale_var.get(),
                "num_images": self.num_images_var.get()
            }
            
            # 安全性チェックの設定を正しく送信
            arguments["enable_safety_checker"] = self.safety_checker_var.get()
            
            if self.use_custom_size_var.get():
                arguments["image_size"] = {
                    "width": self.custom_width_var.get(),
                    "height": self.custom_height_var.get()
                }
            else:
                arguments["image_size"] = self.image_size_var.get()
            
            seed_value = self.seed_var.get().strip()
            if seed_value:
                try:
                    arguments["seed"] = int(seed_value)
                except ValueError:
                    pass
            
            result = fal_client.subscribe(selected_model, arguments=arguments)
            
            self.root.after(0, lambda: self.display_results(result))
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(str(e)))
    
    def display_results(self, result):
        try:
            saved_files = []
            
            for i, image_data in enumerate(result['images']):
                response = requests.get(image_data['url'])
                image = Image.open(BytesIO(response.content))
                
                # 自動保存
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"img_{timestamp}_{i+1}.png"
                filepath = os.path.join(self.output_dir, filename)
                image.save(filepath)
                saved_files.append(filename)
                
                # サムネイル作成
                image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.generated_images.append({
                    'image': image,
                    'url': image_data['url'],
                    'filename': filename
                })
                
                # 画像表示フレームを作成
                img_frame = ttk.Frame(self.scrollable_frame)
                img_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky=(tk.W, tk.E))
                
                img_label = ttk.Label(img_frame, image=photo)
                img_label.image = photo
                img_label.grid(row=0, column=0, columnspan=2)
                
                size_info = f"{image.width}x{image.height}\n保存済: {filename}"
                size_label = ttk.Label(img_frame, text=size_info, foreground="gray")
                size_label.grid(row=1, column=0, columnspan=2)
                
                ttk.Button(img_frame, text="ブラウザで開く", 
                          command=lambda url=image_data['url']: webbrowser.open(url)).grid(row=2, column=0, padx=2, pady=2, columnspan=2)
            
            safety_status = "フィルター有効" if self.safety_checker_var.get() else "フィルター無効"
            status_msg = f"生成完了！ {len(result['images'])}枚自動保存 ({safety_status}): {', '.join(saved_files)}"
            self.status_var.set(status_msg)
            
        except Exception as e:
            self.handle_error(str(e))
        finally:
            self.progress.stop()
            self.generate_button.config(state="normal")
    
    def clear_results(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.generated_images = []
        self.status_var.set(f"結果をクリア (自動保存先: {self.output_dir})")
    
    def handle_error(self, error_message):
        self.progress.stop()
        self.generate_button.config(state="normal")
        self.status_var.set(f"エラー: {error_message}")

def main():
    root = tk.Tk()
    app = FluxGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()