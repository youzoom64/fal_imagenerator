# lyrics_image_generator.py
import json
import os
import re
import fal_client
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

class LyricsImageGenerator:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        
        # API設定
        fal_client.api_key = self.config["api_key"]
        from openai import OpenAI
        self.openai_client = OpenAI(api_key=self.config["openai_api_key"])
        
        # 歌詞パート
        self.lyrics_parts = ["intro", "verse1", "pre_chorus", "chorus", "verse2", "bridge", "outro"]
        
    def DEBUGLOG(self, message: str, level: str = "INFO"):
        """統一デバッグログ関数"""
        if self.config.get("debug_enabled", False):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def find_latest_lyrics_files(self, lyrics_dir: str) -> Tuple[Optional[str], Optional[str]]:
        """最新のオープニングとエンディングファイルを検索"""
        opening_files = []
        ending_files = []
        
        for filename in os.listdir(lyrics_dir):
            file_path = os.path.join(lyrics_dir, filename)
            if filename.startswith("lyrics_opening_") and filename.endswith(".json"):
                opening_files.append((os.path.getctime(file_path), file_path))
            elif filename.startswith("lyrics_ending_") and filename.endswith(".json"):
                ending_files.append((os.path.getctime(file_path), file_path))
        
        # 最新ファイルを取得
        latest_opening = sorted(opening_files, reverse=True)[0][1] if opening_files else None
        latest_ending = sorted(ending_files, reverse=True)[0][1] if ending_files else None
        
        if latest_opening:
            self.DEBUGLOG(f"最新オープニング: {os.path.basename(latest_opening)}")
        if latest_ending:
            self.DEBUGLOG(f"最新エンディング: {os.path.basename(latest_ending)}")
            
        return latest_opening, latest_ending
    
    def translate_to_english(self, text: str) -> str:
        """テキストを英語に翻訳"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "日本語の歌詞を自然で美しい英語に翻訳してください。"},
                    {"role": "user", "content": f"以下を英語に翻訳: {text}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.DEBUGLOG(f"翻訳エラー: {e}", "ERROR")
            return text
    
    def translate_lyrics_json(self, lyrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """歌詞JSON全体を英語化"""
        english_lyrics = {
            "title": self.translate_to_english(lyrics_data.get("title", "")),
            "lyrics": {}
        }
        
        for part in self.lyrics_parts:
            if part in lyrics_data.get("lyrics", {}):
                lyrics_lines = lyrics_data["lyrics"][part]
                if isinstance(lyrics_lines, list):
                    english_lyrics["lyrics"][part] = [self.translate_to_english(line) for line in lyrics_lines]
                else:
                    english_lyrics["lyrics"][part] = self.translate_to_english(lyrics_lines)
        
        return english_lyrics
    
    def create_image_prompt(self, lyrics_lines: List[str], title: str, part_name: str) -> str:
        """歌詞から画像プロンプト生成"""
        lyrics_text = " ".join(lyrics_lines) if isinstance(lyrics_lines, list) else lyrics_lines
        return f"Beautiful artistic image inspired by '{title}', {part_name}: {lyrics_text}. Cinematic, emotional, high quality artwork."
    
    def generate_image(self, prompt: str, filename: str) -> Optional[str]:
        """fal AIで画像生成"""
        try:
            result = fal_client.subscribe(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": prompt,
                    "image_size": "landscape_4_3",
                    "num_inference_steps": 4,
                    "guidance_scale": 3.5,
                    "num_images": 1,
                    "enable_safety_checker": False
                }
            )
            
            if result and 'images' in result and result['images']:
                image_url = result['images'][0]['url']
                self.DEBUGLOG(f"画像生成完了: {filename}")
                return image_url
            else:
                self.DEBUGLOG(f"画像生成失敗: {filename}", "ERROR")
                return None
                
        except Exception as e:
            self.DEBUGLOG(f"画像生成エラー ({filename}): {e}", "ERROR")
            return None
    
    def download_image(self, image_url: str, file_path: str) -> bool:
        """画像ダウンロード"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.DEBUGLOG(f"画像保存: {file_path}")
            return True
            
        except Exception as e:
            self.DEBUGLOG(f"ダウンロードエラー: {e}", "ERROR")
            return False
    
    def process_lyrics_file(self, file_path: str, song_type: str, base_dir: str) -> Tuple[bool, Optional[str]]:
        """歌詞ファイル処理 - 戻り値: (成功/失敗, 画像フォルダパス)"""
        try:
            # 歌詞読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                lyrics_data = json.load(f)
            
            self.DEBUGLOG(f"{song_type} 処理開始: {os.path.basename(file_path)}")
            
            # 英語化
            english_lyrics = self.translate_lyrics_json(lyrics_data)
            
            # 英語版JSON保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            english_file = os.path.join(base_dir, f"en_lyrics_{song_type}_{timestamp}.json")
            
            with open(english_file, 'w', encoding='utf-8') as f:
                json.dump(english_lyrics, f, ensure_ascii=False, indent=2)
            
            self.DEBUGLOG(f"英語版保存: {os.path.basename(english_file)}")
            
            # 画像ディレクトリ作成
            image_dir = os.path.join(base_dir, f"{song_type}_image")
            os.makedirs(image_dir, exist_ok=True)
            
            # 各パート画像生成
            title = english_lyrics.get("title", "Untitled")
            lyrics = english_lyrics.get("lyrics", {})
            
            for part in self.lyrics_parts:
                if part in lyrics:
                    prompt = self.create_image_prompt(lyrics[part], title, part)
                    image_url = self.generate_image(prompt, f"{song_type}_{part}")
                    
                    if image_url:
                        image_path = os.path.join(image_dir, f"{part}.png")
                        self.download_image(image_url, image_path)
            
            return True, image_dir
            
        except Exception as e:
            self.DEBUGLOG(f"ファイル処理エラー: {e}", "ERROR")
            return False, None
    
    def process_directory(self, lyrics_dir: str) -> Tuple[bool, List[str]]:
        """ディレクトリ処理 - 戻り値: (成功/失敗, 作成された画像フォルダパスのリスト)"""
        try:
            # 最新ファイル検索
            opening_file, ending_file = self.find_latest_lyrics_files(lyrics_dir)
            
            if not opening_file or not ending_file:
                self.DEBUGLOG(f"ファイルが見つからない: {lyrics_dir}", "WARNING")
                return False, []
            
            # 各ファイル処理
            created_folders = []
            success = True
            
            for song_type, file_path in [("opening", opening_file), ("ending", ending_file)]:
                file_success, image_folder = self.process_lyrics_file(file_path, song_type, lyrics_dir)
                if file_success and image_folder:
                    created_folders.append(image_folder)
                else:
                    success = False
            
            return success, created_folders
            
        except Exception as e:
            self.DEBUGLOG(f"ディレクトリエラー: {e}", "ERROR")
            return False, []
    
    def process_all_directories(self) -> Tuple[bool, List[str]]:
        """全ディレクトリ処理 - 戻り値: (成功/失敗, 作成された全画像フォルダパスのリスト)"""
        base_dir = self.config["output_directory"]
        success_count = 0
        total_count = 0
        all_created_folders = []
        
        for root, dirs, files in os.walk(base_dir):
            has_opening = any(f.startswith("lyrics_opening_") and f.endswith(".json") for f in files)
            has_ending = any(f.startswith("lyrics_ending_") and f.endswith(".json") for f in files)
            
            if has_opening and has_ending:
                total_count += 1
                self.DEBUGLOG(f"処理開始: {root}")
                
                dir_success, created_folders = self.process_directory(root)
                if dir_success:
                    success_count += 1
                    all_created_folders.extend(created_folders)
                    self.DEBUGLOG(f"処理完了: {root}")
                else:
                    self.DEBUGLOG(f"処理失敗: {root}", "ERROR")
        
        self.DEBUGLOG(f"結果: {success_count}/{total_count} 成功")
        overall_success = success_count > 0
        
        return overall_success, all_created_folders

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python lyrics_image_generator.py <directory>  # 特定ディレクトリ")
        print("  python lyrics_image_generator.py --all        # 全ディレクトリ")
        return
    
    generator = LyricsImageGenerator()
    
    if sys.argv[1] == "--all":
        success, created_folders = generator.process_all_directories()
        if success:
            print("全処理完了")
            print("作成されたフォルダ:")
            for folder in created_folders:
                print(f"  {folder}")
        else:
            print("処理失敗")
    else:
        lyrics_dir = sys.argv[1]
        if not os.path.exists(lyrics_dir):
            print(f"ディレクトリが見つかりません: {lyrics_dir}")
            return
        
        success, created_folders = generator.process_directory(lyrics_dir)
        if success:
            print("処理完了")
            print("作成されたフォルダ:")
            for folder in created_folders:
                print(f"  {folder}")
        else:
            print("処理失敗")

if __name__ == "__main__":
    main()