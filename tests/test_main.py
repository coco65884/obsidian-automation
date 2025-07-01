from main import get_existing_notes, process_pdf, main
import pytest
import os
import tempfile
from unittest.mock import patch
import sys

# パスを追加してモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMain:
    """main.pyのテスト"""

    @pytest.fixture
    def temp_note_folder(self):
        """テスト用の一時ノートフォルダ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用のMarkdownファイルを作成
            test_files = ["note1.md", "note2.md", "test_paper.md"]
            for file_name in test_files:
                file_path = os.path.join(temp_dir, file_name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("# Test Note\nThis is a test note.")
            yield temp_dir

    @pytest.fixture
    def temp_pdf_folder(self):
        """テスト用の一時PDFフォルダ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用のPDFファイル（空ファイル）を作成
            test_files = ["test1.pdf", "test2.pdf"]
            for file_name in test_files:
                with open(os.path.join(temp_dir, file_name), 'wb') as f:
                    f.write(b"dummy pdf content")
            yield temp_dir

    def test_get_existing_notes(self, temp_note_folder):
        """既存ノート取得のテスト"""
        with patch('main.NOTE_FOLDER', temp_note_folder):
            existing_notes = get_existing_notes()

            assert isinstance(existing_notes, set)
            assert "note1" in existing_notes
            assert "note2" in existing_notes
            assert "test_paper" in existing_notes
            assert len(existing_notes) == 3

    def test_get_existing_notes_empty_folder(self):
        """空フォルダでの既存ノート取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('main.NOTE_FOLDER', temp_dir):
                existing_notes = get_existing_notes()
                assert isinstance(existing_notes, set)
                assert len(existing_notes) == 0

    def test_get_existing_notes_nonexistent_folder(self):
        """存在しないフォルダでの既存ノート取得テスト"""
        with patch('main.NOTE_FOLDER', '/nonexistent/folder'):
            existing_notes = get_existing_notes()
            assert isinstance(existing_notes, set)
            assert len(existing_notes) == 0

    @patch('main.create_obsidian_note')
    @patch('main.get_zotero_item_info')
    @patch('main.summarize_text')
    @patch('main.extract_text_from_pdf')
    def test_process_pdf_success(self, mock_extract, mock_summarize,
                                 mock_zotero, mock_create_note):
        """PDF処理成功のテスト"""
        # モックの設定
        mock_extract.return_value = "Test PDF content"
        mock_summarize.return_value = "Test summary"
        mock_zotero.return_value = {"title": "Test Paper"}
        mock_create_note.return_value = None

        # テスト実行
        result = process_pdf("test.pdf")

        # アサーション
        assert result is True
        mock_extract.assert_called_once_with("test.pdf")
        mock_summarize.assert_called_once_with("Test PDF content")
        mock_zotero.assert_called_once_with("test")
        mock_create_note.assert_called_once()

    @patch('main.extract_text_from_pdf')
    def test_process_pdf_extract_failure(self, mock_extract):
        """PDFテキスト抽出失敗のテスト"""
        mock_extract.return_value = None

        result = process_pdf("test.pdf")

        assert result is False
        mock_extract.assert_called_once_with("test.pdf")

    @patch('main.create_obsidian_note')
    @patch('main.get_zotero_item_info')
    @patch('main.summarize_text')
    @patch('main.extract_text_from_pdf')
    def test_process_pdf_summarize_failure(self, mock_extract, mock_summarize,
                                           mock_zotero, mock_create_note):
        """要約生成失敗のテスト"""
        mock_extract.return_value = "Test PDF content"
        mock_summarize.return_value = None
        mock_zotero.return_value = {"title": "Test Paper"}
        mock_create_note.return_value = None

        result = process_pdf("test.pdf")

        # 要約が失敗してもノート作成は続行される
        assert result is True
        mock_create_note.assert_called_once()

    @patch('main.create_obsidian_note')
    @patch('main.get_zotero_item_info')
    @patch('main.summarize_text')
    @patch('main.extract_text_from_pdf')
    def test_process_pdf_zotero_failure(self, mock_extract, mock_summarize,
                                        mock_zotero, mock_create_note):
        """Zotero情報取得失敗のテスト"""
        mock_extract.return_value = "Test PDF content"
        mock_summarize.return_value = "Test summary"
        mock_zotero.return_value = None
        mock_create_note.return_value = None

        result = process_pdf("test.pdf")

        # Zotero情報取得が失敗してもノート作成は続行される
        assert result is True
        mock_create_note.assert_called_once()

    @patch('main.create_obsidian_note')
    @patch('main.get_zotero_item_info')
    @patch('main.summarize_text')
    @patch('main.extract_text_from_pdf')
    def test_process_pdf_note_creation_failure(self, mock_extract, mock_summarize,
                                               mock_zotero, mock_create_note):
        """ノート作成失敗のテスト"""
        mock_extract.return_value = "Test PDF content"
        mock_summarize.return_value = "Test summary"
        mock_zotero.return_value = {"title": "Test Paper"}
        mock_create_note.side_effect = Exception("Note creation failed")

        result = process_pdf("test.pdf")

        assert result is False

    @patch('main.process_pdf')
    @patch('main.get_existing_notes')
    @patch('main.os.path.exists')
    @patch('main.glob.glob')
    def test_main_function(self, mock_glob, mock_exists, mock_get_notes,
                           mock_process):
        """main関数のテスト"""
        # モックの設定
        mock_exists.return_value = True
        mock_get_notes.return_value = {"existing_note"}
        mock_glob.return_value = ["/path/to/test1.pdf",
                                  "/path/to/existing_note.pdf"]
        mock_process.return_value = True

        with patch('builtins.print'):  # print文をモック
            main()

        # 既存ノートと同名のPDFはスキップされ、新しいPDFのみ処理される
        mock_process.assert_called_once_with("/path/to/test1.pdf")

    @patch('main.os.path.exists')
    def test_main_pdf_folder_not_exists(self, mock_exists):
        """PDFフォルダが存在しない場合のテスト"""
        mock_exists.return_value = False

        with patch('builtins.print') as mock_print:
            main()

        # エラーメッセージが出力されることを確認
        mock_print.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
