"""システム操作関連のユーティリティ"""
import subprocess
import platform
import os

def open_folder(folder_path):
    """フォルダを開く"""
    try:
        abs_path = os.path.abspath(folder_path)
        
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{abs_path}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", abs_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", abs_path])
        
        return True
    except Exception as e:
        return False