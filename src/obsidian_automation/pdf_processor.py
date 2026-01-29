import PyPDF2
import google.generativeai as genai
import os
from .keyword_manager import KeywordManager


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page_text = reader.pages[page_num].extract_text()
                # 不正な文字を処理
                if page_text:
                    # サロゲート文字やその他の問題のある文字を除去/置換
                    cleaned_text = clean_text(page_text)
                    text += cleaned_text
        return text
    except Exception as e:
        print(f"PDFからのテキスト抽出中にエラーが発生しました: {e}")
        return None


def clean_text(text):
    """テキストから不正な文字を除去し、UTF-8エンコーディング問題を解決"""
    if not text:
        return ""

    try:
        # サロゲート文字を除去
        text = text.encode('utf-8', errors='ignore').decode('utf-8')

        # 制御文字を除去（改行とタブは保持）
        import re
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # 連続する空白を単一のスペースに
        text = re.sub(r'\s+', ' ', text)

        # 前後の空白をトリミング
        text = text.strip()

        return text
    except Exception as e:
        print(f"テキストクリーニング中にエラーが発生しました: {e}")
        # フォールバック: ASCII文字のみを保持
        return ''.join(char for char in text if ord(char) < 128)

# 使用例:
# pdf_text = extract_text_from_pdf("path/to/your/document.pdf")
# if pdf_text:
#     print(pdf_text[:500]) # 最初の500文字を表示


def load_custom_prompt():
    """custom_prompt.mdからテンプレートを読み込む"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        prompt_path = os.path.join(project_root, "prompt", "custom_prompt.md")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # キーワードマネージャーからキーワードセクションを取得
        keyword_manager = KeywordManager()
        keywords_section = keyword_manager.create_keyword_prompt()

        # プレースホルダーを置き換え
        content = content.replace('{KEYWORDS_SECTION}', keywords_section)

        return content
    except Exception as e:
        print(f"custom_prompt.mdの読み込み中にエラーが発生しました: {e}")
        return None


def get_available_models():
    """利用可能なモデルを確認"""
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                # models/プレフィックスを除去してモデル名を取得
                model_name = model.name.replace('models/', '')
                available_models.append(model_name)
        return available_models
    except Exception as e:
        print(f"利用可能なモデルの取得中にエラーが発生しました: {e}")
        return []


def normalize_llm_text(markdown_text: str) -> str:
    """LLM出力内のLaTeX系やリテラル改行表記をMarkdownの改行に正規化する"""
    if not markdown_text:
        return markdown_text
    try:
        import re
        text = markdown_text
        # '\n'（バックスラッシュ+nのリテラル）を実際の改行へ
        text = text.replace('\\n', '\n')

        # プロンプト指示によりエスケープされたバックスラッシュを元に戻す (\\ -> \)
        text = text.replace('\\\\', '\\')

        # LaTeXの \newline を段落改行へ
        text = re.sub(r'\\newline\b', '\n\n', text)
        # 余分な空白の正規化（連続空行は2行に圧縮）
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    except Exception:
        return markdown_text


def summarize_text(text, model_name="gemini-2.5-flash"):
    try:
        # テキストを事前にクリーニング
        if text:
            text = clean_text(text)

        if not text:
            print("クリーニング後のテキストが空です。")
            return None

        # まず利用可能なモデルを確認
        available_models = get_available_models()

        # モデル名を確認し、必要に応じて調整
        if model_name not in available_models:
            # gemini-2.5-flashが見つからない場合、代替モデルを試す
            fallback_models = ["gemini-1.5-flash"]
            # fallback_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            for fallback_model in fallback_models:
                if fallback_model in available_models:
                    print(f"モデル '{model_name}' が見つからないため、"
                          f"'{fallback_model}' を使用します。")
                    model_name = fallback_model
                    break
            else:
                print("エラー: 利用可能なモデルが見つかりません。")
                if available_models:
                    print(f"利用可能なモデル: {available_models}")
                return None

        model = genai.GenerativeModel(model_name)

        # custom_prompt.mdからテンプレートを読み込み
        custom_prompt = load_custom_prompt()
        if not custom_prompt:
            print("custom_prompt.mdが見つからないため、デフォルトのプロンプトを使用します。")
            prompt = f"以下のテキストを簡潔に要約してください。重要なポイントを網羅してください。\n\n{text}"
        else:
            # テンプレートを使用してプロンプトを作成
            prompt = f"{custom_prompt}\n\n以下が要約対象のテキストです：\n\n{text}"

        # プロンプトも念のためクリーニング
        prompt = clean_text(prompt)

        response = model.generate_content(prompt)
        response_text = response.text

        # JSON形式のレスポンスを解析
        try:
            import json
            import re
            
            # デバッグ: レスポンステキストの最初の500文字を表示
            print(f"レスポンステキスト（最初の500文字）: {response_text[:500]}")
            
            # JSONブロックを抽出（```json と ``` で囲まれた部分）
            json_pattern = r'```json\s*\n(.*?)\n```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(1)
                print(f"JSONブロックを抽出: {json_text[:200]}...")
            else:
                # JSONブロックが見つからない場合は、全体をJSONとして解析を試行
                json_text = response_text.strip()
                print("JSONブロックが見つからないため、全体をJSONとして解析を試行")
            
            # JSONを解析してフィールドを取得
            json_data = json.loads(json_text)
            
            # すべてのフィールドを自動抽出して正規化
            result = {}
            for field, value in json_data.items():
                if value:
                    result[field] = normalize_llm_text(value) if isinstance(value, str) else value
                else:
                    result[field] = ''
            
            print(f"JSON解析成功 - 抽出フィールド数: {len([k for k, v in result.items() if v])}")
            print(f"抽出されたフィールド: {list(result.keys())}")
            
            # キーワード処理
            if result.get('keyword'):
                keyword_manager = KeywordManager()
                processed_keywords = keyword_manager.process_generated_keywords(result['keyword'])
                if processed_keywords:
                    # キーワードを改行区切りの#付き形式に整形
                    result['keyword'] = '\n> '.join([f'#{kw}' for kw in processed_keywords])
                    print(f"処理済みキーワード: {result['keyword']}")
            
            return result
        except json.JSONDecodeError as e:
            # JSON解析に失敗した場合のロバスト処理
            import re, json
            print(f"JSON解析に失敗しました: {e}")
            print(f"レスポンステキスト全体: {response_text}")

            # コードフェンスを剥がしてテキストを取得
            fence_pattern = r"```json\s*\n(.*?)\n```"
            fence_match = re.search(fence_pattern, response_text, re.DOTALL)
            raw = fence_match.group(1) if fence_match else response_text

            # 無効なバックスラッシュを二重化してJSONとして再試行
            def escape_invalid_backslashes(s: str) -> str:
                # 有効なエスケープ(\n, \t, \/, \", \\)以外の \x を \\x に置換
                return re.sub(r"\\(?![\\\"nt/])", r"\\\\", s)

            fixed = escape_invalid_backslashes(raw)
            try:
                data = json.loads(fixed)
                result = {}
                
                # すべてのフィールドを自動抽出して正規化
                for field, value in data.items():
                    if value:
                        result[field] = normalize_llm_text(value) if isinstance(value, str) else value
                    else:
                        result[field] = ''
                
                # キーワード処理
                if result.get('keyword'):
                    keyword_manager = KeywordManager()
                    processed_keywords = keyword_manager.process_generated_keywords(result['keyword'])
                    if processed_keywords:
                        result['keyword'] = '\n> '.join([f'#{kw}' for kw in processed_keywords])
                
                return result
            except Exception as e2:
                print(f"修正後のJSON解析にも失敗: {e2}")
                # 最後のフォールバック: 正規表現で各フィールドを抜き出す
                result = {}
                
                # JSONから全フィールド名を抽出
                field_pattern = r'"(\w+)"\s*:\s*"([\s\S]*?)"\s*(,|})'
                matches = re.findall(field_pattern, raw)
                
                for field, value, _ in matches:
                    result[field] = normalize_llm_text(value)
                
                # キーワード処理
                if result.get('keyword'):
                    keyword_manager = KeywordManager()
                    processed_keywords = keyword_manager.process_generated_keywords(result['keyword'])
                    if processed_keywords:
                        result['keyword'] = '\n> '.join([f'#{kw}' for kw in processed_keywords])
                
                return result
    except Exception as e:
        print(f"テキストの要約中にエラーが発生しました: {e}")
        return None

# 使用例:
# long_text = "ここに非常に長いテキストが入ります..."
# summary = summarize_text(long_text)
# if summary:
#     print("要約:\n", summary)
