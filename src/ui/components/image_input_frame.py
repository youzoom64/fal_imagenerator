"""画像入力フレームコンポーネント（image-to-image用）- デバッグ対応版"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from PIL import Image, ImageTk
from ...utils.file_utils import create_thumbnail

# デバッグロガーをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from debug_logger import debug_logger

class ImageInputFrame:
    def __init__(self, parent, config_manager):
        debug_logger.log_function_entry("ImageInputFrame.__init__")
        
        self.parent = parent
        self.config_manager = config_manager
        self.current_image_path = None
        self.current_image = None
        self.dnd_enabled = False
        self.root_window = None
        
        debug_logger.info("ImageInputFrame初期化開始")
        self.frame = self.create_frame()
        debug_logger.info("ImageInputFrame初期化完了")
        
        debug_logger.log_function_exit("ImageInputFrame.__init__")
    
    def create_frame(self):
        """画像入力フレームを作成"""
        debug_logger.log_function_entry("create_frame")
        
        image_frame = ttk.LabelFrame(self.parent, text="入力画像", padding="5")
        
        # 画像表示・ドロップエリア
        self.image_display_frame = tk.Frame(image_frame, bg="lightgray", relief="sunken", bd=2, 
                                           width=300, height=200)
        self.image_display_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.image_display_frame.grid_propagate(False)
        
        debug_logger.debug("画像表示フレーム作成完了")
        
        # 初期メッセージ
        self.drop_label = tk.Label(self.image_display_frame, 
                                  text="D&D機能チェック中...\n画像をドラッグ&ドロップ\nまたは下のボタンで選択",
                                  bg="lightgray", fg="gray", font=("Arial", 10), justify="center")
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 画像表示用Label（初期は非表示）
        self.image_label = tk.Label(self.image_display_frame, bg="lightgray")
        
        # ボタン類
        button_frame = tk.Frame(image_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="📁 画像を選択", command=self.browse_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🗑️ クリア", command=self.clear_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📋 クリップボードから", command=self.paste_from_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔧 D&Dテスト", command=self.test_dnd).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔄 D&D再試行", command=self.retry_dnd_setup).pack(side=tk.LEFT, padx=2)
        
        # ファイル情報表示
        self.file_info_var = tk.StringVar(value="画像が選択されていません")
        info_label = ttk.Label(image_frame, textvariable=self.file_info_var, foreground="gray")
        info_label.grid(row=2, column=0, columnspan=2, pady=2, sticky=tk.W)
        
        # D&D状態表示
        self.dnd_status_var = tk.StringVar(value="D&D状態: 初期化中...")
        dnd_status_label = ttk.Label(image_frame, textvariable=self.dnd_status_var, foreground="blue")
        dnd_status_label.grid(row=3, column=0, columnspan=2, pady=2, sticky=tk.W)
        
        # 基本的なクリック機能を先に設定
        self.setup_basic_interactions()
        
        # D&D機能の設定（遅延実行）
        self.parent.after(100, self.setup_drag_and_drop)
        
        debug_logger.log_function_exit("create_frame", image_frame)
        return image_frame
    
    def setup_basic_interactions(self):
        """基本的なインタラクション（クリック、ホバー）を設定"""
        debug_logger.log_function_entry("setup_basic_interactions")
        
        # 基本的なクリックイベント
        self.image_display_frame.bind("<Button-1>", self.on_click)
        debug_logger.debug("クリックイベント設定完了")
        
        # マウスホバー効果
        self.image_display_frame.bind("<Enter>", self.on_enter)
        self.image_display_frame.bind("<Leave>", self.on_leave)
        self.drop_label.bind("<Enter>", self.on_enter)
        self.drop_label.bind("<Leave>", self.on_leave)
        debug_logger.debug("ホバーイベント設定完了")
        
        debug_logger.log_function_exit("setup_basic_interactions")
    
    def retry_dnd_setup(self):
        """D&D設定を再試行"""
        debug_logger.log_function_entry("retry_dnd_setup")
        self.dnd_status_var.set("D&D状態: 再初期化中...")
        self.setup_drag_and_drop()
        debug_logger.log_function_exit("retry_dnd_setup")
    
    def get_root_window(self):
        """ルートウィンドウを取得"""
        if self.root_window is None:
            root = self.parent
            while root.master:
                root = root.master
            self.root_window = root
            debug_logger.debug(f"ルートウィンドウ取得: {self.root_window}")
        return self.root_window
    
    def setup_drag_and_drop(self):
        """D&D機能を設定"""
        debug_logger.log_function_entry("setup_drag_and_drop")
        
        try:
            # tkinterdnd2の段階的初期化
            debug_logger.info("tkinterdnd2初期化開始")
            
            # Step 1: インポートチェック
            try:
                import tkinterdnd2
                from tkinterdnd2 import TkinterDnD, DND_FILES
                debug_logger.info(f"tkinterdnd2インポート成功 - version: {getattr(tkinterdnd2, '__version__', 'unknown')}")
            except ImportError as e:
                debug_logger.error(f"tkinterdnd2インポート失敗: {e}")
                self.dnd_status_var.set("D&D状態: tkinterdnd2未インストール")
                return
            
            # Step 2: ルートウィンドウの取得と初期化
            root = self.get_root_window()
            
            # Step 3: TkinterDnDの初期化（複数の方法を試行）
            try:
                # 方法1: 既存のルートウィンドウを使用
                debug_logger.debug("方法1: 既存ルートでD&D初期化試行")
                
                # tkdndライブラリの存在確認
                try:
                    root.tk.call('package', 'require', 'tkdnd')
                    debug_logger.info("tkdndパッケージが利用可能")
                except tk.TclError as e:
                    debug_logger.warning(f"tkdndパッケージエラー: {e}")
                    
                    # 方法2: TkinterDnD.Tkを使用
                    debug_logger.debug("方法2: TkinterDnD.Tk()で新規作成")
                    try:
                        # 新しいD&D対応ウィンドウ作成は避ける（既存UIを保持）
                        debug_logger.warning("TkinterDnD.Tk()は既存UIとの競合を避けるため使用しません")
                        raise Exception("既存UI保持のためスキップ")
                    except:
                        # 方法3: 手動初期化
                        debug_logger.debug("方法3: 手動でtkdnd初期化")
                        try:
                            # tkdndの動的読み込みを試行
                            import tkinterdnd2.tkdnd as tkdnd
                            tkdnd_path = os.path.dirname(tkdnd.__file__)
                            debug_logger.debug(f"tkdndパス: {tkdnd_path}")
                            
                            # Tclスクリプトの読み込み
                            root.tk.eval(f'source "{os.path.join(tkdnd_path, "tkdnd.tcl")}"')
                            debug_logger.info("tkdnd.tclの読み込み成功")
                            
                        except Exception as manual_init_error:
                            debug_logger.exception(f"手動初期化失敗: {manual_init_error}")
                            raise
                
                # Step 4: D&Dイベントハンドラーの定義
                def on_drop_enter(event):
                    debug_logger.log_event("drop_enter", widget=str(event.widget))
                    self.image_display_frame.config(bg="lightgreen")
                    self.drop_label.config(bg="lightgreen", text="画像をここにドロップ！")
                    return 'copy'
                
                def on_drop_leave(event):
                    debug_logger.log_event("drop_leave", widget=str(event.widget))
                    self.image_display_frame.config(bg="lightgray")
                    self.drop_label.config(bg="lightgray", text="画像をドラッグ&ドロップ\nまたは下のボタンで選択")
                    return 'none'
                
                def on_drop(event):
                    debug_logger.log_event("drop", data=event.data, widget=str(event.widget))
                    
                    try:
                        # ドロップされたファイルを処理
                        files = event.data.split()
                        debug_logger.debug(f"ドロップファイル: {files}")
                        
                        if files:
                            file_path = files[0].strip('{}').strip('"').strip("'")  # 各種括弧を除去
                            debug_logger.info(f"処理対象ファイル: {file_path}")
                            
                            # 画像ファイルかチェック
                            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']
                            if any(file_path.lower().endswith(ext) for ext in valid_extensions):
                                self.load_image_file(file_path)
                            else:
                                debug_logger.warning(f"サポートされていないファイル形式: {file_path}")
                                messagebox.showwarning("警告", "サポートされていないファイル形式です")
                        
                    except Exception as drop_error:
                        debug_logger.exception(f"ドロップ処理エラー: {drop_error}")
                    finally:
                        # UI を元に戻す
                        self.image_display_frame.config(bg="lightgray")
                        self.drop_label.config(bg="lightgray", text="画像をドラッグ&ドロップ\nまたは下のボタンで選択")
                    
                    return 'copy'
                
                # Step 5: D&Dの登録
                debug_logger.debug("D&Dターゲット登録開始")
                self.image_display_frame.drop_target_register(DND_FILES)
                debug_logger.debug("drop_target_register完了")
                
                self.image_display_frame.dnd_bind('<<DropEnter>>', on_drop_enter)
                debug_logger.debug("DropEnterバインド完了")
                
                self.image_display_frame.dnd_bind('<<DropLeave>>', on_drop_leave)
                debug_logger.debug("DropLeaveバインド完了")
                
                self.image_display_frame.dnd_bind('<<Drop>>', on_drop)
                debug_logger.debug("Dropバインド完了")
                
                debug_logger.info("D&D機能登録完了")
                self.dnd_enabled = True
                self.dnd_status_var.set("D&D状態: ✅ 有効（ファイルをドロップできます）")
                self.drop_label.config(text="画像をドラッグ&ドロップ\nまたは下のボタンで選択")
                
            except tk.TclError as tcl_error:
                debug_logger.error(f"Tcl/Tkエラー: {tcl_error}")
                if "invalid command name" in str(tcl_error):
                    self.dnd_status_var.set("D&D状態: ❌ tkdndライブラリが見つかりません")
                    self.setup_fallback_dnd()
                else:
                    self.dnd_status_var.set(f"D&D状態: ❌ Tclエラー")
            
        except Exception as e:
            debug_logger.exception(f"D&D初期化で予期しないエラー: {e}")
            self.dnd_status_var.set(f"D&D状態: ❌ 初期化エラー")
            self.setup_fallback_dnd()
        
        debug_logger.log_function_exit("setup_drag_and_drop", self.dnd_enabled)
    
    def setup_fallback_dnd(self):
        """フォールバックD&D機能"""
        debug_logger.log_function_entry("setup_fallback_dnd")
        
        # フォールバック: ファイルパスのクリップボード監視
        def check_clipboard():
            try:
                clipboard_content = self.get_root_window().clipboard_get()
                if (clipboard_content and 
                    os.path.isfile(clipboard_content) and 
                    any(clipboard_content.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'])):
                    
                    debug_logger.info(f"クリップボードから画像ファイル検出: {clipboard_content}")
                    self.load_image_file(clipboard_content)
            except:
                pass
        
        # 右クリックメニューでクリップボードチェック
        def show_context_menu(event):
            context_menu = tk.Menu(self.get_root_window(), tearoff=0)
            context_menu.add_command(label="📁 ファイルを選択", command=self.browse_image)
            context_menu.add_command(label="📋 クリップボードから", command=self.paste_from_clipboard)
            context_menu.add_separator()
            context_menu.add_command(label="🔍 クリップボードのパスをチェック", command=check_clipboard)
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            except:
                pass
            finally:
                context_menu.grab_release()
        
        self.image_display_frame.bind("<Button-3>", show_context_menu)  # 右クリック
        
        self.dnd_status_var.set("D&D状態: ⚠️ 代替機能（右クリックメニュー利用）")
        debug_logger.info("フォールバックD&D機能設定完了")
        
        debug_logger.log_function_exit("setup_fallback_dnd")
    
    def test_dnd(self):
        """D&D機能のテスト"""
        debug_logger.log_function_entry("test_dnd")
        
        try:
            import tkinterdnd2
            version = getattr(tkinterdnd2, '__version__', 'unknown')
            debug_logger.info(f"tkinterdnd2バージョン: {version}")
            
            # tkdndライブラリのテスト
            root = self.get_root_window()
            try:
                result = root.tk.call('package', 'require', 'tkdnd')
                debug_logger.info(f"tkdndパッケージテスト成功: {result}")
                test_result = f"✅ tkinterdnd2 v{version}\n✅ tkdndライブラリ利用可能"
            except tk.TclError as e:
                debug_logger.error(f"tkdndパッケージテスト失敗: {e}")
                test_result = f"⚠️ tkinterdnd2 v{version}\n❌ tkdndライブラリエラー: {e}"
            
            messagebox.showinfo("D&Dテスト結果", test_result)
            self.dnd_status_var.set(f"テスト実行: {test_result.replace(chr(10), ' ')}")
            
        except ImportError as e:
            debug_logger.error(f"tkinterdnd2インポートエラー: {e}")
            self.dnd_status_var.set("D&D状態: tkinterdnd2が見つかりません")
            messagebox.showerror("D&Dテスト", "tkinterdnd2がインストールされていません\n\npip install tkinterdnd2")
        
        debug_logger.log_function_exit("test_dnd")
    
    def on_click(self, event):
        """クリック時の処理"""
        debug_logger.log_event("click", x=event.x, y=event.y)
        self.browse_image()
    
    def on_enter(self, event):
        """マウスエンター時の処理"""
        if not self.dnd_enabled:
            self.image_display_frame.config(bg="lightblue")
            self.drop_label.config(bg="lightblue")
    
    def on_leave(self, event):
        """マウスリーブ時の処理"""
        if not self.dnd_enabled:
            self.image_display_frame.config(bg="lightgray")
            self.drop_label.config(bg="lightgray")
    
    # 他のメソッドは変更なし（browse_image, load_image_file等）
    def browse_image(self):
        """画像ファイルを参照して選択"""
        debug_logger.log_function_entry("browse_image")
        
        file_types = [
            ("画像ファイル", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff *.tif"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("GIF files", "*.gif"),
            ("WebP files", "*.webp"),
            ("TIFF files", "*.tiff *.tif"),
            ("BMP files", "*.bmp"),
            ("すべてのファイル", "*.*")
        ]
        
        try:
            file_path = filedialog.askopenfilename(
                title="画像ファイルを選択",
                filetypes=file_types,
                initialdir=os.path.expanduser("~/Pictures")
            )
            
            debug_logger.debug(f"選択されたファイル: {file_path}")
            
            if file_path:
                self.load_image_file(file_path)
            else:
                debug_logger.debug("ファイル選択がキャンセルされました")
                
        except Exception as e:
            debug_logger.exception(f"ファイル選択エラー: {e}")
        
        debug_logger.log_function_exit("browse_image")
    
    def load_image_file(self, file_path):
        """画像ファイルを読み込み表示"""
        debug_logger.log_function_entry("load_image_file", file_path=file_path)
        
        try:
            if not os.path.exists(file_path):
                debug_logger.error(f"ファイルが存在しません: {file_path}")
                messagebox.showerror("エラー", "ファイルが存在しません")
                return
            
            debug_logger.info(f"画像読み込み開始: {file_path}")
            
            # 画像を開く
            image = Image.open(file_path)
            self.current_image = image
            self.current_image_path = file_path
            
            debug_logger.debug(f"画像サイズ: {image.width}x{image.height}, モード: {image.mode}")
            
            # サムネイル作成（表示用）
            display_size = (280, 180)
            thumbnail = create_thumbnail(image, display_size)
            
            # PhotoImageに変換
            self.photo = ImageTk.PhotoImage(thumbnail)
            
            # 画像を表示
            self.drop_label.place_forget()
            self.image_label.config(image=self.photo)
            self.image_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # ファイル情報更新
            file_size = os.path.getsize(file_path) / 1024  # KB
            file_name = os.path.basename(file_path)
            info_text = f"📁 {file_name} ({image.width}x{image.height}, {file_size:.1f}KB)"
            self.file_info_var.set(info_text)
            
            debug_logger.info(f"画像読み込み完了: {info_text}")
            
        except Exception as e:
            debug_logger.exception(f"画像読み込みエラー: {e}")
            messagebox.showerror("エラー", f"画像の読み込みに失敗しました:\n{str(e)}")
        
        debug_logger.log_function_exit("load_image_file")
    
    def paste_from_clipboard(self):
        """クリップボードから画像を貼り付け"""
        debug_logger.log_function_entry("paste_from_clipboard")
        
        try:
            from PIL import ImageGrab
            
            # クリップボードから画像を取得
            clipboard_image = ImageGrab.grabclipboard()
            
            if clipboard_image is None:
                debug_logger.info("クリップボードに画像がありません")
                messagebox.showinfo("情報", "クリップボードに画像がありません")
                return
            
            debug_logger.info(f"クリップボード画像取得: {clipboard_image.size}")
            
            # 画像として読み込み
            self.load_image_from_pil(clipboard_image, "クリップボード画像")
            
        except ImportError:
            debug_logger.error("PIL (Pillow) ライブラリが必要です")
            messagebox.showerror("エラー", "PIL (Pillow) ライブラリが必要です")
        except Exception as e:
            debug_logger.exception(f"クリップボード画像取得エラー: {e}")
            messagebox.showerror("エラー", f"クリップボードから画像を取得できませんでした:\n{str(e)}")
        
        debug_logger.log_function_exit("paste_from_clipboard")
    
    def load_image_from_pil(self, pil_image, display_name="画像"):
        """PILイメージから直接読み込み"""
        debug_logger.log_function_entry("load_image_from_pil", display_name=display_name, size=pil_image.size)
        
        try:
            self.current_image = pil_image
            self.current_image_path = None  # クリップボード画像の場合はパスなし
            
            # サムネイル作成（表示用）
            display_size = (280, 180)
            thumbnail = create_thumbnail(pil_image, display_size)
            
            # PhotoImageに変換
            self.photo = ImageTk.PhotoImage(thumbnail)
            
            # 画像を表示
            self.drop_label.place_forget()
            self.image_label.config(image=self.photo)
            self.image_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # ファイル情報更新
            info_text = f"📋 {display_name} ({pil_image.width}x{pil_image.height})"
            self.file_info_var.set(info_text)
            
            debug_logger.info(f"PIL画像読み込み完了: {info_text}")
            
        except Exception as e:
            debug_logger.exception(f"PIL画像読み込みエラー: {e}")
            messagebox.showerror("エラー", f"画像の読み込みに失敗しました:\n{str(e)}")
        
        debug_logger.log_function_exit("load_image_from_pil")
    
    def clear_image(self):
        """画像をクリア"""
        debug_logger.log_function_entry("clear_image")
        
        self.current_image = None
        self.current_image_path = None
        self.image_label.place_forget()
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
        self.file_info_var.set("画像が選択されていません")
        if hasattr(self, 'photo'):
            del self.photo
        
        debug_logger.info("画像クリア完了")
        debug_logger.log_function_exit("clear_image")
    
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
        debug_logger.log_function_entry("save_temp_image")
        
        if self.current_image and not self.current_image_path:
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"temp_image_{id(self)}.png")
            self.current_image.save(temp_path)
            debug_logger.info(f"一時ファイル保存: {temp_path}")
            debug_logger.log_function_exit("save_temp_image", temp_path)
            return temp_path
        
        debug_logger.log_function_exit("save_temp_image", self.current_image_path)
        return self.current_image_path