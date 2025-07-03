from keywords_reconstructor import KeywordsReconstructor
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# テスト用にパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestKeywordsReconstructor:
    """KeywordsReconstructorクラスのテスト"""

    @pytest.fixture
    def temp_keywords_file(self):
        """テスト用の一時キーワードファイル"""
        test_data = {
            "categories": {
                "field": ["CV", "NLP", "RL"],
                "task": ["Classification", "Detection", "Segmentation"],
                "method": ["SelfSupervisedLearning", "EnsembleLearning"],
                "architecture": ["CNN", "Transformer", "ViT"]
            },
            "custom_keywords": ["TestKeyword1", "TestKeyword2"],
            "aliases": {
                "ComputerVision": "CV",
                "VisionTransformer": "ViT"
            },
            "prohibited_keywords": ["AI", "MachineLearning", "DeepLearning"]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         delete=False, encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name

        yield temp_file

        # クリーンアップ
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.fixture
    def temp_prompt_file(self):
        """テスト用の一時プロンプトファイル"""
        test_prompt = """機械学習の論文に自動で付けられたタグを精査してください。
以下のルールに従ってください。
- 出力はJSONファイルのみで、それ以外の文字列は含まないでください。
- 出力は入力のJSONファイルと同じ形式にしてください。

精査するJSONファイルは以下のとおりです。
{JSON_SECTION}
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                         delete=False, encoding='utf-8') as f:
            f.write(test_prompt)
            temp_file = f.name

        yield temp_file

        # クリーンアップ
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.fixture
    def temp_note_files(self):
        """テスト用の一時ノートファイル"""
        temp_dir = tempfile.mkdtemp()
        note_files = []

        # テスト用ノートファイル1
        note1_content = """---
title: "Test Paper 1"
---

# Introduction

This paper discusses #CV and #ObjectDetection methods.

# Method

We use #CNN and #VisionTransformer for processing.
"""
        note1_path = os.path.join(temp_dir, "test_paper_1.md")
        with open(note1_path, 'w', encoding='utf-8') as f:
            f.write(note1_content)
        note_files.append(note1_path)

        # テスト用ノートファイル2
        note2_content = """---
title: "Test Paper 2"
---

# Abstract

This work focuses on #NLP and #MachineLearning approaches.

# Results

The #AI system shows good performance.
"""
        note2_path = os.path.join(temp_dir, "test_paper_2.md")
        with open(note2_path, 'w', encoding='utf-8') as f:
            f.write(note2_content)
        note_files.append(note2_path)

        yield temp_dir, note_files

        # クリーンアップ
        import shutil
        shutil.rmtree(temp_dir)

    @pytest.fixture
    @patch('keywords_reconstructor.NOTE_FOLDER', '/test/note/folder')
    @patch('keywords_reconstructor.GEMINI_API_KEY', 'test_api_key')
    def keywords_reconstructor(self, temp_keywords_file, temp_prompt_file):
        """テスト用のKeywordsReconstructorインスタンス"""
        with patch('keywords_reconstructor.genai.configure'):
            reconstructor = KeywordsReconstructor(
                keywords_file=temp_keywords_file,
                reconstruction_prompt_file=temp_prompt_file
            )
            return reconstructor

    def test_initialization(self, keywords_reconstructor):
        """初期化テスト"""
        assert keywords_reconstructor.keywords_file is not None
        assert keywords_reconstructor.prompt_file is not None
        assert keywords_reconstructor.note_folder == '/test/note/folder'

    def test_load_keywords_success(self, keywords_reconstructor):
        """キーワード読み込み成功テスト"""
        keywords_data = keywords_reconstructor.load_keywords()

        assert keywords_data is not None
        assert "categories" in keywords_data
        assert "aliases" in keywords_data
        assert "prohibited_keywords" in keywords_data
        assert len(keywords_data["categories"]["field"]) == 3

    def test_load_keywords_file_not_found(self):
        """キーワードファイルが見つからない場合のテスト"""
        with patch('keywords_reconstructor.NOTE_FOLDER', '/test/folder'):
            with patch('keywords_reconstructor.GEMINI_API_KEY', 'test_key'):
                with patch('keywords_reconstructor.genai.configure'):
                    reconstructor = KeywordsReconstructor(
                        keywords_file="nonexistent.json"
                    )
                    result = reconstructor.load_keywords()
                    assert result == {}

    def test_load_reconstruction_prompt_success(self, keywords_reconstructor):
        """プロンプト読み込み成功テスト"""
        prompt = keywords_reconstructor.load_reconstruction_prompt()

        assert prompt is not None
        assert "{JSON_SECTION}" in prompt
        assert "精査してください" in prompt

    def test_load_reconstruction_prompt_file_not_found(self):
        """プロンプトファイルが見つからない場合のテスト"""
        with patch('keywords_reconstructor.NOTE_FOLDER', '/test/folder'):
            with patch('keywords_reconstructor.GEMINI_API_KEY', 'test_key'):
                with patch('keywords_reconstructor.genai.configure'):
                    reconstructor = KeywordsReconstructor(
                        reconstruction_prompt_file="nonexistent.md"
                    )
                    result = reconstructor.load_reconstruction_prompt()
                    assert result == ""

    def test_create_reconstruction_prompt(self, keywords_reconstructor):
        """再構成プロンプト作成テスト"""
        test_keywords = {
            "categories": {"field": ["CV", "NLP"]},
            "custom_keywords": ["Test"],
            "aliases": {"ComputerVision": "CV"},
            "prohibited_keywords": ["AI"]
        }

        prompt = keywords_reconstructor.create_reconstruction_prompt(
            test_keywords)

        assert prompt is not None
        assert "{JSON_SECTION}" not in prompt  # 置換されているはず
        # JSONがインデント付きで出力されるため、実際の形式で確認
        assert '"field": [' in prompt
        assert '"CV"' in prompt
        assert '"NLP"' in prompt

    def test_create_reconstruction_prompt_no_template(self):
        """プロンプトテンプレートがない場合のテスト"""
        with patch('keywords_reconstructor.NOTE_FOLDER', '/test/folder'):
            with patch('keywords_reconstructor.GEMINI_API_KEY', 'test_key'):
                with patch('keywords_reconstructor.genai.configure'):
                    reconstructor = KeywordsReconstructor(
                        reconstruction_prompt_file="nonexistent.md"
                    )
                    result = reconstructor.create_reconstruction_prompt({})
                    assert result == ""

    @patch('keywords_reconstructor.genai.list_models')
    def test_get_available_models_success(self, mock_list_models,
                                          keywords_reconstructor):
        """利用可能モデル取得成功テスト"""
        # モックモデル設定
        mock_model1 = MagicMock()
        mock_model1.name = "models/gemini-2.5-flash"
        mock_model1.supported_generation_methods = ["generateContent"]

        mock_model2 = MagicMock()
        mock_model2.name = "models/gemini-1.5-pro"
        mock_model2.supported_generation_methods = ["generateContent"]

        mock_list_models.return_value = [mock_model1, mock_model2]

        result = keywords_reconstructor.get_available_models()

        assert "gemini-2.5-flash" in result
        assert "gemini-1.5-pro" in result

    @patch('keywords_reconstructor.genai.list_models')
    def test_get_available_models_exception(self, mock_list_models,
                                            keywords_reconstructor):
        """モデル取得例外テスト"""
        mock_list_models.side_effect = Exception("API error")

        result = keywords_reconstructor.get_available_models()
        assert result == []

    @patch('keywords_reconstructor.genai.GenerativeModel')
    def test_call_gemini_api_success(self, mock_model_class,
                                     keywords_reconstructor):
        """Gemini API呼び出し成功テスト"""
        # モック設定
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"test": "response"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        # get_available_modelsをモック
        with patch.object(keywords_reconstructor, 'get_available_models',
                          return_value=["gemini-2.5-flash"]):
            result = keywords_reconstructor.call_gemini_api("test prompt")

        assert result == '{"test": "response"}'
        mock_model.generate_content.assert_called_once_with("test prompt")

    @patch('keywords_reconstructor.genai.GenerativeModel')
    def test_call_gemini_api_fallback_model(self, mock_model_class,
                                            keywords_reconstructor):
        """Gemini API代替モデル使用テスト"""
        # モック設定
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"fallback": "response"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        # get_available_modelsをモック（目的のモデルなし）
        with patch.object(keywords_reconstructor, 'get_available_models',
                          return_value=["gemini-1.5-flash"]):
            result = keywords_reconstructor.call_gemini_api(
                "test prompt", "gemini-2.5-flash")

        assert result == '{"fallback": "response"}'

    @patch('keywords_reconstructor.genai.GenerativeModel')
    def test_call_gemini_api_no_models(self, mock_model_class,
                                       keywords_reconstructor):
        """利用可能モデルなしテスト"""
        with patch.object(keywords_reconstructor, 'get_available_models',
                          return_value=[]):
            result = keywords_reconstructor.call_gemini_api("test prompt")

        assert result == ""

    def test_parse_json_response_valid_json(self, keywords_reconstructor):
        """有効JSON解析テスト"""
        response_text = '{"categories": {"field": ["CV"]}, "deleted": ["AI"]}'
        result = keywords_reconstructor.parse_json_response(response_text)

        assert result == {"categories": {"field": ["CV"]}, "deleted": ["AI"]}

    def test_parse_json_response_with_markdown(self, keywords_reconstructor):
        """マークダウン付きJSON解析テスト"""
        response_text = """Here is the result:

```json
{
  "categories": {
    "field": ["CV", "NLP"]
  },
  "deleted": ["AI"]
}
```

Thank you!"""
        result = keywords_reconstructor.parse_json_response(response_text)

        assert "categories" in result
        assert result["categories"]["field"] == ["CV", "NLP"]

    def test_parse_json_response_invalid_json(self, keywords_reconstructor):
        """無効JSON解析テスト"""
        response_text = "This is not JSON at all"
        result = keywords_reconstructor.parse_json_response(response_text)

        assert result == {}

    def test_update_keywords_file_success(self, keywords_reconstructor):
        """キーワードファイル更新成功テスト"""
        test_data = {"test": "data"}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         delete=False) as temp_file:
            temp_path = temp_file.name

        # 一時的にファイルパスを変更
        original_path = keywords_reconstructor.keywords_file
        keywords_reconstructor.keywords_file = temp_path

        try:
            result = keywords_reconstructor.update_keywords_file(test_data)
            assert result is True

            # ファイル内容確認
            with open(temp_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            assert saved_data == test_data
        finally:
            keywords_reconstructor.keywords_file = original_path
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_markdown_files(self, keywords_reconstructor, temp_note_files):
        """Markdownファイル一覧取得テスト"""
        temp_dir, note_files = temp_note_files

        # note_folderを一時ディレクトリに変更
        original_folder = keywords_reconstructor.note_folder
        keywords_reconstructor.note_folder = temp_dir

        try:
            result = keywords_reconstructor.get_markdown_files()
            assert len(result) == 2
            assert all(f.endswith('.md') for f in result)
        finally:
            keywords_reconstructor.note_folder = original_folder

    def test_get_markdown_files_no_folder(self, keywords_reconstructor):
        """存在しないフォルダのテスト"""
        # note_folderを存在しないパスに変更
        original_folder = keywords_reconstructor.note_folder
        keywords_reconstructor.note_folder = "/nonexistent/path"

        try:
            result = keywords_reconstructor.get_markdown_files()
            assert result == []
        finally:
            keywords_reconstructor.note_folder = original_folder

    def test_update_note_keywords(self, keywords_reconstructor,
                                  temp_note_files):
        """ノートキーワード更新テスト"""
        temp_dir, note_files = temp_note_files
        test_file = note_files[0]

        deleted_keywords = ["MachineLearning"]
        aliases = {"ComputerVision": "CV", "VisionTransformer": "ViT"}

        result = keywords_reconstructor.update_note_keywords(
            test_file, deleted_keywords, aliases)

        # 変更があったはず
        assert result is True

        # ファイル内容確認
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # CV → ComputerVision、ViT → VisionTransformerに置換されているはず
        # 略称→正式名称の統一
        assert "#ComputerVision" in content
        assert "#CV" not in content

    def test_update_note_keywords_no_changes(self, keywords_reconstructor,
                                             temp_note_files):
        """変更なしの場合のテスト"""
        temp_dir, note_files = temp_note_files
        test_file = note_files[0]

        deleted_keywords = ["NonExistentKeyword"]
        aliases = {"SomeOther": "Keyword"}

        result = keywords_reconstructor.update_note_keywords(
            test_file, deleted_keywords, aliases)

        # 変更がないはず
        assert result is False

    def test_update_all_notes(self, keywords_reconstructor, temp_note_files):
        """全ノート更新テスト"""
        temp_dir, note_files = temp_note_files

        # note_folderを一時ディレクトリに変更
        original_folder = keywords_reconstructor.note_folder
        keywords_reconstructor.note_folder = temp_dir

        try:
            deleted_keywords = ["AI"]
            aliases = {"ComputerVision": "CV"}

            result = keywords_reconstructor.update_all_notes(
                deleted_keywords, aliases)

            # 少なくとも1つのファイルが更新されたはず
            assert result >= 1
        finally:
            keywords_reconstructor.note_folder = original_folder

    @patch.object(KeywordsReconstructor, 'call_gemini_api')
    @patch.object(KeywordsReconstructor, 'update_keywords_file')
    @patch.object(KeywordsReconstructor, 'update_all_notes')
    def test_reconstruct_keywords_success(self, mock_update_notes,
                                          mock_update_file, mock_api_call,
                                          keywords_reconstructor):
        """キーワード再構成成功テスト"""
        # モック設定
        mock_api_call.return_value = '''
        {
          "categories": {
            "field": ["CV", "NLP"],
            "task": ["Classification"],
            "method": ["SelfSupervisedLearning"],
            "architecture": ["CNN"]
          },
          "custom_keywords": [],
          "aliases": {"ComputerVision": "CV"},
          "prohibited_keywords": ["AI"],
          "deleted": ["OldKeyword"]
        }
        '''
        mock_update_file.return_value = True
        mock_update_notes.return_value = 2

        result = keywords_reconstructor.reconstruct_keywords()

        assert result is True
        mock_api_call.assert_called_once()
        mock_update_file.assert_called_once()
        mock_update_notes.assert_called_once()

    def test_reconstruct_keywords_no_keywords_data(self,
                                                   keywords_reconstructor):
        """キーワードデータ読み込み失敗テスト"""
        with patch.object(keywords_reconstructor, 'load_keywords',
                          return_value={}):
            result = keywords_reconstructor.reconstruct_keywords()
            assert result is False

    @patch.object(KeywordsReconstructor, 'call_gemini_api')
    def test_reconstruct_keywords_api_failure(self, mock_api_call,
                                              keywords_reconstructor):
        """API呼び出し失敗テスト"""
        mock_api_call.return_value = ""

        result = keywords_reconstructor.reconstruct_keywords()
        assert result is False

    @patch.object(KeywordsReconstructor, 'call_gemini_api')
    def test_reconstruct_keywords_json_parse_failure(self, mock_api_call,
                                                     keywords_reconstructor):
        """JSON解析失敗テスト"""
        mock_api_call.return_value = "Invalid JSON response"

        result = keywords_reconstructor.reconstruct_keywords()
        assert result is False
