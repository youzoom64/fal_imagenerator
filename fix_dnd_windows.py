"""Windows用tkdnd修正スクリプト（完全版）"""
import tkinter as tk
import os
import glob
import shutil

def find_all_tkdnd_files():
    """すべてのtkdnd関連ファイルを探す"""
    try:
        import tkinterdnd2
        base_dir = os.path.dirname(tkinterdnd2.__file__)
        print(f"tkinterdnd2ベースディレクトリ: {base_dir}")
        
        # すべてのtkdnd.tclファイルを再帰的に探す
        tcl_files = []
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file == 'tkdnd.tcl':
                    full_path = os.path.join(root, file)
                    tcl_files.append(full_path)
        
        print(f"\n発見したtkdnd.tclファイル: {len(tcl_files)}個")
        for i, tcl_file in enumerate(tcl_files):
            print(f"  {i+1}. {tcl_file}")
        
        return tcl_files, base_dir
    
    except Exception as e:
        print(f"エラー: {e}")
        return [], ""

def test_tcl_files(tcl_files):
    """各tkdnd.tclファイルをテスト"""
    working_files = []
    
    for tcl_file in tcl_files:
        print(f"\nテスト中: {os.path.basename(os.path.dirname(tcl_file))}/tkdnd.tcl")
        
        try:
            root = tk.Tk()
            root.withdraw()
            
            # パスを正規化（Windowsパス問題対応）
            normalized_path = tcl_file.replace('\\', '/')
            
            # Tclファイルを読み込み
            root.tk.eval(f'source "{normalized_path}"')
            
            # tkdndパッケージを要求
            result = root.tk.call('package', 'require', 'tkdnd')
            print(f"  ✅ 成功: {result}")
            working_files.append(tcl_file)
            
            root.destroy()
            
        except Exception as e:
            print(f"  ❌ 失敗: {e}")
            try:
                root.destroy()
            except:
                pass
    
    return working_files

def create_windows_tkdnd_fix(base_dir, working_tcl_file):
    """Windows用の修正を適用"""
    try:
        # tkdndディレクトリ直下にtkdnd.tclをコピー
        tkdnd_dir = os.path.join(base_dir, 'tkdnd')
        target_tcl = os.path.join(tkdnd_dir, 'tkdnd.tcl')
        
        if not os.path.exists(target_tcl):
            print(f"\nWindows用修正: tkdnd.tclをコピー")
            print(f"  コピー元: {working_tcl_file}")
            print(f"  コピー先: {target_tcl}")
            
            shutil.copy2(working_tcl_file, target_tcl)
            print("  ✅ コピー完了")
            
            # 権限確認
            if os.path.exists(target_tcl):
                print("  ✅ ファイル配置確認")
                return target_tcl
            else:
                print("  ❌ ファイル配置失敗")
                return None
        else:
            print(f"\ntkdnd.tclは既に存在: {target_tcl}")
            return target_tcl
            
    except Exception as e:
        print(f"Windows用修正エラー: {e}")
        return None

def test_final_setup():
    """最終テスト"""
    print("\n=== 最終テスト ===")
    try:
        root = tk.Tk()
        root.withdraw()
        
        result = root.tk.call('package', 'require', 'tkdnd')
        print(f"✅ 最終テスト成功: {result}")
        
        # D&D機能のテスト
        from tkinterdnd2 import DND_FILES
        print("✅ DND_FILESインポート成功")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ 最終テスト失敗: {e}")
        try:
            root.destroy()
        except:
            pass
        return False

def main():
    print("=== Windows用tkdnd修正スクリプト ===")
    
    # Step 1: すべてのtkdnd.tclファイルを探す
    tcl_files, base_dir = find_all_tkdnd_files()
    
    if not tcl_files:
        print("❌ tkdnd.tclファイルが見つかりません")
        print("tkinterdnd2の再インストールが必要です:")
        print("  pip uninstall tkinterdnd2 -y")
        print("  pip install tkinterdnd2 --force-reinstall")
        return False
    
    # Step 2: 動作するtkdnd.tclファイルを特定
    print("\n=== tkdnd.tclファイルテスト ===")
    working_files = test_tcl_files(tcl_files)
    
    if not working_files:
        print("❌ 動作するtkdnd.tclファイルがありません")
        return False
    
    print(f"\n✅ 動作するファイル: {len(working_files)}個")
    for wf in working_files:
        print(f"  {wf}")
    
    # Step 3: Windows用修正を適用
    working_tcl = working_files[0]  # 最初の動作するファイルを使用
    fixed_tcl = create_windows_tkdnd_fix(base_dir, working_tcl)
    
    if not fixed_tcl:
        print("❌ Windows用修正に失敗")
        return False
    
    # Step 4: 最終テスト
    success = test_final_setup()
    
    if success:
        print("\n🎉 修正完了！D&D機能が使用可能になりました")
        print("アプリケーションを実行してテストしてください:")
        print("  python main.py")
        return True
    else:
        print("\n❌ 修正後のテストに失敗")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n代替案:")
            print("1. 仮想環境を再作成")
            print("2. conda install -c conda-forge tkinterdnd2")
            print("3. 別のD&Dライブラリを使用")
    except Exception as e:
        print(f"スクリプト実行エラー: {e}")
        import traceback
        traceback.print_exc()
