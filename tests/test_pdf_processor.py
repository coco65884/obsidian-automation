from pdf_processor import (
    clean_text, extract_text_from_pdf, summarize_text,
    PDFProcessingError, APIError
)
import pytest
import tempfile
import os
from unittest.mock import patch, Mock, mock_open
import sys

# テスト用にパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPDFProcessor:
    """PDF処理関数のテスト"""

    def test_clean_text_basic(self):
        """基本的なテキストクリーニングのテスト"""
        # 正常なテキスト
        clean_text_input = "This is normal text."
        result = clean_text(clean_text_input)
        assert result == "This is normal text."

    def test_clean_text_with_control_characters(self):
        """制御文字を含むテキストのクリーニングテスト"""
        # 制御文字を含むテキスト
        dirty_text = "Text with\x00control\x01characters\x02"
        result = clean_text(dirty_text)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x02" not in result
        assert "Text with control characters" in result

    def test_clean_text_with_surrogate_characters(self):
        """サロゲート文字のクリーニングテスト"""
        # UTF-8エンコーディングエラーのシミュレーション
        with patch('builtins.str.encode') as mock_encode:
            mock_encode.return_value.decode.return_value = "cleaned text"

            result = clean_text("text with surrogates")
            assert result == "cleaned text"

    def test_clean_text_empty_input(self):
        """空の入力のテスト"""
        assert clean_text("") == ""
        assert clean_text(None) == ""

    @patch('pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_success(self, mock_pdf_reader):
        """PDF文字列抽出成功のテスト"""
        # モックページオブジェクトを作成
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        # モックPDFリーダーを設定
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        # テスト用の一時PDFファイル
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(b'dummy pdf content')
            temp_pdf_path = temp_pdf.name

        try:
            result = extract_text_from_pdf(temp_pdf_path)

            assert "Page 1 content" in result
            assert "Page 2 content" in result
            mock_pdf_reader.assert_called_once()
        finally:
            os.unlink(temp_pdf_path)

    @patch('pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_file_not_found(self, mock_pdf_reader):
        """存在しないPDFファイルのテスト"""
        with pytest.raises(PDFProcessingError, match="PDFファイルが見つかりません"):
            extract_text_from_pdf("/non/existent/file.pdf")

    @patch('pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_pypdf2_error(self, mock_pdf_reader):
        """PyPDF2エラーのテスト"""
        # PyPDF2でエラーが発生する場合をシミュレート
        mock_pdf_reader.side_effect = Exception("PDF parsing error")

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(b'dummy pdf content')
            temp_pdf_path = temp_pdf.name

        try:
            with pytest.raises(PDFProcessingError, match="PDFの読み込み中にエラーが発生しました"):
                extract_text_from_pdf(temp_pdf_path)
        finally:
            os.unlink(temp_pdf_path)

    @patch('pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_empty_pages(self, mock_pdf_reader):
        """空のページを持つPDFのテスト"""
        # 空のページを持つモックを作成
        mock_page = Mock()
        mock_page.extract_text.return_value = ""

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(b'dummy pdf content')
            temp_pdf_path = temp_pdf.name

        try:
            result = extract_text_from_pdf(temp_pdf_path)
            # 空のページでもエラーにならず、空文字列が返されることを確認
            assert result == ""
        finally:
            os.unlink(temp_pdf_path)

    @patch('pdf_processor.genai.GenerativeModel')
    @patch('pdf_processor.genai.configure')
    def test_summarize_text_success(self, mock_configure, mock_model_class):
        """テキスト要約成功のテスト"""
        # モックの設定
        mock_model_instance = Mock()
        mock_response = Mock()
        mock_response.text = "これは要約されたテキストです。"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        # 環境変数のモック
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'}):
            result = summarize_text("長いテキストの内容", "要約してください")

            assert result == "これは要約されたテキストです。"
            mock_configure.assert_called_once_with(api_key='test_api_key')
            mock_model_instance.generate_content.assert_called_once()

    @patch('pdf_processor.genai.GenerativeModel')
    @patch('pdf_processor.genai.configure')
    def test_summarize_text_api_error(self, mock_configure, mock_model_class):
        """API呼び出しエラーのテスト"""
        # API エラーをシミュレート
        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = Exception(
            "API Error")
        mock_model_class.return_value = mock_model_instance

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'}):
            with pytest.raises(APIError, match="Gemini APIでエラーが発生しました"):
                summarize_text("テキスト", "プロンプト")

    def test_summarize_text_no_api_key(self):
        """APIキーが設定されていない場合のテスト"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(APIError, match="Gemini APIキーが設定されていません"):
                summarize_text("テキスト", "プロンプト")

    @patch('pdf_processor.genai.GenerativeModel')
    @patch('pdf_processor.genai.configure')
    def test_summarize_text_empty_response(self, mock_configure, mock_model_class):
        """空のレスポンスのテスト"""
        mock_model_instance = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'}):
            result = summarize_text("テキスト", "プロンプト")
            assert result == ""

    @patch('pdf_processor.genai.GenerativeModel')
    @patch('pdf_processor.genai.configure')
    def test_summarize_text_with_clean_text(self, mock_configure, mock_model_class):
        """clean_textが適用されることのテスト"""
        mock_model_instance = Mock()
        mock_response = Mock()
        mock_response.text = "Clean response"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        with patch('pdf_processor.clean_text') as mock_clean_text:
            mock_clean_text.side_effect = lambda x: f"cleaned: {x}"

            with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'}):
                result = summarize_text("dirty text", "dirty prompt")

                # clean_textが呼ばれたことを確認
                assert mock_clean_text.call_count == 3  # text, prompt, response
                assert result == "cleaned: Clean response"

    def test_pdf_processing_error_inheritance(self):
        """PDFProcessingErrorが正しくExceptionを継承しているかテスト"""
        error = PDFProcessingError("test message")
        assert isinstance(error, Exception)
        assert str(error) == "test message"

    def test_api_error_inheritance(self):
        """APIErrorが正しくExceptionを継承しているかテスト"""
        error = APIError("api test message")
        assert isinstance(error, Exception)
        assert str(error) == "api test message"

    @patch('pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_with_page_errors(self, mock_pdf_reader):
        """一部のページでエラーが発生する場合のテスト"""
        # 最初のページは正常、2番目のページでエラー
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"

        mock_page2 = Mock()
        mock_page2.extract_text.side_effect = Exception(
            "Page extraction error")

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(b'dummy pdf content')
            temp_pdf_path = temp_pdf.name

        try:
            result = extract_text_from_pdf(temp_pdf_path)
            # エラーが発生したページは無視されて、正常なページのテキストのみ返される
            assert "Page 1 content" in result
            assert "Page 2" not in result
        finally:
            os.unlink(temp_pdf_path)

    @patch('pdf_processor.os.path.exists')
    def test_extract_text_from_pdf_permission_error(self, mock_exists):
        """ファイルアクセス権限エラーのテスト"""
        mock_exists.return_value = True

        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PDFProcessingError, match="PDFファイルにアクセスできません"):
                extract_text_from_pdf("test.pdf")
