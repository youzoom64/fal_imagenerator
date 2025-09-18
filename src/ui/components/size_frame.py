"""画像サイズ設定フレームコンポーネント"""
import tkinter as tk
from tkinter import ttk

class SizeFrame:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        
        self.use_custom_size_var = tk.BooleanVar(
            value=config_manager.get("default_use_custom_size", False)
        )
        self.image_size_var = tk.StringVar(
            value=config_manager.get("default_image_size", "landscape_4_3")
        )
        self.custom_width_var = tk.IntVar(
            value=config_manager.get("default_custom_width", 1024)
        )
        self.custom_height_var = tk.IntVar(
            value=config_manager.get("default_custom_height", 768)
        )
        
        self.frame = self.create_frame()
        self.on_size_mode_change()
    
    def create_frame(self):
        """画像サイズ設定フレームを作成"""
        size_frame = ttk.LabelFrame(self.parent, text="画像サイズ設定", padding="5")
        
        # モード選択ラジオボタン
        preset_radio = ttk.Radiobutton(size_frame, text="プリセットを使用", 
                                      variable=self.use_custom_size_var, 
                                      value=False, command=self.on_size_mode_change)
        preset_radio.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        custom_radio = ttk.Radiobutton(size_frame, text="カスタムサイズ (px)", 
                                      variable=self.use_custom_size_var, 
                                      value=True, command=self.on_size_mode_change)
        custom_radio.grid(row=0, column=1, sticky=tk.W, padx=(20, 0), pady=2)
        
        # プリセットサイズフレーム
        self.preset_frame = ttk.Frame(size_frame)
        self.preset_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.preset_frame, text="プリセット:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.image_size_combo = ttk.Combobox(self.preset_frame, textvariable=self.image_size_var, 
                                            values=["square_hd", "landscape_4_3", "landscape_16_9", 
                                                   "portrait_4_3", "portrait_16_9"])
        self.image_size_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # カスタムサイズフレーム
        self.custom_frame = ttk.Frame(size_frame)
        self.custom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.custom_frame, text="幅:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.width_spin = ttk.Spinbox(self.custom_frame, from_=64, to=2048, increment=64, 
                                     textvariable=self.custom_width_var, width=10)
        self.width_spin.grid(row=0, column=1, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(self.custom_frame, text="px    高さ:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.height_spin = ttk.Spinbox(self.custom_frame, from_=64, to=2048, increment=64, 
                                      textvariable=self.custom_height_var, width=10)
        self.height_spin.grid(row=0, column=3, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(self.custom_frame, text="px").grid(row=0, column=4, sticky=tk.W)
        
        return size_frame
    
    def on_size_mode_change(self):
        """サイズモード変更時の処理"""
        if self.use_custom_size_var.get():
            self.image_size_combo.configure(state="disabled")
            self.width_spin.configure(state="normal")
            self.height_spin.configure(state="normal")
        else:
            self.image_size_combo.configure(state="readonly")
            self.width_spin.configure(state="disabled")
            self.height_spin.configure(state="disabled")
    
    def get_image_size_params(self):
        """画像サイズパラメータを取得"""
        if self.use_custom_size_var.get():
            return {
                "width": self.custom_width_var.get(),
                "height": self.custom_height_var.get()
            }
        else:
            return self.image_size_var.get()