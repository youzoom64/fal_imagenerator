"""結果表示フレームコンポーネント"""
import tkinter as tk
from tkinter import ttk
import webbrowser
from PIL import ImageTk
from ..utils.image_utils import ImageDisplayManager

class ResultFrame:
    def __init__(self, parent, output_dir):
        self.parent = parent
        self.output_dir = output_dir
        self.generated_images = []
        self.image_display_manager = ImageDisplayManager()
        self.frame = self.create_frame()
    
    def create_frame(self):
        """結果表示フレームを作成"""
        result_frame = ttk.LabelFrame(self.parent, text="生成結果", padding="5")
        
        # 画像表示用のキャンバスとスクロールバー
        canvas_frame = ttk.Frame(result_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.result_canvas = tk.Canvas(canvas_frame, height=300)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.result_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.result_canvas)
        
        self.scrollable_frame.bind("<Configure>", 
                                  lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        
        self.result_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.result_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.result_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ボタンフレーム
        button_result_frame = ttk.Frame(result_frame)
        button_result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(button_result_frame, text="結果をクリア", command=self.clear_results).pack(side=tk.LEFT)
        
        # グリッド設定
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        return result_frame
    
    def display_images(self, image_results, saved_files):
        """生成された画像を表示"""
        for i, (image_data, saved_file) in enumerate(zip(image_results, saved_files)):
            # 画像を取得してサムネイル作成
            image_info = self.image_display_manager.create_image_display(image_data['url'], saved_file)
            
            if not image_info["success"]:
                continue
            
            image = image_info["image"]
            photo = image_info["photo"]
            
            self.generated_images.append({
                'image': image,
                'url': image_data['url'],
                'filename': saved_file
            })
            
            # 画像表示フレームを作成
            img_frame = ttk.Frame(self.scrollable_frame)
            img_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            img_label = ttk.Label(img_frame, image=photo)
            img_label.image = photo  # 参照を保持
            img_label.grid(row=0, column=0, columnspan=2)
            
            size_info = f"{image.width}x{image.height}\n保存済: {saved_file}"
            size_label = ttk.Label(img_frame, text=size_info, foreground="gray")
            size_label.grid(row=1, column=0, columnspan=2)
            
            ttk.Button(img_frame, text="ブラウザで開く", 
                      command=lambda url=image_data['url']: webbrowser.open(url)).grid(
                          row=2, column=0, padx=2, pady=2, columnspan=2)
    
    def clear_results(self):
        """結果をクリア"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.generated_images = []
    
    def get_generated_images(self):
        """生成された画像のリストを取得"""
        return self.generated_images