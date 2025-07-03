import json
import os
import re
from typing import Dict, List
import google.generativeai as genai
from config import NOTE_FOLDER, GEMINI_API_KEY


class KeywordsReconstructor:
    def __init__(self, keywords_file="keywords.json",
                 reconstruction_prompt_file="keywords_reconstruction.md"):
        """
        キーワード再構成クラス

        Args:
            keywords_file: キーワードファイルのパス
            reconstruction_prompt_file: 再構成プロンプトファイルのパス
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.keywords_file = os.path.join(script_dir, keywords_file)
        self.prompt_file = os.path.join(script_dir, reconstruction_prompt_file)
        self.note_folder = NOTE_FOLDER

        # Gemini API設定
        genai.configure(api_key=GEMINI_API_KEY)

    def load_keywords(self) -> Dict:
        """現在のkeywords.jsonを読み込み"""
        try:
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"キーワードファイルの読み込みエラー: {e}")
            return {}

    def load_reconstruction_prompt(self) -> str:
        """再構成プロンプトを読み込み"""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"プロンプトファイルの読み込みエラー: {e}")
            return ""

    def create_reconstruction_prompt(self, keywords_data: Dict) -> str:
        """再構成用プロンプトを作成"""
        prompt_template = self.load_reconstruction_prompt()
        if not prompt_template:
            print("プロンプトテンプレートが読み込めません")
            return ""

        # keywords_dataをJSONに変換
        keywords_json = json.dumps(keywords_data, ensure_ascii=False, indent=2)

        # プロンプトテンプレートの{JSON_SECTION}を置換
        prompt = prompt_template.replace("{JSON_SECTION}", keywords_json)
        return prompt

    def get_available_models(self) -> List[str]:
        """利用可能なモデルを確認"""
        try:
            models = genai.list_models()
            available_models = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name.replace('models/', '')
                    available_models.append(model_name)
            return available_models
        except Exception as e:
            print(f"利用可能なモデルの取得エラー: {e}")
            return []

    def call_gemini_api(self, prompt: str,
                        model_name="gemini-2.5-flash") -> str:
        """Gemini APIを呼び出してJSON再構成を実行"""
        try:
            # 利用可能なモデルを確認
            available_models = self.get_available_models()

            if model_name not in available_models:
                # gemini-2.5-flashが見つからない場合の代替
                fallback_models = ["gemini-1.5-flash", "gemini-1.5-pro",
                                   "gemini-pro"]
                for fallback_model in fallback_models:
                    if fallback_model in available_models:
                        print(f"モデル '{model_name}' が見つからないため、"
                              f"'{fallback_model}' を使用します。")
                        model_name = fallback_model
                        break
                else:
                    print("エラー: 利用可能なモデルが見つかりません。")
                    return ""

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            if response.text:
                return response.text.strip()
            else:
                print("APIからの応答が空です")
                return ""

        except Exception as e:
            print(f"Gemini API呼び出しエラー: {e}")
            return ""

    def parse_json_response(self, response_text: str) -> Dict:
        """APIレスポンスからJSONを抽出・解析"""
        try:
            # レスポンステキストからJSONブロックを抽出
            # マークダウンコードブロックや余分なテキストを除去
            lines = response_text.strip().split('\n')
            json_lines = []
            in_json_block = False

            for line in lines:
                # JSON開始を検出
                if line.strip().startswith('{'):
                    in_json_block = True
                    json_lines.append(line)
                elif in_json_block:
                    json_lines.append(line)
                    # JSON終了を検出
                    if (line.strip().endswith('}') and
                            line.count('}') >= line.count('{')):
                        break

            if not json_lines:
                # 直接JSON解析を試行
                return json.loads(response_text)

            json_text = '\n'.join(json_lines)
            return json.loads(json_text)

        except json.JSONDecodeError as e:
            print(f"JSON解析エラー: {e}")
            print(f"レスポンステキスト: {response_text}")
            return {}
        except Exception as e:
            print(f"レスポンス解析エラー: {e}")
            return {}

    def update_keywords_file(self, new_keywords_data: Dict) -> bool:
        """keywords.jsonを更新"""
        try:
            with open(self.keywords_file, 'w', encoding='utf-8') as f:
                json.dump(new_keywords_data, f, ensure_ascii=False, indent=2)
            print("keywords.jsonを更新しました")
            return True
        except Exception as e:
            print(f"キーワードファイル更新エラー: {e}")
            return False

    def get_markdown_files(self) -> List[str]:
        """NOTE_FOLDER内のMarkdownファイル一覧を取得"""
        markdown_files = []

        if not os.path.exists(self.note_folder):
            print(f"ノートフォルダが見つかりません: {self.note_folder}")
            return markdown_files

        for root, dirs, files in os.walk(self.note_folder):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))

        return markdown_files

    def update_note_keywords(self, file_path: str, deleted_keywords: List[str],
                             aliases: Dict[str, str]) -> bool:
        """ノートファイル内のキーワードを更新"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            modified = False

            # 削除対象キーワードを除去
            for deleted_keyword in deleted_keywords:
                pattern = rf'#\b{re.escape(deleted_keyword)}\b'
                if re.search(pattern, content):
                    content = re.sub(pattern, '', content)
                    modified = True
                    filename = os.path.basename(file_path)
                    print(f"削除: {deleted_keyword} from {filename}")

            # エイリアスの統一（略称→正式名称）
            for full_name, alias in aliases.items():
                # 略称を正式名称に置換
                pattern = rf'#\b{re.escape(alias)}\b'
                if re.search(pattern, content):
                    content = re.sub(pattern, f'#{full_name}', content)
                    modified = True
                    filename = os.path.basename(file_path)
                    print(f"置換: #{alias} → #{full_name} in {filename}")

            # 変更があった場合のみファイルを更新
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            print(f"ノートファイル更新エラー {file_path}: {e}")
            return False

    def update_all_notes(self, deleted_keywords: List[str],
                         aliases: Dict[str, str]) -> int:
        """全てのノートファイルを更新"""
        markdown_files = self.get_markdown_files()
        updated_count = 0

        print(f"対象ファイル数: {len(markdown_files)}")

        for file_path in markdown_files:
            if self.update_note_keywords(file_path, deleted_keywords, aliases):
                updated_count += 1

        print(f"更新されたファイル数: {updated_count}")
        return updated_count

    def reconstruct_keywords(self) -> bool:
        """キーワード再構成のメイン処理"""
        print("キーワード再構成を開始します...")

        # 1. 現在のキーワードデータを読み込み
        current_keywords = self.load_keywords()
        if not current_keywords:
            print("キーワードデータが読み込めませんでした")
            return False

        # 2. 再構成プロンプトを作成
        prompt = self.create_reconstruction_prompt(current_keywords)
        if not prompt:
            print("プロンプトが作成できませんでした")
            return False

        print("Gemini APIを呼び出してキーワードを再構成中...")

        # 3. Gemini APIを呼び出し
        response = self.call_gemini_api(prompt)
        if not response:
            print("APIからの応答が取得できませんでした")
            return False

        # 4. JSONレスポンスを解析
        new_keywords_data = self.parse_json_response(response)
        if not new_keywords_data:
            print("JSON解析に失敗しました")
            return False

        # 5. deletedキーワードを取得
        deleted_keywords = new_keywords_data.get("deleted", [])

        # 6. aliasesを取得
        new_aliases = new_keywords_data.get("aliases", {})

        # 7. deletedフィールドを除去してからkeywords.jsonを更新
        if "deleted" in new_keywords_data:
            del new_keywords_data["deleted"]

        # 8. keywords.jsonを更新
        if not self.update_keywords_file(new_keywords_data):
            print("keywords.jsonの更新に失敗しました")
            return False

        # 9. 全ノートファイルを更新
        if deleted_keywords or new_aliases:
            print("ノートファイルを更新中...")
            self.update_all_notes(deleted_keywords, new_aliases)

        print("キーワード再構成が完了しました")
        return True


def main():
    """単体実行用のメイン関数"""
    reconstructor = KeywordsReconstructor()
    success = reconstructor.reconstruct_keywords()

    if success:
        print("✅ キーワード再構成が正常に完了しました")
    else:
        print("❌ キーワード再構成に失敗しました")
        exit(1)


if __name__ == "__main__":
    main()
