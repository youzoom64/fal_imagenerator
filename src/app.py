"""メインアプリケーションクラス（D&D対応版）"""
import tkinter as tk
import os
from .core.config_manager import ConfigManager
from .core.model_manager import ModelManager
from .core.image_generator import ImageGenerator
from .ui.main_window import MainWindow

# D&D対応のインポート
try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    TkinterDnD = None
    DND_AVAILABLE = False

class FluxGUIApp:
    def __init__(self):
        # 自動保存ディレクトリを作成
        self.output_dir = "generated_images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # コアコンポーネントを初期化
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager()
        self.image_generator = ImageGenerator(self.output_dir)
        
        # D&D対応のメインウィンドウを作成
        if DND_AVAILABLE:
            print("D&D機能が利用可能です")
            self.root = TkinterDnD.Tk()  # 重要: TkinterDnD.Tk()を使用
        else:
            print("D&D機能が利用できません（通常モード）")
            self.root = tk.Tk()
        
        self.main_window = MainWindow(
            root=self.root,
            config_manager=self.config_manager,
            model_manager=self.model_manager,
            image_generator=self.image_generator
        )
    
    def run(self):
        """アプリケーションを実行"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            print(f"アプリケーションエラー: {e}")
            self.shutdown()
    
    def shutdown(self):
        """アプリケーションを終了"""
        if self.root:
            self.root.quit()
            self.root.destroy()