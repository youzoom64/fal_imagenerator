"""生成設定フレームコンポーネント（strength追加）"""
import tkinter as tk
from tkinter import ttk

class SettingsFrame:
    def __init__(self, parent, config_manager, model_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.model_manager = model_manager
        self.current_mode = "text-to-image"  # デフォルトモード
        
        # 既存の変数
        self.inference_steps_var = tk.IntVar(value=config_manager.get("default_inference_steps", 28))
        self.guidance_scale_var = tk.DoubleVar(value=config_manager.get("default_guidance_scale", 3.5))
        self.num_images_var = tk.IntVar(value=config_manager.get("default_num_images", 1))
        self.seed_var = tk.StringVar()
        self.safety_checker_var = tk.BooleanVar(value=config_manager.get("enable_safety_checker", True))
        
        # image-to-image用の新しい変数
        self.strength_var = tk.DoubleVar(value=config_manager.get("default_strength", 0.95))
        
        self.frame = self.create_frame()
    
    def create_frame(self):
        """生成設定フレームを作成"""
        settings_frame = ttk.LabelFrame(self.parent, text="生成設定", padding="5")
        
        # 推論ステップ数
        ttk.Label(settings_frame, text="推論ステップ数:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        initial_model = self.config_manager.get("default_model", "fal-ai/flux/dev")
        max_steps = self.model_manager.get_model_parameters(initial_model).get("max_inference_steps", 50)
        
        self.inference_steps_spin = ttk.Spinbox(settings_frame, from_=1, to=max_steps, 
                                               textvariable=self.inference_steps_var, width=10)
        self.inference_steps_spin.grid(row=0, column=1, sticky=tk.W, padx=(5, 10))
        
        self.max_steps_label = ttk.Label(settings_frame, text=f"(最大: {max_steps})", foreground="gray")
        self.max_steps_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # ガイダンススケール
        ttk.Label(settings_frame, text="ガイダンススケール:").grid(row=0, column=3, sticky=tk.W, pady=2)
        guidance_scale_spin = ttk.Spinbox(settings_frame, from_=1.0, to=20.0, increment=0.5, 
                                         textvariable=self.guidance_scale_var, width=10)
        guidance_scale_spin.grid(row=0, column=4, sticky=tk.W, padx=(5, 0))
        
        # Strength（image-to-image用）- 初期は非表示
        self.strength_label = ttk.Label(settings_frame, text="Strength:")
        self.strength_spin = ttk.Spinbox(settings_frame, from_=0.1, to=1.0, increment=0.05, 
                                        textvariable=self.strength_var, width=10)
        self.strength_info_label = ttk.Label(settings_frame, text="(元画像の影響度)", foreground="gray")
        
        # 画像枚数
        ttk.Label(settings_frame, text="画像枚数:").grid(row=1, column=0, sticky=tk.W, pady=2)
        num_images_spin = ttk.Spinbox(settings_frame, from_=1, to=4, 
                                     textvariable=self.num_images_var, width=10)
        num_images_spin.grid(row=1, column=1, sticky=tk.W, padx=(5, 20))
        
        # シード値
        ttk.Label(settings_frame, text="シード値:").grid(row=1, column=2, sticky=tk.W, pady=2)
        seed_entry = ttk.Entry(settings_frame, textvariable=self.seed_var, width=15)
        seed_entry.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), columnspan=2)
        
        # 安全性フィルター設定
        ttk.Label(settings_frame, text="安全性フィルター:").grid(row=2, column=0, sticky=tk.W, pady=2)
        safety_check = ttk.Checkbutton(settings_frame, text="有効", 
                                      variable=self.safety_checker_var)
        safety_check.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        return settings_frame
    
    def set_mode(self, mode):
        """モードに応じてUI要素の表示/非表示を切り替え"""
        self.current_mode = mode
        
        if mode == "image-to-image":
            # Strengthを表示
            self.strength_label.grid(row=1, column=5, sticky=tk.W, pady=2, padx=(20, 5))
            self.strength_spin.grid(row=1, column=6, sticky=tk.W, padx=(5, 5))
            self.strength_info_label.grid(row=1, column=7, sticky=tk.W, padx=(0, 5))
        else:
            # Strengthを非表示
            self.strength_label.grid_remove()
            self.strength_spin.grid_remove()
            self.strength_info_label.grid_remove()
    
    def update_model_constraints(self, model_endpoint):
        """モデル変更時の制約更新"""
        model_params = self.model_manager.get_model_parameters(model_endpoint)
        max_steps = model_params.get("max_inference_steps", 50)
        default_steps = model_params.get("default_inference_steps", 28)
        default_guidance = model_params.get("default_guidance_scale", 3.5)
        default_strength = model_params.get("default_strength", 0.95)
        
        # 推論ステップ数の制限を更新
        self.inference_steps_spin.configure(to=max_steps)
        self.max_steps_label.configure(text=f"(最大: {max_steps})")
        
        # 現在の値が制限を超えている場合は調整
        if self.inference_steps_var.get() > max_steps:
            self.inference_steps_var.set(min(default_steps, max_steps))
        
        # デフォルト値を更新
        self.guidance_scale_var.set(default_guidance)
        if self.current_mode == "image-to-image":
            self.strength_var.set(default_strength)
    
    def get_generation_settings(self):
        """生成設定を取得"""
        settings = {
            "num_inference_steps": self.inference_steps_var.get(),
            "guidance_scale": self.guidance_scale_var.get(),
            "num_images": self.num_images_var.get(),
            "seed": self.seed_var.get().strip() if self.seed_var.get().strip() else None,
            "enable_safety_checker": self.safety_checker_var.get()
        }
        
        # image-to-imageの場合はstrengthを追加
        if self.current_mode == "image-to-image":
            settings["strength"] = self.strength_var.get()
        
        return settings