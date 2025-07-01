from zotero_integrator import get_pdf_metadata_from_zotero
import pytest
import os
from unittest.mock import patch, Mock, MagicMock
import sys

# テスト用にパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestZoteroIntegrator:
    """Zotero統合機能のテスト"""

    def test_get_pdf_metadata_from_zotero_no_credentials(self):
        """Zotero認証情報がない場合のテスト"""
        with patch.dict(os.environ, {}, clear=True):
            result = get_pdf_metadata_from_zotero("test.pdf")
            assert result is None

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_from_zotero_success(self, mock_zotero_class):
        """Zotero連携成功のテスト"""
        # モックのZoteroインスタンスを設定
        mock_zotero_instance = Mock()
        mock_zotero_class.return_value = mock_zotero_instance

        # 検索結果のモック
        mock_search_results = [
            {
                'key': 'TEST123',
                'data': {
                    'title': 'Test Paper',
                    'creators': [
                        {'creatorType': 'author',
                            'firstName': 'John', 'lastName': 'Doe'}
                    ],
                    'date': '2023',
                    'DOI': '10.1000/test',
                    'url': 'https://example.com/paper',
                    'abstractNote': 'This is a test abstract',
                    'tags': [{'tag': 'machine learning'}, {'tag': 'AI'}],
                    'itemType': 'journalArticle'
                }
            }
        ]

        mock_zotero_instance.items.return_value = mock_search_results

        # 環境変数をモック
        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'test_library_id',
            'ZOTERO_API_KEY': 'test_api_key'
        }):
            result = get_pdf_metadata_from_zotero("Test Paper.pdf")

            # 結果の検証
            assert result is not None
            assert result['title'] == 'Test Paper'
            assert result['DOI'] == '10.1000/test'
            assert len(result['creators']) == 1
            assert result['creators'][0]['firstName'] == 'John'
            assert result['creators'][0]['lastName'] == 'Doe'

            # Zoteroが正しく呼ばれたことを確認
            mock_zotero_class.assert_called_once_with(
                'test_library_id', 'user', 'test_api_key')
            mock_zotero_instance.items.assert_called_once()

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_from_zotero_no_results(self, mock_zotero_class):
        """検索結果がない場合のテスト"""
        mock_zotero_instance = Mock()
        mock_zotero_class.return_value = mock_zotero_instance

        # 空の検索結果
        mock_zotero_instance.items.return_value = []

        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'test_library_id',
            'ZOTERO_API_KEY': 'test_api_key'
        }):
            result = get_pdf_metadata_from_zotero("NonExistent.pdf")
            assert result is None

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_from_zotero_api_error(self, mock_zotero_class):
        """Zotero APIエラーのテスト"""
        mock_zotero_instance = Mock()
        mock_zotero_class.return_value = mock_zotero_instance

        # API呼び出しでエラーが発生
        mock_zotero_instance.items.side_effect = Exception("API Error")

        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'test_library_id',
            'ZOTERO_API_KEY': 'test_api_key'
        }):
            result = get_pdf_metadata_from_zotero("Test.pdf")
            assert result is None

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_filename_without_extension(self, mock_zotero_class):
        """拡張子なしのファイル名での検索テスト"""
        mock_zotero_instance = Mock()
        mock_zotero_class.return_value = mock_zotero_instance

        mock_search_results = [
            {
                'key': 'TEST123',
                'data': {
                    'title': 'Test Research Paper',
                    'creators': [],
                    'date': '2023'
                }
            }
        ]

        mock_zotero_instance.items.return_value = mock_search_results

        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'test_library_id',
            'ZOTERO_API_KEY': 'test_api_key'
        }):
            # 拡張子なしのファイル名でテスト
            result = get_pdf_metadata_from_zotero("Test Research Paper")

            assert result is not None
            assert result['title'] == 'Test Research Paper'

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_special_characters_in_filename(self, mock_zotero_class):
        """特殊文字を含むファイル名のテスト"""
        mock_zotero_instance = Mock()
        mock_zotero_class.return_value = mock_zotero_instance

        mock_search_results = [
            {
                'key': 'TEST123',
                'data': {
                    'title': 'Paper: A Study & Analysis [2023]',
                    'creators': [],
                    'date': '2023'
                }
            }
        ]

        mock_zotero_instance.items.return_value = mock_search_results

        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'test_library_id',
            'ZOTERO_API_KEY': 'test_api_key'
        }):
            result = get_pdf_metadata_from_zotero(
                "Paper_ A Study & Analysis [2023].pdf")

            assert result is not None
            assert result['title'] == 'Paper: A Study & Analysis [2023]'

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_multiple_results(self, mock_zotero_class):
        """複数の検索結果がある場合のテスト（最初の結果を返す）"""
        mock_zotero_instance = Mock()
        mock_zotero_class.return_value = mock_zotero_instance

        mock_search_results = [
            {
                'key': 'TEST123',
                'data': {
                    'title': 'First Paper',
                    'creators': [],
                    'date': '2023'
                }
            },
            {
                'key': 'TEST456',
                'data': {
                    'title': 'Second Paper',
                    'creators': [],
                    'date': '2022'
                }
            }
        ]

        mock_zotero_instance.items.return_value = mock_search_results

        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'test_library_id',
            'ZOTERO_API_KEY': 'test_api_key'
        }):
            result = get_pdf_metadata_from_zotero("Paper.pdf")

            # 最初の結果が返されることを確認
            assert result is not None
            assert result['title'] == 'First Paper'
            assert result['date'] == '2023'

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_incomplete_data(self, mock_zotero_class):
        """不完全なデータの場合のテスト"""
        mock_zotero_instance = Mock()
        mock_zotero_class.return_value = mock_zotero_instance

        # 一部のフィールドが欠けているデータ
        mock_search_results = [
            {
                'key': 'TEST123',
                'data': {
                    'title': 'Incomplete Paper',
                    # creators, date などが欠けている
                }
            }
        ]

        mock_zotero_instance.items.return_value = mock_search_results

        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'test_library_id',
            'ZOTERO_API_KEY': 'test_api_key'
        }):
            result = get_pdf_metadata_from_zotero("Incomplete.pdf")

            # 欠けているフィールドがあってもエラーにならないことを確認
            assert result is not None
            assert result['title'] == 'Incomplete Paper'
            assert 'creators' in result or result.get('creators') is None
            assert 'date' in result or result.get('date') is None

    def test_get_pdf_metadata_empty_filename(self):
        """空のファイル名の場合のテスト"""
        result = get_pdf_metadata_from_zotero("")
        assert result is None

        result = get_pdf_metadata_from_zotero(None)
        assert result is None

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_zotero_import_error(self, mock_zotero_class):
        """Zoteroライブラリのインポートエラーのテスト"""
        # pyzoteroのインポートエラーをシミュレート
        with patch('zotero_integrator.zotero', None):
            result = get_pdf_metadata_from_zotero("test.pdf")
            assert result is None

    @patch('zotero_integrator.zotero.Zotero')
    def test_get_pdf_metadata_authentication_error(self, mock_zotero_class):
        """認証エラーのテスト"""
        # Zoteroインスタンス作成時に認証エラーが発生
        mock_zotero_class.side_effect = Exception("Authentication failed")

        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': 'invalid_library_id',
            'ZOTERO_API_KEY': 'invalid_api_key'
        }):
            result = get_pdf_metadata_from_zotero("test.pdf")
            assert result is None

    def test_environment_variable_handling(self):
        """環境変数の処理テスト"""
        # ZOTERO_LIBRARY_IDのみ設定されている場合
        with patch.dict(os.environ, {'ZOTERO_LIBRARY_ID': 'test_id'}, clear=True):
            result = get_pdf_metadata_from_zotero("test.pdf")
            assert result is None

        # ZOTERO_API_KEYのみ設定されている場合
        with patch.dict(os.environ, {'ZOTERO_API_KEY': 'test_key'}, clear=True):
            result = get_pdf_metadata_from_zotero("test.pdf")
            assert result is None

        # 両方とも空文字列の場合
        with patch.dict(os.environ, {
            'ZOTERO_LIBRARY_ID': '',
            'ZOTERO_API_KEY': ''
        }):
            result = get_pdf_metadata_from_zotero("test.pdf")
            assert result is None
