"""新機能のテストスクリプト"""
import os
import sys
import tkinter as tk

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_prompt_history():
    """プロンプト履歴機能のテスト"""
    print("🧪 プロンプト履歴機能テスト開始")
    
    try:
        from src.ui.components.prompt_history_window import PromptHistoryWindow
        from src.ui.components.prompt_frame import PromptFrame
        from src.core.config_manager import ConfigManager
        
        root = tk.Tk()
        root.withdraw()  # ウィンドウを隠す
        
        config_manager = ConfigManager()
        frame = tk.Frame(root)
        prompt_frame = PromptFrame(frame, config_manager)
        
        history_window = PromptHistoryWindow(root, prompt_frame)
        
        # テストデータ追加
        history_window.add_to_history("Test prompt 1", "Test negative 1")
        history_window.add_to_history("Test prompt 2", "")
        
        print("✅ プロンプト履歴機能テスト成功")
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ プロンプト履歴機能テスト失敗: {e}")
        return False

def test_config_manager():
    """設定管理機能のテスト"""
    print("🧪 設定管理機能テスト開始")
    
    try:
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager("test_config.json")
        
        # テスト設定
        config.set("test_key", "test_value")
        config.set("test_number", 42)
        config.safe_set("test_safe", 3.14)
        
        # 値の確認
        assert config.get("test_key") == "test_value"
        assert config.get("test_number") == 42
        assert config.safe_get("test_safe") == 3.14
        
        # ファイルクリーンアップ
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        
        print("✅ 設定管理機能テスト成功")
        return True
        
    except Exception as e:
        print(f"❌ 設定管理機能テスト失敗: {e}")
        return False

def test_preset_manager():
    """プリセット管理機能のテスト"""
    print("🧪 プリセット管理機能テスト開始")
    
    try:
        from src.ui.components.preset_manager_window import PresetManagerWindow
        
        root = tk.Tk()
        root.withdraw()  # ウィンドウを隠す
        
        # モックのメインウィンドウ
        class MockMainWindow:
            def __init__(self):
                self.current_mode = "text-to-image"
        
        mock_main = MockMainWindow()
        preset_manager = PresetManagerWindow(root, mock_main)
        
        # テストプリセットデータ
        test_preset = {
            "mode": "text-to-image",
            "prompt": "Test preset prompt",
            "inference_steps": 28
        }
        
        preset_manager.presets["test_preset"] = test_preset
        preset_manager.save_presets()
        
        # データの確認
        loaded_presets = preset_manager.load_presets()
        assert "test_preset" in loaded_presets
        
        # テストファイルクリーンアップ
        if os.path.exists("presets.json"):
            os.remove("presets.json")
        
        print("✅ プリセット管理機能テスト成功")
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ プリセット管理機能テスト失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 新機能テスト実行開始\n")
    
    tests = [
        test_config_manager,
        test_prompt_history,
        test_preset_manager
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"📊 テスト結果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 すべてのテストが成功しました！")
        print("\n💡 次の手順:")
        print("1. python main.py でアプリケーションを起動")
        print("2. プロンプトフレームの「📚 履歴」ボタンをクリック")
        print("3. 「⚙️ プリセット管理」ボタンでプリセット機能をテスト")
        print("4. 設定変更が自動保存されることを確認")
    else:
        print("⚠️ 一部のテストが失敗しました。エラーメッセージを確認してください。")