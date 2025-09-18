"""画像入力フレームメインクラス"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from PIL import Image, ImageTk
from ....utils.file_utils import create_thumbnail

# デバッグロガーをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
from debug_logger import debug_logger

from .drag_drop_handler import DragDropHandler
from .image_loader import ImageLoader
from .ui_builder import ImageInputUIBuilder

class ImageInputFrame:
    def __init__(self, parent, config_manager):
        debug_logger.log_function_entry("ImageInputFrame.__init__")
        
        self.parent = parent
        self.config_manager = config_manager
        self.current_image_path = None
        self.current_image = None
        
        # ハンドラー・ビルダーを初期化
        self.ui_builder = ImageInputUIBuilder(self)
        self.image_loader = ImageLoader(self)
        self.drag_drop_handler = DragDropHandler(self)
        
        debug_logger.info("ImageInputFrame初期化開始")
        self.frame = self.ui_builder.create_frame()
        debug_logger.info("ImageInputFrame初期化完了")
        
        debug_logger.log_function_exit("ImageInputFrame.__init__")
    
    def get_image_path(self):
        """現在選択されている画像パスを取得"""
        return self.current_image_path
    
    def get_image(self):
        """現在選択されている画像オブジェクトを取得"""
        return self.current_image
    
    def has_image(self):
        """画像が選択されているかチェック"""
        return self.current_image is not None
    
    def save_temp_image(self):
        """一時ファイルとして画像を保存（クリップボード画像用）"""
        return self.image_loader.save_temp_image()
    
    def set_image(self, image, path=None):
        """画像を設定"""
        self.current_image = image
        self.current_image_path = path
    
    def clear_image_data(self):
        """画像データをクリア"""
        self.current_image = None
        self.current_image_path = None