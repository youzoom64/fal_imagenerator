"""エントリーポイント"""
import sys
import os

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import FluxGUIApp

def main():
    """メイン関数"""
    try:
        app = FluxGUIApp()
        app.run()
    except Exception as e:
        print(f"起動エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()