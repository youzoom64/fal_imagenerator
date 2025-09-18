"""APIキー設定フレームコンポーネント"""
import tkinter as tk
from tkinter import ttk

class APIFrame:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.api_key_var = tk.StringVar(value=config_manager.get("api_key", ""))
        self.frame = self.create_frame()
    
    def create_frame(self):
        """APIキー設定フレームを作成"""
        api_frame = ttk.LabelFrame(self.parent, text="API設定", padding="5")
        
        ttk.Label(api_frame, text="APIキー:").grid(row=0, column=0, sticky=tk.W)
        
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=60, show="*")
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(api_frame, text="保存", command=self.save_api_key).grid(row=0, column=2, padx=(5, 0))
        
        # グリッド設定
        api_frame.columnconfigure(1, weight=1)
        
        return api_frame
    
    def save_api_key(self):
        """APIキーを保存"""
        self.config_manager.set("api_key", self.api_key_var.get())
        self.config_manager.save_config()
    
    def get_api_key(self):
        """現在のAPIキーを取得"""
        return self.api_key_var.get()