"""モード選択フレームコンポーネント（設定記憶対応）"""
import tkinter as tk
from tkinter import ttk

class ModeSelectionFrame:
    def __init__(self, parent, on_mode_change_callback=None):
        self.parent = parent
        self.on_mode_change_callback = on_mode_change_callback
        self.mode_var = tk.StringVar(value="text-to-image")
        self.frame = self.create_frame()
    
    def create_frame(self):
        """モード選択フレームを作成"""
        mode_frame = ttk.LabelFrame(self.parent, text="生成モード", padding="5")
        
        # ラジオボタンで選択
        text_to_image_radio = ttk.Radiobutton(
            mode_frame, 
            text="Text-to-Image (文章から画像生成)", 
            variable=self.mode_var, 
            value="text-to-image",
            command=self.on_mode_change
        )
        text_to_image_radio.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        image_to_image_radio = ttk.Radiobutton(
            mode_frame, 
            text="Image-to-Image (画像から画像変換)", 
            variable=self.mode_var, 
            value="image-to-image",
            command=self.on_mode_change
        )
        image_to_image_radio.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        return mode_frame
    
    def on_mode_change(self):
        """モード変更時の処理"""
        if self.on_mode_change_callback:
            self.on_mode_change_callback(self.mode_var.get())
    
    def get_current_mode(self):
        """現在のモードを取得"""
        return self.mode_var.get()
    
    def set_mode(self, mode):
        """モードを設定（プログラムから）"""
        if mode in ["text-to-image", "image-to-image"]:
            self.mode_var.set(mode)
            self.on_mode_change()