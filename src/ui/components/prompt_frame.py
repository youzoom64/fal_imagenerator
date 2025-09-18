"""プロンプト入力フレームコンポーネント（履歴機能付き）"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from .prompt_history_window import PromptHistoryWindow

class PromptFrame:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.prompt_history = PromptHistoryWindow(parent, self)
        self.frame = self.create_frame()
    
    def create_frame(self):
        """プロンプト入力フレームを作成"""
        prompt_frame = ttk.LabelFrame(self.parent, text="プロンプト", padding="5")
        
        # ポジティブプロンプト
        prompt_header_frame = ttk.Frame(prompt_frame)
        prompt_header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(prompt_header_frame, text="プロンプト:").pack(side=tk.LEFT)
        ttk.Button(prompt_header_frame, text="📚 履歴", 
                  command=self.prompt_history.show_window).pack(side=tk.RIGHT)
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=6, width=80)
        self.prompt_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 0))
        self.prompt_text.insert(tk.END, self.config_manager.get("default_prompt", ""))
        
        # ネガティブプロンプト
        ttk.Label(prompt_frame, text="ネガティブプロンプト:").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        self.negative_prompt_text = scrolledtext.ScrolledText(prompt_frame, height=4, width=80)
        self.negative_prompt_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 0))
        self.negative_prompt_text.insert(tk.END, self.config_manager.get("default_negative_prompt", ""))
        
        # グリッド設定
        prompt_frame.columnconfigure(0, weight=1)
        prompt_header_frame.columnconfigure(0, weight=1)
        
        return prompt_frame
    
    def get_prompt(self):
        """入力されたプロンプトを取得"""
        return self.prompt_text.get("1.0", tk.END).strip()
    
    def get_negative_prompt(self):
        """入力されたネガティブプロンプトを取得"""
        return self.negative_prompt_text.get("1.0", tk.END).strip()
    
    def set_prompt(self, prompt):
        """プロンプトを設定"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert(tk.END, prompt)
    
    def set_negative_prompt(self, negative_prompt):
        """ネガティブプロンプトを設定"""
        self.negative_prompt_text.delete("1.0", tk.END)
        self.negative_prompt_text.insert(tk.END, negative_prompt)
    
    def save_to_history(self):
        """現在のプロンプトを履歴に保存"""
        prompt = self.get_prompt()
        negative_prompt = self.get_negative_prompt()
        self.prompt_history.add_to_history(prompt, negative_prompt)