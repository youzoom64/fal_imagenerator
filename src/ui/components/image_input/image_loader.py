"""画像読み込み処理クラス"""
import os
import tempfile
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sys

# デバッグロガーをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
try:
    from debug_logger import debug_logger
except ImportError:
    import logging
    debug_logger = logging.getLogger(__name__)

try:
    from ....utils.file_utils import create_thumbnail
except ImportError:
    def create_thumbnail(image, size):
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail

class ImageLoader:
    def __init__(self, image_input_frame):
        self.frame_obj = image_input_frame
    
    def browse_image(self):
        """画像ファイルを参照して選択"""
        debug_logger.info("ファイル選択開始")
        
        file_types = [
            ("画像ファイル", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff *.tif"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("すべてのファイル", "*.*")
        ]
        
        try:
            file_path = filedialog.askopenfilename(
                title="画像ファイルを選択",
                filetypes=file_types,
                initialdir=os.path.expanduser("~/Pictures")
            )
            
            if file_path:
                self.load_image_file(file_path)
                
        except Exception as e:
            debug_logger.error(f"ファイル選択エラー: {e}")
    
    def load_image_file(self, file_path):
        """画像ファイルを読み込み表示"""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("エラー", "ファイルが存在しません")
                return
            
            debug_logger.info(f"画像読み込み: {file_path}")
            
            # 画像を開く
            image = Image.open(file_path)
            self.frame_obj.set_image(image, file_path)
            
            # サムネイル作成（表示用）
            thumbnail = create_thumbnail(image, (280, 180))
            self.frame_obj.photo = ImageTk.PhotoImage(thumbnail)
            
            # ファイル情報作成
            file_size = os.path.getsize(file_path) / 1024
            file_name = os.path.basename(file_path)
            info_text = f"📁 {file_name} ({image.width}x{image.height}, {file_size:.1f}KB)"
            
            # UI更新
            self.frame_obj.ui_builder.display_image(self.frame_obj.photo, info_text)
            
        except Exception as e:
            debug_logger.error(f"画像読み込みエラー: {e}")
            messagebox.showerror("エラー", f"画像の読み込みに失敗しました:\n{str(e)}")
    
    def paste_from_clipboard(self):
        """クリップボードから画像を貼り付け"""
        try:
            from PIL import ImageGrab
            clipboard_image = ImageGrab.grabclipboard()
            
            if clipboard_image is None:
                messagebox.showinfo("情報", "クリップボードに画像がありません")
                return
            
            self.load_image_from_pil(clipboard_image, "クリップボード画像")
            
        except ImportError:
            messagebox.showerror("エラー", "PIL (Pillow) ライブラリが必要です")
        except Exception as e:
            messagebox.showerror("エラー", f"クリップボードから画像を取得できませんでした:\n{str(e)}")
    
    def load_image_from_pil(self, pil_image, display_name="画像"):
        """PILイメージから直接読み込み"""
        try:
            self.frame_obj.set_image(pil_image, None)
            
            # サムネイル作成
            thumbnail = create_thumbnail(pil_image, (280, 180))
            self.frame_obj.photo = ImageTk.PhotoImage(thumbnail)
            
            # ファイル情報作成
            info_text = f"📋 {display_name} ({pil_image.width}x{pil_image.height})"
            
            # UI更新
            self.frame_obj.ui_builder.display_image(self.frame_obj.photo, info_text)
            
        except Exception as e:
            messagebox.showerror("エラー", f"画像の読み込みに失敗しました:\n{str(e)}")
    
    def save_temp_image(self):
        """一時ファイルとして画像を保存（クリップボード画像用）"""
        if self.frame_obj.current_image and not self.frame_obj.current_image_path:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"temp_image_{id(self.frame_obj)}.png")
            self.frame_obj.current_image.save(temp_path)
            return temp_path
        
        return self.frame_obj.current_image_path