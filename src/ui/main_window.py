"""メインウィンドウクラス（基本構造）"""
import tkinter as tk
from tkinter import ttk
from .components.api_frame import APIFrame
from .components.mode_selection_frame import ModeSelectionFrame
from .components.model_frame import ModelFrame
from .components.prompt_frame import PromptFrame
from .components.image_input import ImageInputFrame
from .components.size_frame import SizeFrame
from .components.settings_frame import SettingsFrame
from .components.result_frame import ResultFrame
from .handlers.generation_handler import GenerationHandler
from .handlers.ui_handler import UIHandler

class MainWindow:
    def __init__(self, root, config_manager, model_manager, image_generator):
        self.root = root
        self.config_manager = config_manager
        self.model_manager = model_manager
        self.image_generator = image_generator
        self.current_mode = config_manager.get("last_mode", "text-to-image")
        
        # ハンドラーを初期化
        self.generation_handler = GenerationHandler(self)
        self.ui_handler = UIHandler(self)
        
        self.setup_window()
        self.create_ui_components()
        self.setup_layout()
        self.setup_bindings()
        self.restore_settings()
        
        # ウィンドウ閉じるイベント
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 初期状態設定
        self.update_status(f"準備完了 (自動保存先: {image_generator.get_output_dir()})")
    
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("FAL.ai Image Generator - 設定記憶機能付き")
        
        # 保存された位置・サイズを復元
        self.config_manager.restore_window_geometry(self.root)
        self.root.resizable(True, True)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def on_closing(self):
        """ウィンドウを閉じる時の処理"""
        # 現在の設定を保存
        self.ui_handler.save_current_settings()
        
        # ウィンドウ位置・サイズを保存
        self.config_manager.save_window_geometry(self.root)
        
        # 現在のモードを保存
        self.config_manager.set("last_mode", self.current_mode)
        
        # アプリケーション終了
        self.root.quit()
        self.root.destroy()
    
    def create_ui_components(self):
        """UIコンポーネントを作成"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 各コンポーネントを作成
        self.api_frame = APIFrame(self.main_frame, self.config_manager)
        self.mode_frame = ModeSelectionFrame(self.main_frame, self.ui_handler.on_mode_change)
        self.model_frame = ModelFrame(self.main_frame, self.config_manager, 
                                    self.model_manager, self.ui_handler.on_model_change)
        self.prompt_frame = PromptFrame(self.main_frame, self.config_manager)
        self.image_input_frame = ImageInputFrame(self.main_frame, self.config_manager)
        self.size_frame = SizeFrame(self.main_frame, self.config_manager)
        self.settings_frame = SettingsFrame(self.main_frame, self.config_manager, self.model_manager)
        self.result_frame = ResultFrame(self.main_frame, self.image_generator.get_output_dir())
        
        # プリセット管理ウィンドウを追加
        from .components.preset_manager_window import PresetManagerWindow
        self.preset_manager = PresetManagerWindow(self.root, self)
        
        # 生成ボタンフレーム
        self.button_frame = ttk.Frame(self.main_frame)
        
        self.generate_button = ttk.Button(self.button_frame, text="画像生成開始", 
                                        command=self.generation_handler.start_generation)
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(self.button_frame, text="💾 設定を保存", 
                command=self.ui_handler.save_current_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.button_frame, text="⚙️ プリセット管理", 
                command=self.preset_manager.show_window).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.button_frame, text="📁 フォルダを開く", 
                command=self.ui_handler.open_output_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        # プログレスバー
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        
        # ステータスラベル
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)

    def restore_settings(self):
        """保存された設定を復元（エラーハンドリング強化）"""
        try:
            # モードを復元
            last_mode = self.config_manager.safe_get("last_mode", "text-to-image")
            if last_mode in ["text-to-image", "image-to-image"]:
                self.mode_frame.set_mode(last_mode)
        except Exception as e:
            print(f"設定復元エラー: {e}")
            # デフォルトモードに設定
            self.mode_frame.set_mode("text-to-image")



    def setup_layout(self):
        """レイアウトを設定"""
        self.ui_handler.setup_layout()
    
    def setup_bindings(self):
        """イベントバインディングを設定"""
        self.ui_handler.setup_bindings()
    
    def update_status(self, message):
        """ステータスメッセージを更新"""
        self.status_var.set(message)