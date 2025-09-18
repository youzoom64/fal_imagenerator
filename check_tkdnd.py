
"""tkdnd診断スクリプト（修正版）"""
import tkinter as tk
import os
import sys

def check_tkdnd():
    print("=== tkdnd診断開始 ===")
    
    # システム情報
    import platform
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # tkinterdnd2の確認
    try:
        import tkinterdnd2
        
        # バージョン情報（複数の方法で取得を試行）
        version = "不明"
        try:
            version = tkinterdnd2.__version__
        except AttributeError:
            try:
                # pipでインストール情報を確認
                import pkg_resources
                version = pkg_resources.get_distribution('tkinterdnd2').version
            except:
                try:
                    # importlib.metadataを使用（Python 3.8+）
                    from importlib import metadata
                    version = metadata.version('tkinterdnd2')
                except:
                    version = "バージョン取得不可"
        
        print(f"✅ tkinterdnd2: インストール済み（バージョン: {version}）")
        print(f"   パス: {tkinterdnd2.__file__}")
        
        # tkdndディレクトリの確認
        tkdnd_dir = os.path.dirname(tkinterdnd2.__file__)
        print(f"   ディレクトリ: {tkdnd_dir}")
        
        # ディレクトリ内容を確認
        try:
            files = os.listdir(tkdnd_dir)
            print(f"   ディレクトリ内容: {len(files)}個のファイル/フォルダ")
            
            # tkdnd関連ファイルを探す
            tkdnd_related = [f for f in files if 'tkdnd' in f.lower()]
            if tkdnd_related:
                print(f"   tkdnd関連: {tkdnd_related}")
            
            # .tclファイルを探す
            tcl_files = [f for f in files if f.endswith('.tcl')]
            if tcl_files:
                print(f"   .tclファイル: {tcl_files}")
            
        except Exception as e:
            print(f"   ディレクトリ確認エラー: {e}")
        
        # サブディレクトリも確認
        tkdnd_files = []
        for root, dirs, files in os.walk(tkdnd_dir):
            for file in files:
                if 'tkdnd' in file.lower() or file.endswith('.tcl'):
                    relative_path = os.path.relpath(os.path.join(root, file), tkdnd_dir)
                    tkdnd_files.append(relative_path)
        
        print(f"   関連ファイル総数: {len(tkdnd_files)}個")
        for i, file in enumerate(tkdnd_files):
            if i < 5:  # 最初の5個を表示
                print(f"     {file}")
            elif i == 5:
                print(f"     ... (他に{len(tkdnd_files)-5}個)")
                break
        
    except ImportError as e:
        print(f"❌ tkinterdnd2: インポートエラー - {e}")
        print("\n修復方法:")
        print("  pip install tkinterdnd2")
        return False
    
    # Tkinterでのテスト
    print("\n=== Tkinterテスト ===")
    try:
        root = tk.Tk()
        root.withdraw()  # ウィンドウを非表示
        print("✅ Tkinterウィンドウ作成成功")
        
        # tkdndパッケージのテスト
        try:
            print("tkdndパッケージ要求を試行...")
            result = root.tk.call('package', 'require', 'tkdnd')
            print(f"✅ tkdndパッケージ成功: {result}")
            root.destroy()
            return True
        except tk.TclError as tcl_error:
            print(f"❌ tkdndパッケージエラー: {tcl_error}")
            
            # 詳細診断
            print("\n=== 手動修復試行 ===")
            
            try:
                # tkdnd関連モジュールの詳細確認
                try:
                    import tkinterdnd2.tkdnd
                    print("✅ tkinterdnd2.tkdndモジュール発見")
                    tkdnd_module_path = os.path.dirname(tkinterdnd2.tkdnd.__file__)
                    print(f"   パス: {tkdnd_module_path}")
                except Exception as module_error:
                    print(f"❌ tkinterdnd2.tkdndモジュールエラー: {module_error}")
                    tkdnd_module_path = tkdnd_dir
                
                # 可能な.tclファイルの場所をすべて確認
                possible_tcl_locations = [
                    os.path.join(tkdnd_dir, "tkdnd.tcl"),
                    os.path.join(tkdnd_dir, "tkdnd", "tkdnd.tcl"),
                    os.path.join(tkdnd_module_path, "tkdnd.tcl"),
                    os.path.join(tkdnd_module_path, "tkdnd", "tkdnd.tcl")
                ]
                
                print("tkdnd.tclファイルを探索中...")
                tcl_file_found = None
                for tcl_location in possible_tcl_locations:
                    print(f"  チェック: {tcl_location}")
                    if os.path.exists(tcl_location):
                        tcl_file_found = tcl_location
                        print(f"  ✅ 発見: {tcl_location}")
                        break
                    else:
                        print(f"  ❌ 見つからず")
                
                if tcl_file_found:
                    try:
                        print(f"\ntkdnd.tcl手動読み込み試行: {tcl_file_found}")
                        # Tclファイルのパスを正規化（Windowsパス問題対応）
                        normalized_path = tcl_file_found.replace('\\', '/')
                        root.tk.eval(f'source "{normalized_path}"')
                        print("✅ tkdnd.tcl手動読み込み成功")
                        
                        # 再度パッケージテスト
                        result2 = root.tk.call('package', 'require', 'tkdnd')
                        print(f"✅ tkdndパッケージ（手動読み込み後）: {result2}")
                        root.destroy()
                        return True
                    except tk.TclError as manual_error:
                        print(f"❌ 手動読み込みエラー: {manual_error}")
                    except Exception as unexpected_error:
                        print(f"❌ 予期しないエラー: {unexpected_error}")
                else:
                    print("❌ tkdnd.tclファイルが見つかりません")
                    
            except Exception as manual_error:
                print(f"❌ 手動診断中にエラー: {manual_error}")
        
        root.destroy()
        
    except Exception as tk_error:
        print(f"❌ Tkinterテストエラー: {tk_error}")
    
    return False

def show_repair_instructions():
    print("\n=== 修復手順 ===")
    print("🔧 以下の方法を順番に試してください:")
    print()
    print("方法1: tkinterdnd2の完全再インストール")
    print("  pip uninstall tkinterdnd2 -y")
    print("  pip cache purge")
    print("  pip install tkinterdnd2 --force-reinstall --no-cache-dir")
    print()
    print("方法2: 特定バージョンのインストール")
    print("  pip uninstall tkinterdnd2 -y")  
    print("  pip install tkinterdnd2==0.3.0")
    print()
    print("方法3: conda使用（推奨）")
    print("  conda install -c conda-forge tkinterdnd2")
    print()
    print("方法4: 代替ライブラリ（最終手段）")
    print("  pip install tkdnd")
    print()
    print("それでも解決しない場合:")
    print("  - Pythonとtkinterの再インストール")
    print("  - 仮想環境の再作成")

if __name__ == "__main__":
    try:
        success = check_tkdnd()
        
        print(f"\n=== 診断結果: {'✅ 成功' if success else '❌ 失敗'} ===")
        
        if success:
            print("🎉 tkdnd機能が正常に動作します！")
            print("D&D機能が使用可能です。")
            print("\nアプリケーションでD&D機能をテストしてください:")
            print("  python main.py")
        else:
            print("⚠️ tkdnd機能に問題があります。")
            show_repair_instructions()
            
    except Exception as e:
        print(f"❌ 診断スクリプト実行エラー: {e}")
        import traceback
        traceback.print_exc()