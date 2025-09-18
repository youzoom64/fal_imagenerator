"""画像入力フレームのUI構築クラス"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# デバッグロガーをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
try:
    from debug_logger import debug_logger
except ImportError:
    import logging
    debug_logger = logging.getLogger(__name__)

class ImageInputUIBuilder:
    def __init__(self, image_input_frame):
        self.frame_obj = image_input_frame
        self.image_display_frame = None
        self.drop_label = None
        self.image_label = None
        self.file_info_var = None
        self.dnd_status_var = None
    
    def create_frame(self):
        """画像入力フレームを作成"""
        debug_logger.info("UI作成開始")
        
        image_frame = ttk.LabelFrame(self.frame_obj.parent, text="入力画像", padding="5")
        
        # 画像表示エリアを作成
        self._create_image_display_area(image_frame)
        
        # ボタン類を作成
        self._create_buttons(image_frame)
        
        # 情報表示ラベルを作成
        self._create_info_labels(image_frame)
        
        # 基本的なインタラクションを設定
        self._setup_basic_interactions()
        
        # D&D機能の設定（遅延実行）
        self.frame_obj.parent.after(100, self.frame_obj.drag_drop_handler.setup_drag_and_drop)
        
        debug_logger.info("UI作成完了")
        return image_frame
    
    def _create_image_display_area(self, parent):
        """画像表示エリアを作成"""
        self.image_display_frame = tk.Frame(parent, bg="lightgray", relief="sunken", bd=2, 
                                           width=300, height=200)
        self.image_display_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.image_display_frame.grid_propagate(False)
        
        # 初期メッセージ
        self.drop_label = tk.Label(self.image_display_frame, 
                                  text="D&D機能チェック中...\n画像をドラッグ&ドロップ\nまたは下のボタンで選択",
                                  bg="lightgray", fg="gray", font=("Arial", 10), justify="center")
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 画像表示用Label（初期は非表示）
        self.image_label = tk.Label(self.image_display_frame, bg="lightgray")
    
    def _create_buttons(self, parent):
        """ボタン類を作成"""
        button_frame = tk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="📁 画像を選択", 
                  command=self.frame_obj.image_loader.browse_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🗑️ クリア", 
                  command=self.clear_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📋 クリップボードから", 
                  command=self.frame_obj.image_loader.paste_from_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔧 D&Dテスト", 
                  command=self.frame_obj.drag_drop_handler.test_dnd).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔄 D&D再試行", 
                  command=self.frame_obj.drag_drop_handler.retry_dnd_setup).pack(side=tk.LEFT, padx=2)
    
    def _create_info_labels(self, parent):
        """情報表示ラベルを作成"""
        # ファイル情報表示
        self.file_info_var = tk.StringVar(value="画像が選択されていません")
        info_label = ttk.Label(parent, textvariable=self.file_info_var, foreground="gray")
        info_label.grid(row=2, column=0, columnspan=2, pady=2, sticky=tk.W)
        
        # D&D状態表示
        self.dnd_status_var = tk.StringVar(value="D&D状態: 初期化中...")
        dnd_status_label = ttk.Label(parent, textvariable=self.dnd_status_var, foreground="blue")
        dnd_status_label.grid(row=3, column=0, columnspan=2, pady=2, sticky=tk.W)
    
    def _setup_basic_interactions(self):
        """基本的なインタラクション（クリック、ホバー）を設定"""
        # 基本的なクリックイベント
        self.image_display_frame.bind("<Button-1>", self._on_click)
        
        # マウスホバー効果
        self.image_display_frame.bind("<Enter>", self._on_enter)
        self.image_display_frame.bind("<Leave>", self._on_leave)
        self.drop_label.bind("<Enter>", self._on_enter)
        self.drop_label.bind("<Leave>", self._on_leave)
    
    def _on_click(self, event):
        """クリック時の処理"""
        self.frame_obj.image_loader.browse_image()
    
    def _on_enter(self, event):
        """マウスエンター時の処理"""
        if not self.frame_obj.drag_drop_handler.dnd_enabled:
            self.image_display_frame.config(bg="lightblue")
            self.drop_label.config(bg="lightblue")
    
    def _on_leave(self, event):
        """マウスリーブ時の処理"""
        if not self.frame_obj.drag_drop_handler.dnd_enabled:
            self.image_display_frame.config(bg="lightgray")
            self.drop_label.config(bg="lightgray")
    
    def display_image(self, photo, info_text):
        """画像を表示"""
        self.drop_label.place_forget()
        self.image_label.config(image=photo)
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        self.file_info_var.set(info_text)
    
    def clear_image(self):
        """画像表示をクリア"""
        self.frame_obj.clear_image_data()
        self.image_label.place_forget()
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
        self.file_info_var.set("画像が選択されていません")
        if hasattr(self.frame_obj, 'photo'):
            del self.frame_obj.photo
    
    def update_dnd_status(self, status):
        """D&D状態を更新"""
        self.dnd_status_var.set(status)
    
    def update_drop_label(self, text):
        """ドロップラベルテキストを更新"""
        self.drop_label.config(text=text)