from obsidian_note_creator import (
    load_template, format_date, clean_filename, replace_zotero_placeholders,
    make_citation, make_authors_block, make_info_block, create_obsidian_note
)
import pytest
import tempfile
import os
from unittest.mock import patch, mock_open, Mock
from datetime import datetime
import sys

# テスト用にパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestObsidianNoteCreator:
    """Obsidianノート作成機能のテスト"""

    def test_load_template_success(self):
        """テンプレート読み込み成功のテスト"""
        template_content = "# {{title}}\n\n## 概要\n{{abstractNote}}"

        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("obsidian_note_creator.TEMPLATE_PATH", "test_template.md"):
                result = load_template()
                assert result == template_content

    def test_load_template_file_not_found(self):
        """テンプレートファイルが見つからない場合のテスト"""
        with patch("builtins.open", side_effect=FileNotFoundError("No such file")):
            with patch("obsidian_note_creator.TEMPLATE_PATH", "nonexistent.md"):
                result = load_template()
                assert result is None

    def test_format_date_basic_formats(self):
        """基本的な日付フォーマットのテスト"""
        # 年月日形式
        assert format_date("2023-12-25", "YYYY-MM-DD") == "2023-12-25"
        assert format_date("2023-12-25", "YYYY") == "2023"
        assert format_date("2023-12-25", "MM") == "12"
        assert format_date("2023-12-25", "DD") == "25"

    def test_format_date_different_input_formats(self):
        """様々な入力形式のテスト"""
        # スラッシュ区切り
        assert format_date("2023/12/25", "YYYY-MM-DD") == "2023-12-25"

        # 年のみ
        assert format_date("2023", "YYYY") == "2023"

        # ISO形式
        assert format_date("2023-12-25T10:30:00", "YYYY-MM-DD") == "2023-12-25"

    def test_format_date_invalid_input(self):
        """無効な日付入力のテスト"""
        # 無効な日付文字列はそのまま返される
        assert format_date("invalid-date", "YYYY-MM-DD") == "invalid-date"

        # 空文字列
        assert format_date("", "YYYY-MM-DD") == ""

        # None
        assert format_date(None, "YYYY-MM-DD") == ""

    def test_clean_filename_basic(self):
        """基本的なファイル名クリーニングのテスト"""
        # 正常なファイル名
        assert clean_filename("Normal File Name") == "Normal File Name"

        # 特殊文字を含む
        assert clean_filename("File[Name]") == "FileName"
        assert clean_filename("File{Name}") == "FileName"
        assert clean_filename("File:Name") == "FileName"
        assert clean_filename("File|Name") == "FileName"

    def test_clean_filename_edge_cases(self):
        """エッジケースのテスト"""
        # 空文字列
        assert clean_filename("") == ""

        # None
        assert clean_filename(None) is None

        # 連続するスペース
        assert clean_filename("File   Name") == "File Name"

        # 前後のスペース
        assert clean_filename("  File Name  ") == "File Name"

    def test_replace_zotero_placeholders_basic(self):
        """基本的なZoteroプレースホルダー置換のテスト"""
        content = "Title: {{title}}\nAuthor: {{author}}\nYear: {{year}}"
        zotero_data = {
            'title': 'Test Paper',
            'creators': [{'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'}],
            'date': '2023-01-01'
        }

        result = replace_zotero_placeholders(content, zotero_data)

        assert "Test Paper" in result
        assert "John Doe" in result
        assert "2023" in result

    def test_replace_zotero_placeholders_liquid_format(self):
        """Liquid記法フォーマットのテスト"""
        content = "Date: {{date | format('YYYY-MM-DD')}}\nImport: {{importDate | format('YYYY')}}"
        zotero_data = {
            'date': '2023-01-01',
            'dateAdded': '2023-12-25T10:00:00Z'
        }

        result = replace_zotero_placeholders(content, zotero_data)

        assert "2023-01-01" in result
        assert "2023" in result

    def test_replace_zotero_placeholders_empty_data(self):
        """空のZoteroデータのテスト"""
        content = "Title: {{title}}"
        result = replace_zotero_placeholders(content, None)
        assert result == content

        result = replace_zotero_placeholders(content, {})
        assert "Title: " in result  # プレースホルダーは空文字列に置換される

    def test_make_citation_basic(self):
        """基本的な引用作成のテスト"""
        zotero_data = {
            'title': 'Test Paper',
            'creators': [{'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'}],
            'date': '2023-01-01',
            'DOI': '10.1000/test'
        }

        citation = make_citation(zotero_data)

        assert "Doe, John" in citation
        assert "Test Paper" in citation
        assert "https://doi.org/10.1000/test" in citation

    def test_make_citation_no_data(self):
        """データなしの引用作成のテスト"""
        citation = make_citation(None)
        assert "参考文献は手動で追加してください" in citation

        citation = make_citation({})
        assert "参考文献は手動で追加してください" in citation

    def test_make_citation_preprint(self):
        """プレプリントの引用作成のテスト"""
        zotero_data = {
            'title': 'Preprint Paper',
            'creators': [{'creatorType': 'author', 'firstName': 'Jane', 'lastName': 'Smith'}],
            'date': '2023-12-25',
            'itemType': 'preprint'
        }

        citation = make_citation(zotero_data)

        assert "Smith, Jane" in citation
        assert "arXiv" in citation
        assert "25 December 2023" in citation

    def test_make_authors_block_basic(self):
        """基本的な著者ブロック作成のテスト"""
        creators = [
            {'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'},
            {'creatorType': 'author', 'firstName': 'Jane', 'lastName': 'Smith'}
        ]

        result = make_authors_block(creators)

        assert "- Doe, John" in result
        assert "- Smith, Jane" in result

    def test_make_authors_block_empty(self):
        """空の著者リストのテスト"""
        result = make_authors_block([])
        assert result == "  - ''"

        result = make_authors_block(None)
        assert result == "  - ''"

    def test_make_info_block_basic(self):
        """基本的な情報ブロック作成のテスト"""
        zotero_data = {
            'title': 'Test Paper',
            'creators': [
                {'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'},
                {'creatorType': 'author', 'firstName': 'Jane', 'lastName': 'Smith'}
            ],
            'date': '2023-01-01',
            'citekey': 'doe2023test',
            'itemType': 'journalArticle'
        }

        result = make_info_block(zotero_data)

        assert "**FirstAuthor**: Doe, John" in result
        assert "**Author**: Smith, Jane" in result
        assert "**Title**: Test Paper" in result
        assert "**Year**: 2023" in result
        assert "**Citekey**: doe2023test" in result
        assert "**itemType**: journalArticle" in result

    @patch("obsidian_note_creator.load_template")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.join")
    def test_create_obsidian_note_with_template(self, mock_join, mock_file, mock_load_template):
        """テンプレートを使用したノート作成のテスト"""
        # モックの設定
        mock_join.return_value = "test_note.md"
        mock_load_template.return_value = "# {{title}}\n\n>[!Overview]+\n\n{{info_block}}"

        pdf_path = "/path/to/test.pdf"
        zotero_data = {
            'title': 'Test Paper',
            'creators': [{'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'}]
        }
        summary_text = "This is a test summary."

        # 関数実行
        create_obsidian_note(pdf_path, zotero_data, summary_text)

        # ファイルが書き込まれたことを確認
        mock_file.assert_called_once_with(
            "test_note.md", 'w', encoding='utf-8')

        # 書き込み内容を確認
        written_content = mock_file().write.call_args[0][0]
        assert "Test Paper" in written_content
        assert "This is a test summary" in written_content

    @patch("obsidian_note_creator.load_template")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_obsidian_note_without_template(self, mock_file, mock_load_template):
        """テンプレートなしのノート作成のテスト"""
        # テンプレート読み込み失敗をシミュレート
        mock_load_template.return_value = None

        with patch("os.path.join", return_value="test_note.md"):
            pdf_path = "/path/to/test.pdf"
            zotero_data = {'title': 'Test Paper'}
            summary_text = "Test summary"

            create_obsidian_note(pdf_path, zotero_data, summary_text)

            # デフォルトノートが作成されることを確認
            written_content = mock_file().write.call_args[0][0]
            assert "# test" in written_content
            assert "Test summary" in written_content

    @patch("obsidian_note_creator.load_template")
    @patch("builtins.open", side_effect=IOError("Write error"))
    def test_create_obsidian_note_write_error(self, mock_file, mock_load_template):
        """ファイル書き込みエラーのテスト"""
        mock_load_template.return_value = "# Test Template"

        with patch("os.path.join", return_value="test_note.md"):
            # エラーが発生してもクラッシュしないことを確認
            try:
                create_obsidian_note("/path/to/test.pdf", {}, "summary")
            except Exception:
                pytest.fail(
                    "create_obsidian_note should handle write errors gracefully")

    def test_replace_zotero_placeholders_yaml_frontmatter(self):
        """YAMLフロントマターの処理テスト"""
        content = """---
title: "{{title}}"
author: {{author}}
---

# Content"""

        zotero_data = {
            'title': 'Test Paper',
            'creators': [{'creatorType': 'author', 'firstName': 'John', 'lastName': 'Doe'}]
        }

        result = replace_zotero_placeholders(content, zotero_data)

        # YAMLフロントマターのtitleから引用符が除去されることを確認
        assert 'title: Test Paper' in result
        assert 'title: "Test Paper"' not in result

    def test_replace_zotero_placeholders_obsidian_links(self):
        """Obsidianリンクの処理テスト"""
        content = "Link: [[{{{title}}}.pdf]]"
        zotero_data = {'title': 'Test Paper'}

        result = replace_zotero_placeholders(content, zotero_data)

        # 波括弧が除去されることを確認
        assert "[[Test Paper.pdf]]" in result
        assert "{" not in result and "}" not in result

    def test_replace_zotero_placeholders_overview_insertion(self):
        """Overview挿入のテスト"""
        content = ">[!Overview]+"

        result = replace_zotero_placeholders(content, {})

        # [!Overview]がそのまま残ることを確認
        assert ">[!Overview]+" in result
