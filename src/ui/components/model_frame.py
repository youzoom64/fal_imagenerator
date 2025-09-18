"""モデル選択フレームコンポーネント（モード対応版）"""
import tkinter as tk
from tkinter import ttk

class ModelFrame:
    def __init__(self, parent, config_manager, model_manager, on_model_change_callback=None):
        self.parent = parent
        self.config_manager = config_manager
        self.model_manager = model_manager
        self.on_model_change_callback = on_model_change_callback
        self.current_mode = "text-to-image"  # デフォルトモード
        
        self.model_var = tk.StringVar()
        default_model_key = model_manager.get_model_display_name(
            config_manager.get("default_model", "fal-ai/flux/dev")
        )
        self.model_var.set(default_model_key)
        
        self.frame = self.create_frame()
    
    def create_frame(self):
        """モデル選択フレームを作成"""
        model_frame = ttk.LabelFrame(self.parent, text="モデル選択", padding="5")
        
        ttk.Label(model_frame, text="モデル:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                       values=self.model_manager.get_model_names("text-to-image"), 
                                       state="readonly", width=50)
        self.model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)
        
        # グリッド設定
        model_frame.columnconfigure(1, weight=1)
        
        return model_frame
    
    def set_mode(self, mode):
        """モードに応じてモデルリストを更新"""
        self.current_mode = mode
        
        # 現在のモデルに対応するモデルリストを取得
        model_names = self.model_manager.get_model_names(mode)
        self.model_combo.configure(values=model_names)
        
        # 最初のモデルを選択（デフォルト）
        if model_names:
            self.model_var.set(model_names[0])
            self.on_model_change()
    
    def on_model_change(self, event=None):
        """モデル変更時の処理"""
        if self.on_model_change_callback:
            selected_endpoint = self.get_selected_model_endpoint()
            self.on_model_change_callback(selected_endpoint, event)
    
    def get_selected_model_endpoint(self):
        """選択されたモデルのエンドポイントを取得"""
        selected_display_name = self.model_var.get()
        models = self.model_manager.get_models_by_type(self.current_mode)
        return models.get(selected_display_name, list(models.values())[0])
    
    def get_selected_model_display_name(self):
        """選択されたモデルの表示名を取得"""
        return self.model_var.get()