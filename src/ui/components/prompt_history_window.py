"""プロンプト履歴ウィンドウ（修正版）"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from datetime import datetime

class PromptHistoryWindow:
    def __init__(self, parent, prompt_frame):
        self.parent = parent
        self.prompt_frame = prompt_frame
        self.history_file = "prompt_history.json"
        self.window = None
        self.history_data = self.load_history()
        
    def load_history(self):
        """履歴データを読み込み"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"prompts": []}
        except Exception:
            return {"prompts": []}
    
    def save_history(self):
        """履歴データを保存"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def add_to_history(self, prompt, negative_prompt=""):
        """履歴にプロンプトを追加"""
        if not prompt.strip():
            return
            
        # 重複チェック
        for item in self.history_data["prompts"]:
            if item["prompt"] == prompt and item.get("negative_prompt", "") == negative_prompt:
                # 既存の場合は時間だけ更新
                item["timestamp"] = datetime.now().isoformat()
                self.save_history()
                return
        
        # 新規追加
        entry = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "timestamp": datetime.now().isoformat()
        }
        
        self.history_data["prompts"].insert(0, entry)  # 最新を先頭に
        
        # 最大100件まで保持
        if len(self.history_data["prompts"]) > 100:
            self.history_data["prompts"] = self.history_data["prompts"][:100]
        
        self.save_history()
    
    def show_window(self):
        """履歴ウィンドウを表示"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("プロンプト履歴")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 検索フレーム
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="検索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="🔍 検索", command=self.on_search).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(search_frame, text="🔄 リフレッシュ", command=self.refresh_list).pack(side=tk.LEFT)
        
        # 履歴リストフレーム
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for history list
        columns = ("date", "prompt", "negative")
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 列設定
        self.history_tree.heading("date", text="日時")
        self.history_tree.heading("prompt", text="プロンプト")
        self.history_tree.heading("negative", text="ネガティブプロンプト")
        
        self.history_tree.column("date", width=120, minwidth=100)
        self.history_tree.column("prompt", width=400, minwidth=200)
        self.history_tree.column("negative", width=250, minwidth=100)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ダブルクリックイベント
        self.history_tree.bind("<Double-1>", self.on_item_select)
        
        # プレビューフレーム
        preview_frame = ttk.LabelFrame(main_frame, text="プレビュー", padding="5")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        # プロンプトプレビュー - 修正：state='normal'で作成後にreadonlyに設定
        ttk.Label(preview_frame, text="プロンプト:").grid(row=0, column=0, sticky=(tk.W, tk.N), pady=2)
        self.preview_prompt = scrolledtext.ScrolledText(preview_frame, height=4, width=80)
        self.preview_prompt.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.preview_prompt.config(state='disabled')  # 修正：readonlyではなくdisabledを使用
        
        # ネガティブプロンプトプレビュー - 修正：同様に修正
        ttk.Label(preview_frame, text="ネガティブ:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=2)
        self.preview_negative = scrolledtext.ScrolledText(preview_frame, height=2, width=80)
        self.preview_negative.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.preview_negative.config(state='disabled')  # 修正：readonlyではなくdisabledを使用
        
        preview_frame.columnconfigure(1, weight=1)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="✅ 選択して適用", command=self.apply_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📝 プロンプトのみ適用", command=lambda: self.apply_selected(prompt_only=True)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ 選択項目を削除", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🧹 全履歴クリア", command=self.clear_all_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ 閉じる", command=self.window.destroy).pack(side=tk.RIGHT)
        
        # 初期データ読み込み
        self.refresh_list()
        
        # 選択変更イベント
        self.history_tree.bind("<<TreeviewSelect>>", self.on_selection_change)
    
    def refresh_list(self):
        """リストを更新"""
        self.history_data = self.load_history()
        self.populate_list()
    
    def populate_list(self, items=None):
        """リストに項目を追加"""
        # 既存項目をクリア
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        if items is None:
            items = self.history_data["prompts"]
        
        for entry in items:
            try:
                # 日時フォーマット
                timestamp = entry.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        date_str = dt.strftime("%m/%d %H:%M")
                    except:
                        date_str = "不明"
                else:
                    date_str = "不明"
                
                # プロンプト表示（長い場合は省略）
                prompt = entry.get("prompt", "")
                prompt_display = prompt[:80] + "..." if len(prompt) > 80 else prompt
                
                negative = entry.get("negative_prompt", "")
                negative_display = negative[:50] + "..." if len(negative) > 50 else negative
                
                self.history_tree.insert("", "end", values=(date_str, prompt_display, negative_display))
            except Exception:
                continue
    
    def on_search(self, event=None):
        """検索処理"""
        query = self.search_var.get().lower()
        if not query:
            self.populate_list()
            return
        
        filtered_items = []
        for entry in self.history_data["prompts"]:
            if (query in entry.get("prompt", "").lower() or 
                query in entry.get("negative_prompt", "").lower()):
                filtered_items.append(entry)
        
        self.populate_list(filtered_items)
    
    def on_selection_change(self, event=None):
        """選択変更時のプレビュー更新"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        try:
            item_index = self.history_tree.index(selection[0])
            current_items = self.get_current_items()
            
            if 0 <= item_index < len(current_items):
                entry = current_items[item_index]
                
                # プレビュー更新 - 修正：正しいstate管理
                self.preview_prompt.config(state='normal')
                self.preview_prompt.delete("1.0", tk.END)
                self.preview_prompt.insert("1.0", entry.get("prompt", ""))
                self.preview_prompt.config(state='disabled')
                
                self.preview_negative.config(state='normal')
                self.preview_negative.delete("1.0", tk.END)
                self.preview_negative.insert("1.0", entry.get("negative_prompt", ""))
                self.preview_negative.config(state='disabled')
        except Exception:
            pass
    
    def on_item_select(self, event=None):
        """ダブルクリック時の処理"""
        self.apply_selected()
    
    def get_current_items(self):
        """現在表示されているアイテムを取得"""
        query = self.search_var.get().lower()
        if not query:
            return self.history_data["prompts"]
        
        filtered_items = []
        for entry in self.history_data["prompts"]:
            if (query in entry.get("prompt", "").lower() or 
                query in entry.get("negative_prompt", "").lower()):
                filtered_items.append(entry)
        return filtered_items
    
    def apply_selected(self, prompt_only=False):
        """選択した項目を適用"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "項目を選択してください")
            return
        
        try:
            item_index = self.history_tree.index(selection[0])
            current_items = self.get_current_items()
            
            if 0 <= item_index < len(current_items):
                entry = current_items[item_index]
                
                # プロンプトを適用
                self.prompt_frame.set_prompt(entry.get("prompt", ""))
                
                if not prompt_only:
                    # ネガティブプロンプトも適用
                    self.prompt_frame.set_negative_prompt(entry.get("negative_prompt", ""))
                
                messagebox.showinfo("完了", "プロンプトを適用しました")
                self.window.destroy()
        except Exception as e:
            messagebox.showerror("エラー", f"適用に失敗しました: {e}")
    
    def delete_selected(self):
        """選択した項目を削除"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "削除する項目を選択してください")
            return
        
        if not messagebox.askyesno("確認", "選択した項目を削除しますか？"):
            return
        
        try:
            item_index = self.history_tree.index(selection[0])
            current_items = self.get_current_items()
            
            if 0 <= item_index < len(current_items):
                entry_to_delete = current_items[item_index]
                
                # 元のリストから削除
                for i, entry in enumerate(self.history_data["prompts"]):
                    if (entry.get("prompt", "") == entry_to_delete.get("prompt", "") and 
                        entry.get("negative_prompt", "") == entry_to_delete.get("negative_prompt", "")):
                        del self.history_data["prompts"][i]
                        break
                
                self.save_history()
                self.refresh_list()
                messagebox.showinfo("完了", "項目を削除しました")
        except Exception as e:
            messagebox.showerror("エラー", f"削除に失敗しました: {e}")
    
    def clear_all_history(self):
        """全履歴をクリア"""
        if not messagebox.askyesno("確認", "全ての履歴を削除しますか？\n\nこの操作は取り消せません。"):
            return
        
        try:
            self.history_data = {"prompts": []}
            self.save_history()
            self.refresh_list()
            messagebox.showinfo("完了", "全履歴を削除しました")
        except Exception as e:
            messagebox.showerror("エラー", f"削除に失敗しました: {e}")