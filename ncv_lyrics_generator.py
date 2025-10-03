import sqlite3
import json
import os
import re
import openai
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

class LyricsGenerator:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.config_path = config_path
        
    
    def DEBUGLOG(self, message: str, level: str = "INFO"):
        """統一デバッグログ関数"""
        if self.config.get("debug_enabled", False):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.DEBUGLOG(f"設定ファイルが見つかりません: {config_path}", "ERROR")
            raise
        except json.JSONDecodeError as e:
            self.DEBUGLOG(f"設定ファイルの解析に失敗: {e}", "ERROR")
            raise
    
    def save_config_with_history(self, new_config: Dict[str, Any]):
        """設定を履歴付きで保存する統一関数"""
        # 現在の設定を読み込み
        current_config = self.load_config(self.config_path)
        
        # 変更箇所のみを更新
        for key, value in new_config.items():
            current_config[key] = value
        
        # 履歴情報を追加
        if "config_history" not in current_config:
            current_config["config_history"] = []
        
        current_config["config_history"].append({
            "timestamp": datetime.now().isoformat(),
            "changes": new_config
        })
        
        # 保存
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, ensure_ascii=False, indent=2)
        
        self.config = current_config
        self.DEBUGLOG(f"設定を保存しました: {list(new_config.keys())}")
    
    def get_user_data(self, user_id: str) -> Optional[Tuple[str, str, str, str, Dict[str, Any]]]:
        """データベースからuser_idの最新データを取得"""
        try:
            conn = sqlite3.connect(self.config["database_path"])
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # ai_analysesテーブルから最新のレコードを取得
            query = """
            SELECT * FROM ai_analyses 
            WHERE user_id = ? 
            ORDER BY analysis_date DESC 
            LIMIT 1
            """
            
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                self.DEBUGLOG(f"user_id {user_id} のデータが見つかりません", "WARNING")
                return None
            
            # 必要なデータを抽出
            analysis_text = row["analysis_result"] or ""
            broadcast_title = row["broadcast_title"] or ""
            user_name = row["user_name"] or f"user_{user_id}"
            lv_value = row["broadcast_lv_id"] or "unknown_lv"  # 追加
            
            # その他のカラムも取得
            other_data = {key: row[key] for key in row.keys() 
                        if key not in ["analysis_result", "broadcast_title", "user_name", "broadcast_lv_id"]}
            
            self.DEBUGLOG(f"データ取得完了: user_id={user_id}, user_name={user_name}, lv={lv_value}")
            
            conn.close()
            return analysis_text, broadcast_title, user_name, lv_value, other_data
            
        except sqlite3.Error as e:
            self.DEBUGLOG(f"データベースエラー: {e}", "ERROR")
            return None

            
    def remove_html_tags(self, text: str) -> str:
        """HTMLタグを除去"""
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 複数の空白や改行を整理
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
   
    def generate_lyrics_prompt(self, analysis_text: str, broadcast_title: str, user_name: str, prompt_type: str = "opening") -> str:
        """ChatGPT用のプロンプトを生成"""
        clean_text = self.remove_html_tags(analysis_text)
        
        # config.jsonから指定されたタイプのプロンプトテンプレートを取得
        prompt_template = self.config["prompts"][prompt_type]["user_prompt_template"]
        
        # テンプレートに値を代入
        prompt = prompt_template.format(
            broadcast_title=broadcast_title,
            user_name=user_name,
            clean_text=clean_text
        )
        
        return prompt

    def call_chatgpt_api(self, prompt: str, prompt_type: str = "opening") -> Optional[Dict[str, Any]]:
        """ChatGPT APIを呼び出し"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config["openai_api_key"])
            
            # config.jsonから指定されたタイプのシステムプロンプトを取得
            system_prompt = self.config["prompts"][prompt_type]["system_prompt"]
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            self.DEBUGLOG(f"ChatGPT API応答取得完了 ({prompt_type}) (文字数: {len(content)})")
            
            # JSONとして解析を試行
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # JSONブロックを抽出する試行
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                
                # 直接JSONとして解析を試行
                return json.loads(content)
                
        except Exception as e:
            self.DEBUGLOG(f"API エラー ({prompt_type}): {e}", "ERROR")
            return None

    def generate_lyrics_for_user(self, user_id: str, prompt_type: str = "opening") -> bool:
        """指定されたuser_idの歌詞を生成"""
        self.DEBUGLOG(f"歌詞生成開始 ({prompt_type}): user_id={user_id}")
        
        # 1. データベースからデータを取得
        user_data = self.get_user_data(user_id)
        if not user_data:
            return False
        
        analysis_text, broadcast_title, user_name, lv_value, other_data = user_data  # 修正
        
        if not analysis_text.strip():
            self.DEBUGLOG("analysis_textが空です", "WARNING")
            return False
        
        # 2. プロンプトを生成
        prompt = self.generate_lyrics_prompt(analysis_text, broadcast_title, user_name, prompt_type)
        
        # 3. ChatGPT APIを呼び出し
        lyrics_data = self.call_chatgpt_api(prompt, prompt_type)
        if not lyrics_data:
            return False
        
        # 4. 結果を保存
        success = self.save_lyrics_response(user_name, user_id, lyrics_data, prompt_type, lv_value, broadcast_title)  # 修正
        
        if success:
            self.DEBUGLOG(f"歌詞生成完了 ({prompt_type}): user_id={user_id}")
        
        return success
    
    def save_lyrics_response(self, user_name: str, user_id: str, lyrics_data: Dict[str, Any], prompt_type: str = "opening", lv_value: str = "", broadcast_title: str = "") -> bool:
        """歌詞応答を保存"""
        try:
            # 出力ディレクトリの作成: {lv_value}_{broadcast_title}/ユーザー名_ユーザーID/
            base_dir = self.config["output_directory"]
            
            # サブディレクトリ名を作成（ファイル名として無効な文字を除去）
            safe_broadcast_title = re.sub(r'[<>:"/\\|?*]', '_', broadcast_title)
            sub_dir = f"{lv_value}_{safe_broadcast_title}"
            user_dir = f"{user_name}_{user_id}"
            
            full_path = os.path.join(base_dir, sub_dir, user_dir)
            os.makedirs(full_path, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if prompt_type == "both":
                # 両方の場合は別々のファイルに保存
                for song_type in ["opening", "ending"]:
                    if song_type in lyrics_data:
                        filename = f"lyrics_{song_type}_{timestamp}.json"
                        file_path = os.path.join(full_path, filename)
                        
                        # ChatGPTから返ってきたJSONをそのまま保存
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(lyrics_data[song_type], f, ensure_ascii=False, indent=2)
                        
                        self.DEBUGLOG(f"歌詞ファイルを保存: {file_path}")
            else:
                # 単体の場合
                filename = f"lyrics_{prompt_type}_{timestamp}.json"
                file_path = os.path.join(full_path, filename)
                
                # ChatGPTから返ってきたJSONをそのまま保存
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(lyrics_data, f, ensure_ascii=False, indent=2)
                
                self.DEBUGLOG(f"歌詞ファイルを保存: {file_path}")
            
            return True
            
        except Exception as e:
            self.DEBUGLOG(f"ファイル保存エラー: {e}", "ERROR")
            return False

def main():
    """メイン実行関数"""
    if len(os.sys.argv) < 2:
        print("使用方法: python ncv_lyrics_generator.py <user_id> [opening|ending|both]")
        return
    
    user_id = os.sys.argv[1]
    prompt_type = os.sys.argv[2] if len(os.sys.argv) > 2 else "both"
    
    if prompt_type not in ["opening", "ending", "both"]:
        print("prompt_typeは 'opening' または 'ending' または 'both' を指定してください")
        return
    
    try:
        generator = LyricsGenerator()
        success = generator.generate_lyrics_for_user(user_id, prompt_type)
        
        if success:
            print(f"歌詞生成が完了しました: user_id={user_id}, type={prompt_type}")
        else:
            print(f"歌詞生成に失敗しました: user_id={user_id}, type={prompt_type}")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()