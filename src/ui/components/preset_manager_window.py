"""プリセット管理ウィンドウ（修正版）"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

class PresetManagerWindow:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.preset_file = "presets.json"
        self.window = None
        self.presets = self.load_presets()
    
    def load_presets(self):
        """プリセットデータを読み込み"""
        try:
            if os.path.exists(self.preset_file):
                with open(self.preset_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def save_presets(self):
        """プリセットデータを保存"""
        try:
            with open(self.preset_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("エラー", f"プリセット保存に失敗しました: {e}")
    
    def show_window(self):
        """プリセット管理ウィンドウを表示"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("プリセット管理")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # プリセットリストフレーム
        list_frame = ttk.LabelFrame(main_frame, text="保存されたプリセット", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # リストボックス
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.preset_listbox = tk.Listbox(list_container)
        scrollbar_list = ttk.Scrollbar(list_container, orient="vertical", command=self.preset_listbox.yview)
        self.preset_listbox.configure(yscrollcommand=scrollbar_list.set)
        
        self.preset_listbox.pack(side="left", fill="both", expand=True)
        scrollbar_list.pack(side="right", fill="y")
        
        self.preset_listbox.bind("<<ListboxSelect>>", self.on_preset_select)
        self.preset_listbox.bind("<Double-1>", self.apply_preset)
        
        # プリセット詳細フレーム
        details_frame = ttk.LabelFrame(main_frame, text="プリセット詳細", padding="5")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 修正：normalで作成してからdisabledに設定
        self.details_text = tk.Text(details_frame, height=8)
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.pack(side="left", fill="both", expand=True)
        details_scroll.pack(side="right", fill="y")
        
        # 初期状態をdisabledに設定
        self.details_text.config(state='disabled')
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="💾 現在の設定を保存", command=self.save_current_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="✅ 選択したプリセットを適用", command=self.apply_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="✏️ 名前を変更", command=self.rename_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ 削除", command=self.delete_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ 閉じる", command=self.window.destroy).pack(side=tk.RIGHT)
        
        # 初期データ読み込み
        self.refresh_preset_list()
    
    def refresh_preset_list(self):
        """プリセットリストを更新"""
        self.preset_listbox.delete(0, tk.END)
        for name in sorted(self.presets.keys()):
            self.preset_listbox.insert(tk.END, name)
    
    def on_preset_select(self, event=None):
        """プリセット選択時の詳細表示"""
        selection = self.preset_listbox.curselection()
        if not selection:
            return
        
        preset_name = self.preset_listbox.get(selection[0])
        preset_data = self.presets.get(preset_name, {})
        
        # 詳細表示
        self.details_text.config(state='normal')
        self.details_text.delete("1.0", tk.END)
        
        details = []
        details.append(f"プリセット名: {preset_name}")
        details.append(f"モード: {preset_data.get('mode', 'N/A')}")
        details.append(f"モデル: {preset_data.get('model_display_name', 'N/A')}")
        details.append(f"推論ステップ数: {preset_data.get('inference_steps', 'N/A')}")
        details.append(f"ガイダンススケール: {preset_data.get('guidance_scale', 'N/A')}")
        details.append(f"画像枚数: {preset_data.get('num_images', 'N/A')}")
        details.append(f"安全性フィルター: {'有効' if preset_data.get('safety_checker', True) else '無効'}")
        
        if preset_data.get('mode') == 'image-to-image':
            details.append(f"Strength: {preset_data.get('strength', 'N/A')}")
        
        if not preset_data.get('use_custom_size', False):
            details.append(f"画像サイズ: {preset_data.get('image_size', 'N/A')}")
        else:
            details.append(f"カスタムサイズ: {preset_data.get('custom_width', 'N/A')}x{preset_data.get('custom_height', 'N/A')}")
        
        details.append("")
        details.append("プロンプト:")
        details.append(preset_data.get('prompt', 'N/A'))
        
        if preset_data.get('negative_prompt'):
            details.append("")
            details.append("ネガティブプロンプト:")
            details.append(preset_data.get('negative_prompt', ''))
        
        self.details_text.insert("1.0", "\n".join(details))
        self.details_text.config(state='disabled')
    
    def save_current_preset(self):
        """現在の設定をプリセットとして保存"""
        preset_name = simpledialog.askstring("プリセット保存", "プリセット名を入力してください:")
        if not preset_name:
            return
        
        if preset_name in self.presets:
            if not messagebox.askyesno("確認", f"プリセット '{preset_name}' は既に存在します。上書きしますか？"):
                return
        
        try:
            # 現在の設定を取得
            preset_data = {
                "mode": self.main_window.current_mode,
                "model_endpoint": self.main_window.model_frame.get_selected_model_endpoint(),
                "model_display_name": self.main_window.model_frame.get_selected_model_display_name(),
                "prompt": self.main_window.prompt_frame.get_prompt(),
                "negative_prompt": self.main_window.prompt_frame.get_negative_prompt(),
                "inference_steps": self.main_window.settings_frame.inference_steps_var.get(),
                "guidance_scale": self.main_window.settings_frame.guidance_scale_var.get(),
                "num_images": self.main_window.settings_frame.num_images_var.get(),
                "safety_checker": self.main_window.settings_frame.safety_checker_var.get(),
                "strength": self.main_window.settings_frame.strength_var.get(),
                "use_custom_size": self.main_window.size_frame.use_custom_size_var.get(),
                "image_size": self.main_window.size_frame.image_size_var.get(),
                "custom_width": self.main_window.size_frame.custom_width_var.get(),
                "custom_height": self.main_window.size_frame.custom_height_var.get(),
            }
            
            self.presets[preset_name] = preset_data
            self.save_presets()
            self.refresh_preset_list()
            messagebox.showinfo("完了", f"プリセット '{preset_name}' を保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"プリセット保存に失敗しました: {e}")
    
    def apply_preset(self, event=None):
        """選択したプリセットを適用"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "プリセットを選択してください")
            return
        
        preset_name = self.preset_listbox.get(selection[0])
        preset_data = self.presets.get(preset_name, {})
        
        try:
            # モードを設定
            mode = preset_data.get("mode", "text-to-image")
            self.main_window.mode_frame.set_mode(mode)
            
            # プロンプトを設定
            self.main_window.prompt_frame.set_prompt(preset_data.get("prompt", ""))
            self.main_window.prompt_frame.set_negative_prompt(preset_data.get("negative_prompt", ""))
            
            # 設定値を適用
            self.main_window.settings_frame.inference_steps_var.set(preset_data.get("inference_steps", 28))
            self.main_window.settings_frame.guidance_scale_var.set(preset_data.get("guidance_scale", 3.5))
            self.main_window.settings_frame.num_images_var.set(preset_data.get("num_images", 1))
            self.main_window.settings_frame.safety_checker_var.set(preset_data.get("safety_checker", True))
            self.main_window.settings_frame.strength_var.set(preset_data.get("strength", 0.95))
            
            # サイズ設定を適用
            self.main_window.size_frame.use_custom_size_var.set(preset_data.get("use_custom_size", False))
            self.main_window.size_frame.image_size_var.set(preset_data.get("image_size", "landscape_4_3"))
            self.main_window.size_frame.custom_width_var.set(preset_data.get("custom_width", 1024))
            self.main_window.size_frame.custom_height_var.set(preset_data.get("custom_height", 768))
            
            # モデルを設定（モードが設定された後に）
            model_display_name = preset_data.get("model_display_name", "")
            if model_display_name:
                self.main_window.model_frame.model_var.set(model_display_name)
            
            messagebox.showinfo("完了", f"プリセット '{preset_name}' を適用しました")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("エラー", f"プリセット適用に失敗しました: {e}")
    
    def rename_preset(self):
        """プリセット名を変更"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "名前を変更するプリセットを選択してください")
            return
        
        old_name = self.preset_listbox.get(selection[0])
        new_name = simpledialog.askstring("プリセット名変更", f"新しい名前を入力してください:", initialvalue=old_name)
        
        if not new_name or new_name == old_name:
            return
        
        if new_name in self.presets:
            messagebox.showerror("エラー", f"プリセット名 '{new_name}' は既に存在します")
            return
        
        self.presets[new_name] = self.presets.pop(old_name)
        self.save_presets()
        self.refresh_preset_list()
        messagebox.showinfo("完了", f"プリセット名を '{new_name}' に変更しました")
    
    def delete_preset(self):
        """プリセットを削除"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するプリセットを選択してください")
            return
        
        preset_name = self.preset_listbox.get(selection[0])
        if not messagebox.askyesno("確認", f"プリセット '{preset_name}' を削除しますか？"):
            return
        
        del self.presets[preset_name]
        self.save_presets()
        self.refresh_preset_list()
        
        # 詳細表示をクリア
        self.details_text.config(state='normal')
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state='disabled')
        
        messagebox.showinfo("完了", f"プリセット '{preset_name}' を削除しました")