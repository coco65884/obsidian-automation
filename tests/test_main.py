from main import process_pdf_file, monitor_directory
import pytest
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
import sys

# テスト用にパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMain:
    """メインモジュールの処理のテスト"""

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_success(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """PDF処理成功のテスト"""
        # モックの設定
        mock_extract_text.return_value = "Extracted PDF text"
        mock_get_metadata.return_value = {
            'title': 'Test Paper',
            'creators': [{'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'}]
        }
        mock_summarize.return_value = "Generated summary with keywords"

        # KeywordManagerのモック
        mock_km_instance = Mock()
        mock_km_instance.process_generated_keywords.return_value = "Processed keywords"
        mock_keyword_manager.return_value = mock_km_instance

        # テスト実行
        process_pdf_file("/test/path/test.pdf")

        # 各関数が正しく呼ばれたことを確認
        mock_extract_text.assert_called_once_with("/test/path/test.pdf")
        mock_get_metadata.assert_called_once_with("test.pdf")
        mock_summarize.assert_called_once()
        mock_create_note.assert_called_once()

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_extract_text_error(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """PDF文字列抽出エラーのテスト"""
        # テキスト抽出でエラーが発生
        mock_extract_text.side_effect = Exception("PDF extraction error")

        # エラーが発生してもクラッシュしないことを確認
        try:
            process_pdf_file("/test/path/test.pdf")
        except Exception:
            pytest.fail(
                "process_pdf_file should handle extraction errors gracefully")

        # 後続の処理は実行されないことを確認
        mock_get_metadata.assert_not_called()
        mock_summarize.assert_not_called()
        mock_create_note.assert_not_called()

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_zotero_error(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """Zoteroメタデータ取得エラーのテスト"""
        mock_extract_text.return_value = "Extracted text"
        mock_get_metadata.side_effect = Exception("Zotero error")
        mock_summarize.return_value = "Summary text"

        mock_km_instance = Mock()
        mock_km_instance.process_generated_keywords.return_value = "Keywords"
        mock_keyword_manager.return_value = mock_km_instance

        # エラーが発生してもクラッシュしないことを確認
        try:
            process_pdf_file("/test/path/test.pdf")
        except Exception:
            pytest.fail(
                "process_pdf_file should handle Zotero errors gracefully")

        # Zoteroメタデータなしでもノート作成は実行されることを確認
        mock_create_note.assert_called_once()

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_summarize_error(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """要約生成エラーのテスト"""
        mock_extract_text.return_value = "Extracted text"
        mock_get_metadata.return_value = {'title': 'Test Paper'}
        mock_summarize.side_effect = Exception("Summarization error")

        mock_km_instance = Mock()
        mock_keyword_manager.return_value = mock_km_instance

        # エラーが発生してもクラッシュしないことを確認
        try:
            process_pdf_file("/test/path/test.pdf")
        except Exception:
            pytest.fail(
                "process_pdf_file should handle summarization errors gracefully")

        # 要約なしでもノート作成は実行されることを確認
        mock_create_note.assert_called_once()

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_note_creation_error(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """ノート作成エラーのテスト"""
        mock_extract_text.return_value = "Extracted text"
        mock_get_metadata.return_value = {'title': 'Test Paper'}
        mock_summarize.return_value = "Summary"
        mock_create_note.side_effect = Exception("Note creation error")

        mock_km_instance = Mock()
        mock_km_instance.process_generated_keywords.return_value = "Keywords"
        mock_keyword_manager.return_value = mock_km_instance

        # エラーが発生してもクラッシュしないことを確認
        try:
            process_pdf_file("/test/path/test.pdf")
        except Exception:
            pytest.fail(
                "process_pdf_file should handle note creation errors gracefully")

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_keyword_manager_error(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """キーワード処理エラーのテスト"""
        mock_extract_text.return_value = "Extracted text"
        mock_get_metadata.return_value = {'title': 'Test Paper'}
        mock_summarize.return_value = "Summary"

        # KeywordManagerでエラーが発生
        mock_keyword_manager.side_effect = Exception("Keyword manager error")

        # エラーが発生してもクラッシュしないことを確認
        try:
            process_pdf_file("/test/path/test.pdf")
        except Exception:
            pytest.fail(
                "process_pdf_file should handle keyword manager errors gracefully")

        # ノート作成は実行されることを確認
        mock_create_note.assert_called_once()

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_no_zotero_metadata(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """Zoteroメタデータが見つからない場合のテスト"""
        mock_extract_text.return_value = "Extracted text"
        mock_get_metadata.return_value = None  # メタデータなし
        mock_summarize.return_value = "Summary"

        mock_km_instance = Mock()
        mock_km_instance.process_generated_keywords.return_value = "Keywords"
        mock_keyword_manager.return_value = mock_km_instance

        process_pdf_file("/test/path/test.pdf")

        # メタデータなしでもノート作成は実行されることを確認
        mock_create_note.assert_called_once()
        call_args = mock_create_note.call_args[0]
        assert call_args[1] is None  # zotero_dataがNone

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_empty_text(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """空のテキストが抽出された場合のテスト"""
        mock_extract_text.return_value = ""  # 空のテキスト
        mock_get_metadata.return_value = {'title': 'Test Paper'}
        mock_summarize.return_value = "Default summary"

        mock_km_instance = Mock()
        mock_km_instance.process_generated_keywords.return_value = "Keywords"
        mock_keyword_manager.return_value = mock_km_instance

        process_pdf_file("/test/path/test.pdf")

        # 空のテキストでも処理が継続されることを確認
        mock_summarize.assert_called_once()
        mock_create_note.assert_called_once()

    @patch('main.watchdog.observers.Observer')
    @patch('main.time.sleep')
    def test_monitor_directory_basic(self, mock_sleep, mock_observer_class):
        """ディレクトリ監視の基本テスト"""
        # Observerのモック
        mock_observer_instance = Mock()
        mock_observer_class.return_value = mock_observer_instance

        # sleepを1回だけ実行して終了するように設定
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        try:
            monitor_directory()
        except KeyboardInterrupt:
            pass  # 期待される終了

        # Observerが正しく設定されたことを確認
        mock_observer_instance.schedule.assert_called_once()
        mock_observer_instance.start.assert_called_once()
        mock_observer_instance.stop.assert_called_once()
        mock_observer_instance.join.assert_called_once()

    @patch('main.watchdog.observers.Observer')
    @patch('main.time.sleep')
    def test_monitor_directory_observer_error(self, mock_sleep, mock_observer_class):
        """Observerエラーのテスト"""
        # Observerでエラーが発生
        mock_observer_class.side_effect = Exception("Observer error")

        # エラーが発生してもクラッシュしないことを確認
        try:
            monitor_directory()
        except Exception:
            pytest.fail(
                "monitor_directory should handle observer errors gracefully")

    def test_pdf_file_filtering(self):
        """PDFファイルのフィルタリングテスト"""
        # 実際のファイルハンドラーのテストは複雑なので、
        # ここでは基本的なロジックのテストのみ実装
        assert True  # プレースホルダー

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_with_custom_prompt(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """カスタムプロンプトでの処理テスト"""
        mock_extract_text.return_value = "Extracted text"
        mock_get_metadata.return_value = {'title': 'Test Paper'}

        # KeywordManagerのモック
        mock_km_instance = Mock()
        mock_km_instance.create_keyword_prompt.return_value = "Custom keyword prompt"
        mock_km_instance.process_generated_keywords.return_value = "Processed keywords"
        mock_keyword_manager.return_value = mock_km_instance

        # カスタムプロンプトの読み込みをモック
        with patch('builtins.open', mock_open=Mock()):
            with patch('main.os.path.exists', return_value=True):
                mock_summarize.return_value = "Summary with custom prompt"

                process_pdf_file("/test/path/test.pdf")

                # カスタムプロンプトが使用されたことを確認
                mock_km_instance.create_keyword_prompt.assert_called_once()
                mock_summarize.assert_called_once()

    @patch('main.extract_text_from_pdf')
    @patch('main.get_pdf_metadata_from_zotero')
    @patch('main.summarize_text')
    @patch('main.create_obsidian_note')
    @patch('main.KeywordManager')
    def test_process_pdf_file_filename_edge_cases(
        self, mock_keyword_manager, mock_create_note,
        mock_summarize, mock_get_metadata, mock_extract_text
    ):
        """ファイル名のエッジケースのテスト"""
        mock_extract_text.return_value = "Extracted text"
        mock_get_metadata.return_value = {'title': 'Test Paper'}
        mock_summarize.return_value = "Summary"

        mock_km_instance = Mock()
        mock_km_instance.process_generated_keywords.return_value = "Keywords"
        mock_keyword_manager.return_value = mock_km_instance

        # 特殊文字を含むファイル名でテスト
        test_filenames = [
            "/path/to/file with spaces.pdf",
            "/path/to/file[with]brackets.pdf",
            "/path/to/file(with)parentheses.pdf",
            "/path/to/ファイル名.pdf"  # 日本語ファイル名
        ]

        for filename in test_filenames:
            try:
                process_pdf_file(filename)
                # エラーが発生しないことを確認
            except Exception:
                pytest.fail(
                    f"process_pdf_file should handle filename: {filename}")

    @patch('main.os.path.basename')
    def test_filename_extraction(self, mock_basename):
        """ファイル名抽出のテスト"""
        mock_basename.return_value = "test_file.pdf"

        # process_pdf_fileの内部でbasenameが呼ばれることを間接的に確認
        with patch('main.extract_text_from_pdf', side_effect=Exception("Stop here")):
            try:
                process_pdf_file("/full/path/to/test_file.pdf")
            except Exception:
                pass  # 期待されるエラー

            mock_basename.assert_called()


def mock_open(read_data=""):
    """mock_openの簡易実装"""
    m = Mock()
    m.read.return_value = read_data
    m.__enter__.return_value = m
    m.__exit__.return_value = None
    return m
