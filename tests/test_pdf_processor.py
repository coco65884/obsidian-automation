from pdf_processor import (
    extract_text_from_pdf, clean_text, load_custom_prompt,
    get_available_models, process_keywords_in_summary,
    summarize_text
)
import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
import sys

# パスを追加してモジュールをインポート
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))


class TestPDFProcessor:
    """pdf_processor.pyのテスト"""

    def test_clean_text_basic(self):
        """基本的なテキストクリーニングのテスト"""
        # 正常なテキスト
        clean = clean_text("Hello World")
        assert clean == "Hello World"

        # 前後の空白削除
        clean = clean_text("  Hello World  ")
        assert clean == "Hello World"

        # 連続する空白の処理
        clean = clean_text("Hello    World")
        assert clean == "Hello World"

    def test_clean_text_empty_and_none(self):
        """空文字列とNoneのテキストクリーニングテスト"""
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_clean_text_special_characters(self):
        """特殊文字を含むテキストクリーニングのテスト"""
        # 改行とタブは保持されるが、連続する空白は単一のスペースになる
        text_with_newlines = "Hello\nWorld\tTest"
        cleaned = clean_text(text_with_newlines)
        # clean_textは連続する空白を単一のスペースに変換する
        assert "Hello" in cleaned
        assert "World" in cleaned
        assert "Test" in cleaned

    @patch('pdf_processor.PyPDF2.PdfReader')
    @patch('builtins.open')
    def test_extract_text_from_pdf_success(self, mock_open_file,
                                           mock_pdf_reader):
        """PDF文字列抽出成功のテスト"""
        # モックページオブジェクト
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF text"

        # モックリーダー
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page, mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # テスト実行
        result = extract_text_from_pdf("test.pdf")

        # アサーション - 実際のコードはページ間にスペースを挿入しない
        assert result == "Sample PDF textSample PDF text"
        mock_open_file.assert_called_once_with("test.pdf", 'rb')

    @patch('pdf_processor.PyPDF2.PdfReader')
    @patch('builtins.open')
    def test_extract_text_from_pdf_exception(self, mock_open_file,
                                             mock_pdf_reader):
        """PDF抽出例外処理のテスト"""
        mock_pdf_reader.side_effect = Exception("PDF reading error")

        result = extract_text_from_pdf("test.pdf")
        assert result is None

    @patch('pdf_processor.KeywordManager')
    def test_load_custom_prompt_success(self, mock_keyword_manager):
        """custom_prompt.md読み込み成功のテスト"""
        # KeywordManagerのモック
        mock_km_instance = MagicMock()
        mock_km_instance.create_keyword_prompt.return_value = "Mock keywords"
        mock_keyword_manager.return_value = mock_km_instance

        # ファイル読み込みのモック
        mock_content = "Template content {KEYWORDS_SECTION} end"
        with patch('builtins.open', mock_open(read_data=mock_content)):
            result = load_custom_prompt()

        expected = "Template content Mock keywords end"
        assert result == expected

    @patch('pdf_processor.KeywordManager')
    def test_load_custom_prompt_file_not_found(self, mock_keyword_manager):
        """custom_prompt.md見つからない場合のテスト"""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = load_custom_prompt()

        assert result is None

    @patch('pdf_processor.genai.list_models')
    def test_get_available_models_success(self, mock_list_models):
        """利用可能モデル取得成功のテスト"""
        # モックモデル
        mock_model1 = MagicMock()
        mock_model1.name = "models/gemini-1.5-flash"
        mock_model1.supported_generation_methods = ["generateContent"]

        mock_model2 = MagicMock()
        mock_model2.name = "models/gemini-pro"
        mock_model2.supported_generation_methods = ["generateContent"]

        mock_list_models.return_value = [mock_model1, mock_model2]

        result = get_available_models()
        assert "gemini-1.5-flash" in result
        assert "gemini-pro" in result

    @patch('pdf_processor.genai.list_models')
    def test_get_available_models_exception(self, mock_list_models):
        """モデル取得例外処理のテスト"""
        mock_list_models.side_effect = Exception("API error")

        result = get_available_models()
        assert result == []

    @patch('pdf_processor.KeywordManager')
    def test_process_keywords_in_summary_success(self, mock_keyword_manager):
        """要約内キーワード処理成功のテスト"""
        # KeywordManagerのモック
        mock_km_instance = MagicMock()
        mock_km_instance.process_generated_keywords.return_value = [
            "CV", "CNN"]
        mock_keyword_manager.return_value = mock_km_instance

        summary_text = """
> ### **Keywords**
> #MachineLearning
> #DeepLearning

Some other content
"""

        result = process_keywords_in_summary(summary_text)

        # キーワードが処理されることを確認
        assert "#CV" in result or "#CNN" in result
        mock_km_instance.process_generated_keywords.assert_called_once()

    @patch('pdf_processor.KeywordManager')
    def test_process_keywords_in_summary_no_keywords(self,
                                                     mock_keyword_manager):
        """キーワードなしの要約処理のテスト"""
        mock_km_instance = MagicMock()
        mock_km_instance.process_generated_keywords.return_value = []
        mock_keyword_manager.return_value = mock_km_instance

        summary_text = "Simple summary without keywords section"

        result = process_keywords_in_summary(summary_text)
        assert result == summary_text  # 変更されない

    @patch('pdf_processor.process_keywords_in_summary')
    @patch('pdf_processor.genai.GenerativeModel')
    @patch('pdf_processor.load_custom_prompt')
    @patch('pdf_processor.get_available_models')
    def test_summarize_text_success(self, mock_get_models, mock_load_prompt,
                                    mock_gen_model, mock_process_keywords):
        """テキスト要約成功のテスト"""
        # モックの設定
        mock_get_models.return_value = ["gemini-2.5-flash"]
        mock_load_prompt.return_value = "Custom prompt template"

        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated summary"
        mock_model_instance.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model_instance

        mock_process_keywords.return_value = "Processed summary"

        # テスト実行
        result = summarize_text("Sample text to summarize")

        # アサーション
        expected = {
            'summary': "Processed summary",
            'abstract': "",
            'publication': ""
        }
        assert result == expected
        mock_gen_model.assert_called_once_with("gemini-2.5-flash")
        mock_model_instance.generate_content.assert_called_once()

    @patch('pdf_processor.get_available_models')
    def test_summarize_text_no_available_models(self, mock_get_models):
        """利用可能モデルなしのテスト"""
        mock_get_models.return_value = []

        result = summarize_text("Sample text")
        assert result is None

    @patch('pdf_processor.genai.GenerativeModel')
    @patch('pdf_processor.load_custom_prompt')
    @patch('pdf_processor.get_available_models')
    def test_summarize_text_generation_exception(self, mock_get_models,
                                                 mock_load_prompt,
                                                 mock_gen_model):
        """テキスト生成例外のテスト"""
        mock_get_models.return_value = ["gemini-2.5-flash"]
        mock_load_prompt.return_value = "Custom prompt"

        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception(
            "Generation error")
        mock_gen_model.return_value = mock_model_instance

        result = summarize_text("Sample text")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
