import PyPDF2
import google.generativeai as genai
import os
from keyword_manager import KeywordManager


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
        prompt_path = os.path.join(script_dir, "custom_prompt.md")
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


def process_keywords_in_summary(summary_text):
    """要約テキストからキーワードを抽出・処理し、最終的な要約を返す"""
    try:
        keyword_manager = KeywordManager()

        # キーワードを抽出・処理
        processed_keywords = keyword_manager.process_generated_keywords(
            summary_text)

        if processed_keywords:
            # 処理済みキーワードで置き換え
            keyword_lines = []
            for keyword in processed_keywords:
                keyword_lines.append(f"> #{keyword}")

            # Keywords セクションを新しいキーワードで置き換え
            import re
            keywords_pattern = (r'(> ### \*\*Keywords\*\*\s*\n)(.*?)'
                                r'(?=\n\n|\n#|\nObsidian Links|\Z)')

            def replace_keywords(match):
                header = match.group(1)
                return header + "\n".join(keyword_lines) + "\n"

            updated_summary = re.sub(keywords_pattern, replace_keywords,
                                     summary_text, flags=re.DOTALL)

            if updated_summary != summary_text:
                print(f"キーワードを処理済みキーワードで置き換えました: {processed_keywords}")
                return updated_summary

        return summary_text

    except Exception as e:
        print(f"キーワード処理中にエラーが発生しました: {e}")
        return summary_text


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
        summary_text = response.text

        # キーワードを処理
        if summary_text:
            summary_text = process_keywords_in_summary(summary_text)

        return summary_text
    except Exception as e:
        print(f"テキストの要約中にエラーが発生しました: {e}")
        return None

# 使用例:
# long_text = "ここに非常に長いテキストが入ります..."
# summary = summarize_text(long_text)
# if summary:
#     print("要約:\n", summary)
