"""ドラッグ&ドロップ処理クラス（正しい実装）"""
import tkinter as tk
from tkinter import messagebox
import os
import sys

# デバッグロガーをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
try:
    from debug_logger import debug_logger
except ImportError:
    import logging
    debug_logger = logging.getLogger(__name__)

class DragDropHandler:
    def __init__(self, image_input_frame):
        self.frame_obj = image_input_frame
        self.dnd_enabled = False
        debug_logger.info("DragDropHandler初期化（正しい実装）")
    
    def get_root_window(self):
        root = self.frame_obj.parent
        while root.master:
            root = root.master
        return root
    
    def retry_dnd_setup(self):
        debug_logger.info("D&D設定再試行")
        self.setup_drag_and_drop()
    
    def setup_drag_and_drop(self):
        """正しいD&D機能設定"""
        debug_logger.info("D&D機能設定開始（正しい方法）")
        
        try:
            # tkinterdnd2のインポートと確認
            from tkinterdnd2 import DND_FILES, TkinterDnD
            debug_logger.info("tkinterdnd2インポート成功")
            
            # ルートウィンドウがTkinterDnD.Tk()かどうか確認
            root = self.get_root_window()
            root_type = type(root).__name__
            debug_logger.info(f"ルートウィンドウタイプ: {root_type}")
            
            if "TkinterDnD" not in str(type(root)):
                debug_logger.warning("ルートウィンドウがTkinterDnD.Tk()ではありません")
                self.setup_basic_mode("TkinterDnD.Tk()が必要")
                return
            
            # D&Dイベントハンドラー
            def on_drop(event):
                debug_logger.info(f"ファイルドロップ: {event.data}")
                try:
                    # ファイルパスの処理
                    file_path = event.data
                    if file_path.startswith('{') and file_path.endswith('}'):
                        file_path = file_path[1:-1]  # 波括弧を除去
                    
                    debug_logger.info(f"処理ファイル: {file_path}")
                    
                    # 画像ファイル判定
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']
                    if any(file_path.lower().endswith(ext) for ext in valid_extensions):
                        self.frame_obj.image_loader.load_image_file(file_path)
                        debug_logger.info("D&D画像読み込み成功")
                    else:
                        debug_logger.warning(f"サポート外形式: {file_path}")
                        messagebox.showwarning("警告", "サポートされていないファイル形式です")
                        
                except Exception as drop_error:
                    debug_logger.exception(f"ドロップ処理エラー: {drop_error}")
                
                return event.action
            
            def on_drop_enter(event):
                self.frame_obj.ui_builder.image_display_frame.config(bg="lightgreen")
                self.frame_obj.ui_builder.drop_label.config(bg="lightgreen", text="画像をここにドロップ！")
                return event.action
            
            def on_drop_leave(event):
                self.frame_obj.ui_builder.image_display_frame.config(bg="lightgray")
                self.frame_obj.ui_builder.drop_label.config(bg="lightgray")
                self.frame_obj.ui_builder.update_drop_label("画像をドラッグ&ドロップ\nまたは下のボタンで選択")
                return event.action
            
            # D&D登録
            display_frame = self.frame_obj.ui_builder.image_display_frame
            display_frame.drop_target_register(DND_FILES)
            display_frame.dnd_bind('<<Drop>>', on_drop)
            display_frame.dnd_bind('<<DropEnter>>', on_drop_enter)
            display_frame.dnd_bind('<<DropLeave>>', on_drop_leave)
            
            self.dnd_enabled = True
            self.frame_obj.ui_builder.update_dnd_status("D&D状態: ✅ 有効（TkinterDnD.Tk使用）")
            self.frame_obj.ui_builder.update_drop_label("画像をドラッグ&ドロップ\nまたは下のボタンで選択")
            debug_logger.info("D&D機能設定完了")
            
        except ImportError as e:
            debug_logger.error(f"tkinterdnd2インポートエラー: {e}")
            self.setup_basic_mode("tkinterdnd2未インストール")
        except Exception as e:
            debug_logger.exception(f"D&D設定エラー: {e}")
            self.setup_basic_mode(f"設定エラー: {str(e)[:50]}")
    
    def setup_basic_mode(self, reason=""):
        """基本モード設定"""
        self.dnd_enabled = False
        status = f"D&D状態: 無効（{reason}）" if reason else "D&D状態: 無効"
        self.frame_obj.ui_builder.update_dnd_status(status)
        self.frame_obj.ui_builder.update_drop_label("クリックして画像を選択\n📁 ファイル選択ボタンを使用")
        
        # 右クリックメニュー
        def show_menu(event):
            try:
                menu = tk.Menu(self.get_root_window(), tearoff=0)
                menu.add_command(label="📁 ファイルを選択", command=self.frame_obj.image_loader.browse_image)
                menu.add_command(label="📋 クリップボードから", command=self.frame_obj.image_loader.paste_from_clipboard)
                menu.tk_popup(event.x_root, event.y_root)
            except:
                pass
            finally:
                try:
                    menu.grab_release()
                except:
                    pass
        
        self.frame_obj.ui_builder.image_display_frame.bind("<Button-3>", show_menu)
    
    def test_dnd(self):
        """D&D機能テスト"""
        try:
            from tkinterdnd2 import TkinterDnD
            root_type = str(type(self.get_root_window()))
            
            if "TkinterDnD" in root_type:
                messagebox.showinfo("D&Dテスト", f"✅ D&D対応ウィンドウ検出\nタイプ: {root_type}\n\nD&D機能が使用可能です")
            else:
                messagebox.showwarning("D&Dテスト", f"⚠️ 標準tkinterウィンドウ\nタイプ: {root_type}\n\nD&D機能を使用するには\nTkinterDnD.Tk()が必要です")
        except ImportError:
            messagebox.showerror("D&Dテスト", "tkinterdnd2がインストールされていません")