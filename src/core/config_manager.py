"""設定の読み書きを管理するクラス（自動設定記憶対応）"""
import json
import os
import threading
import time

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.auto_save = True
        self.auto_save_delay = 2  # 2秒後に自動保存
        self.save_timer = None
        
        self.default_config = {
            "api_key": "",
            "default_model": "fal-ai/flux/dev",
            "default_prompt": "A beautiful landscape with mountains and cherry blossoms",
            "default_negative_prompt": "",
            "default_image_size": "landscape_4_3",
            "default_custom_width": 1024,
            "default_custom_height": 768,
            "default_inference_steps": 28,
            "default_guidance_scale": 3.5,
            "default_num_images": 1,
            "default_use_custom_size": False,
            "enable_safety_checker": True,
            "default_strength": 0.95,
            "window_width": 900,
            "window_height": 1200,
            "window_x": None,
            "window_y": None,
            "last_mode": "text-to-image",
            "auto_save_prompts": True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """設定を読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # デフォルト値で不足キーを補完
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """設定を即座に保存"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.config = config
        except Exception as e:
            print(f"設定保存エラー: {e}")
    
    def auto_save_config(self):
        """自動保存（遅延実行）"""
        if not self.auto_save:
            return
            
        # 既存のタイマーをキャンセル
        if self.save_timer:
            self.save_timer.cancel()
        
        # 新しいタイマーを設定
        self.save_timer = threading.Timer(self.auto_save_delay, self.save_config)
        self.save_timer.start()
    
    def get(self, key, default=None):
        """設定値を取得"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """設定値を更新（自動保存付き）"""
        self.config[key] = value
        if self.auto_save:
            self.auto_save_config()
    
    def update(self, updates):
        """複数の設定値を一括更新（自動保存付き）"""
        self.config.update(updates)
        if self.auto_save:
            self.auto_save_config()
    
    def save_window_geometry(self, window):
        """ウィンドウ位置・サイズを保存"""
        try:
            geometry = window.geometry()
            # "WIDTHxHEIGHT+X+Y" 形式をパース
            size_pos = geometry.split('+')
            if len(size_pos) >= 3:
                width_height = size_pos[0].split('x')
                if len(width_height) == 2:
                    self.set("window_width", int(width_height[0]))
                    self.set("window_height", int(width_height[1]))
                    self.set("window_x", int(size_pos[1]))
                    self.set("window_y", int(size_pos[2]))
        except Exception:
            pass
    
    def restore_window_geometry(self, window):
        """ウィンドウ位置・サイズを復元"""
        try:
            width = self.get("window_width", 900)
            height = self.get("window_height", 1200)
            x = self.get("window_x")
            y = self.get("window_y")
            
            if x is not None and y is not None:
                window.geometry(f"{width}x{height}+{x}+{y}")
            else:
                window.geometry(f"{width}x{height}")
        except Exception:
            window.geometry("900x1200")

    def safe_set(self, key, value):
        """安全な設定値更新"""
        try:
            # 値の妥当性チェック
            if value is None:
                return
                
            # 型による検証
            if key in ['window_width', 'window_height', 'window_x', 'window_y']:
                if not isinstance(value, (int, float)) or value < 0:
                    return
                    
            if key in ['default_guidance_scale', 'default_strength']:
                if not isinstance(value, (int, float)) or value < 0:
                    return
                    
            self.config[key] = value
            if self.auto_save:
                self.auto_save_config()
        except Exception as e:
            print(f"設定保存エラー ({key}): {e}")

    def safe_get(self, key, default=None):
        """安全な設定値取得"""
        try:
            value = self.config.get(key, default)
            
            # 空文字列や不正な値のチェック
            if value == "" and default is not None:
                return default
                
            return value
        except Exception:
            return default