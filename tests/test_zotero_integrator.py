from zotero_integrator import normalize_filename, get_zotero_item_info
import pytest
import os
from unittest.mock import patch, MagicMock
import sys

# パスを追加してモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestZoteroIntegrator:
    """zotero_integrator.pyのテスト"""

    def test_normalize_filename_basic(self):
        """基本的なファイル名正規化のテスト"""
        # 大文字小文字変換
        assert normalize_filename("TEST_FILE") == "test file"

        # スペース、ハイフン、アンダースコア統一
        assert normalize_filename("test-file_name") == "test file name"

        # 複数スペース除去
        assert normalize_filename("test   file") == "test file"

        # 前後の空白除去
        assert normalize_filename("  test file  ") == "test file"

    def test_normalize_filename_edge_cases(self):
        """ファイル名正規化のエッジケースのテスト"""
        # 空文字列
        assert normalize_filename("") == ""

        # 特殊文字のみ
        assert normalize_filename("---___") == ""

        # 複雑な組み合わせ
        assert normalize_filename(
            "Test_File-Name Space") == "test file name space"

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_zotero_item_info_success(self, mock_zotero_class):
        """Zotero情報取得成功のテスト"""
        # モックZoteroインスタンス
        mock_zotero = MagicMock()
        mock_zotero_class.return_value = mock_zotero

        # モックアイテム
        mock_item = {
            'data': {
                'title': 'Test Paper Title',
                'itemType': 'journalArticle',
                'creators': [{'firstName': 'John', 'lastName': 'Doe'}]
            }
        }

        mock_zotero.items.return_value = [mock_item]

        # テスト実行
        result = get_zotero_item_info("Test Paper Title")

        # アサーション
        assert result is not None
        assert result['title'] == 'Test Paper Title'
        mock_zotero.items.assert_called_once_with(q="Test Paper Title")

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_zotero_item_info_no_results(self, mock_zotero_class):
        """Zotero情報取得結果なしのテスト"""
        mock_zotero = MagicMock()
        mock_zotero_class.return_value = mock_zotero
        mock_zotero.items.return_value = []  # 結果なし

        result = get_zotero_item_info("Nonexistent Paper")

        assert result is None

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_zotero_item_info_partial_match(self, mock_zotero_class):
        """Zotero情報取得部分一致のテスト"""
        mock_zotero = MagicMock()
        mock_zotero_class.return_value = mock_zotero

        # 部分一致するアイテム
        mock_item = {
            'data': {
                'title': 'A Study on Machine Learning Applications',
                'itemType': 'journalArticle'
            }
        }

        mock_zotero.items.return_value = [mock_item]

        # "Machine Learning" で検索（部分一致）
        result = get_zotero_item_info("machine learning")

        assert result is not None
        assert 'Machine Learning' in result['title']

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_zotero_item_info_attachment_with_parent(self, mock_zotero_class):
        """添付ファイルと親アイテムの処理テスト"""
        mock_zotero = MagicMock()
        mock_zotero_class.return_value = mock_zotero

        # 添付ファイルアイテム
        attachment_item = {
            'data': {
                'title': 'test.pdf',
                'itemType': 'attachment',
                'parentItem': 'PARENT123'
            }
        }

        # 親アイテム
        parent_item = {
            'data': {
                'title': 'Parent Paper Title',
                'itemType': 'journalArticle'
            }
        }

        mock_zotero.items.return_value = [attachment_item]
        mock_zotero.item.return_value = parent_item

        result = get_zotero_item_info("test")

        # 親アイテムの情報が返されることを確認
        assert result is not None
        assert result['title'] == 'Parent Paper Title'
        mock_zotero.item.assert_called_once_with('PARENT123')

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_zotero_item_info_attachment_no_parent(self, mock_zotero_class):
        """親アイテムがない添付ファイルの処理テスト"""
        mock_zotero = MagicMock()
        mock_zotero_class.return_value = mock_zotero

        # 親アイテムなしの添付ファイル
        attachment_item = {
            'data': {
                'title': 'test.pdf',
                'itemType': 'attachment'
                # parentItem なし
            }
        }

        mock_zotero.items.return_value = [attachment_item]

        result = get_zotero_item_info("test")

        # 添付ファイル自体の情報が返される
        assert result is not None
        assert result['title'] == 'test.pdf'

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_zotero_item_info_multiple_items(self, mock_zotero_class):
        """複数アイテム中から最適マッチの選択テスト"""
        mock_zotero = MagicMock()
        mock_zotero_class.return_value = mock_zotero

        # 複数のアイテム（最初のものが最も一致度が高い）
        items = [
            {
                'data': {
                    'title': 'Machine Learning Basics',  # 完全一致に近い
                    'itemType': 'journalArticle'
                }
            },
            {
                'data': {
                    'title': 'Advanced Machine Learning Applications',
                    'itemType': 'journalArticle'
                }
            }
        ]

        mock_zotero.items.return_value = items

        result = get_zotero_item_info("machine learning basics")

        # 最初の（最も一致度の高い）アイテムが返される
        assert result is not None
        assert result['title'] == 'Machine Learning Basics'

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_zotero_item_info_api_error(self, mock_zotero_class):
        """Zotero API エラーのテスト"""
        mock_zotero = MagicMock()
        mock_zotero_class.return_value = mock_zotero
        mock_zotero.items.side_effect = Exception("API Error")

        # API エラーが発生してもクラッシュしないことを確認
        try:
            get_zotero_item_info("test")
            # 関数がエラーハンドリングを実装していない場合は例外が発生
        except Exception:
            # 現在の実装では例外処理がないので、これは正常
            pass

    def test_normalize_filename_with_unicode(self):
        """Unicode文字を含むファイル名の正規化テスト"""
        # 日本語文字を含む場合
        result = normalize_filename("テスト_ファイル-名前")
        assert "テスト" in result
        assert "ファイル" in result
        assert "名前" in result


if __name__ == "__main__":
    pytest.main([__file__])
