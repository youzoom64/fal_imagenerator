"""デバッグログ用ユーティリティ"""
import logging
import os
from datetime import datetime

class DebugLogger:
    def __init__(self, log_file="debug.log", level=logging.DEBUG):
        self.logger = logging.getLogger("ImageGeneratorDebug")
        self.logger.setLevel(level)
        
        # すでにハンドラーが設定されている場合はスキップ
        if not self.logger.handlers:
            # ファイルハンドラー
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            
            # コンソールハンドラー
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # フォーマッター
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """デバッグレベルのログ"""
        self.logger.debug(message)
    
    def info(self, message):
        """情報レベルのログ"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告レベルのログ"""
        self.logger.warning(message)
    
    def error(self, message):
        """エラーレベルのログ"""
        self.logger.error(message)
    
    def exception(self, message):
        """例外ログ（スタックトレース付き）"""
        self.logger.exception(message)
    
    def log_function_entry(self, func_name, **kwargs):
        """関数エントリのログ"""
        args_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.debug(f">>> {func_name}({args_str}) 開始")
    
    def log_function_exit(self, func_name, result=None):
        """関数終了のログ"""
        if result is not None:
            self.debug(f"<<< {func_name} 終了 -> {result}")
        else:
            self.debug(f"<<< {func_name} 終了")
    
    def log_event(self, event_name, **data):
        """イベントログ"""
        data_str = ", ".join([f"{k}={v}" for k, v in data.items()])
        self.info(f"EVENT: {event_name} - {data_str}")

# グローバルインスタンス
debug_logger = DebugLogger()