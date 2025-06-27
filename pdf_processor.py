import PyPDF2
import google.generativeai as genai
import os


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        print(f"PDFからのテキスト抽出中にエラーが発生しました: {e}")
        return None

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
            return f.read()
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


def summarize_text(text, model_name="gemini-2.5-flash"):
    try:
        # まず利用可能なモデルを確認
        available_models = get_available_models()

        # モデル名を確認し、必要に応じて調整
        if model_name not in available_models:
            # gemini-2.5-flashが見つからない場合、代替モデルを試す
            fallback_models = ["gemini-1.5-flash",
                               "gemini-1.5-pro", "gemini-pro"]
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

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"テキストの要約中にエラーが発生しました: {e}")
        return None

# 使用例:
# long_text = "ここに非常に長いテキストが入ります..."
# summary = summarize_text(long_text)
# if summary:
#     print("要約:\n", summary)
