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


def summarize_text(text, model_name="gemini-pro"):
    try:
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
