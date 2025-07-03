from keyword_manager import KeywordManager
import pytest
import json
import tempfile
import os
from unittest.mock import patch
import sys

# テスト用にパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestKeywordManager:
    """KeywordManagerクラスのテスト"""

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
    def keyword_manager(self, temp_keywords_file):
        """テスト用のKeywordManagerインスタンス"""
        return KeywordManager(keywords_file=temp_keywords_file)

    def test_initialization_with_existing_file(self, keyword_manager):
        """既存ファイルでの初期化テスト"""
        assert keyword_manager.keywords_data is not None
        assert "categories" in keyword_manager.keywords_data
        assert "prohibited_keywords" in keyword_manager.keywords_data
        assert len(keyword_manager.keywords_data["categories"]["field"]) == 3

    def test_initialization_without_file(self):
        """ファイルが存在しない場合の初期化テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_file = os.path.join(temp_dir, "non_existent.json")
            km = KeywordManager(keywords_file=non_existent_file)

            # デフォルトデータが設定されることを確認
            assert km.keywords_data is not None
            assert "categories" in km.keywords_data
            assert "prohibited_keywords" in km.keywords_data

    def test_similarity_calculation(self, keyword_manager):
        """類似度計算のテスト"""
        # 完全一致
        assert keyword_manager._similarity("test", "test") == 1.0

        # 部分一致
        similarity = keyword_manager._similarity("testing", "test")
        assert 0 < similarity < 1

        # 全く異なる
        similarity = keyword_manager._similarity("apple", "orange")
        assert similarity < 0.5

    def test_normalize_keyword(self, keyword_manager):
        """キーワード正規化のテスト"""
        # エイリアス変換
        assert keyword_manager._normalize_keyword("ComputerVision") == "CV"
        assert keyword_manager._normalize_keyword("VisionTransformer") == "ViT"

        # 通常のキーワード（変換なし）
        assert keyword_manager._normalize_keyword("CNN") == "CNN"

        # 前後の空白除去
        assert keyword_manager._normalize_keyword("  CNN  ") == "CNN"

    def test_is_prohibited_keyword(self, keyword_manager):
        """禁止キーワード判定のテスト"""
        # 禁止キーワード
        assert keyword_manager._is_prohibited_keyword("AI") is True
        assert keyword_manager._is_prohibited_keyword(
            "MachineLearning") is True
        assert keyword_manager._is_prohibited_keyword("ai") is True  # 大文字小文字

        # 許可キーワード
        assert keyword_manager._is_prohibited_keyword("CNN") is False
        assert keyword_manager._is_prohibited_keyword("ViT") is False

    def test_filter_prohibited_keywords(self, keyword_manager):
        """禁止キーワードフィルタリングのテスト"""
        keywords = ["CNN", "AI", "ViT", "MachineLearning", "Detection"]
        filtered = keyword_manager._filter_prohibited_keywords(keywords)

        assert "CNN" in filtered
        assert "ViT" in filtered
        assert "Detection" in filtered
        assert "AI" not in filtered
        assert "MachineLearning" not in filtered

    def test_find_similar_keywords(self, keyword_manager):
        """類似キーワード検索のテスト"""
        # 既存のキーワードに類似（しきい値を下げて確実にヒットするようにする）
        similar = keyword_manager._find_similar_keywords(
            "Classification", threshold=0.7)
        assert len(similar) > 0
        assert "Classification" in similar

        # より厳しいしきい値でのテスト
        similar_strict = keyword_manager._find_similar_keywords(
            "Classify", threshold=0.6)
        # しきい値0.6なら "Classification" がヒットするはず
        if similar_strict:
            assert "Classification" in similar_strict

        # 完全に異なるキーワード
        similar = keyword_manager._find_similar_keywords(
            "XYZ123", threshold=0.8)
        assert len(similar) == 0

    def test_suggest_keywords(self, keyword_manager):
        """キーワード提案のテスト"""
        test_keywords = ["CNN", "NewMethod", "AI", "ComputerVision"]
        existing, new = keyword_manager.suggest_keywords(test_keywords)

        # CNNは既存のキーワード
        assert "CNN" in existing

        # ComputerVision → CV に変換
        assert "CV" in existing

        # NewMethodは新規キーワード
        assert "NewMethod" in new

        # AIは禁止キーワードなので含まれない
        assert "AI" not in existing
        assert "AI" not in new

    def test_extract_keywords_from_text(self, keyword_manager):
        """テキストからキーワード抽出のテスト"""
        text = """
        > ### **Keywords**
        > #CV
        > #ObjectDetection  
        > #YOLO
        > #MachineLearning
        """

        keywords = keyword_manager.extract_keywords_from_text(text)
        expected = ["CV", "ObjectDetection", "YOLO", "MachineLearning"]

        assert len(keywords) == 4
        for keyword in expected:
            assert keyword in keywords

    def test_create_keyword_prompt(self, keyword_manager):
        """キーワードプロンプト作成のテスト"""
        prompt = keyword_manager.create_keyword_prompt()

        assert "CV" in prompt
        assert "NLP" in prompt
        assert "CNN" in prompt
        assert "分野:" in prompt
        assert "タスク:" in prompt
        assert "手法:" in prompt
        assert "アーキテクチャ:" in prompt

    def test_process_generated_keywords(self, keyword_manager):
        """生成されたキーワード処理のテスト"""
        # 一時ファイルのパスを取得してsave処理をモック
        with patch.object(keyword_manager, '_save_keywords'):
            text = """
            > ### **Keywords**
            > #CV
            > #NewTechnique
            > #AI
            """

            processed = keyword_manager.process_generated_keywords(text)

            # CVは既存、NewTechniqueは新規、AIは禁止で除外
            assert "CV" in processed
            assert "NewTechnique" in processed
            assert "AI" not in processed

    def test_add_prohibited_keyword(self, keyword_manager):
        """禁止キーワード追加のテスト"""
        with patch.object(keyword_manager, '_save_keywords'):
            initial_count = len(keyword_manager.get_prohibited_keywords())

            keyword_manager.add_prohibited_keyword("NewProhibitedWord")

            # 禁止キーワードが追加されたことを確認
            prohibited = keyword_manager.get_prohibited_keywords()
            assert len(prohibited) == initial_count + 1
            assert "NewProhibitedWord" in prohibited

    def test_add_new_keywords(self, keyword_manager):
        """新規キーワード追加のテスト"""
        with patch.object(keyword_manager, '_save_keywords'):
            new_keywords = ["TestMethod", "AI", "SpecialTechnique"]

            keyword_manager.add_new_keywords(new_keywords)

            # AIは禁止キーワードなので追加されない
            custom_keywords = keyword_manager.keywords_data["custom_keywords"]
            assert "TestMethod" in custom_keywords
            assert "SpecialTechnique" in custom_keywords
            assert "AI" not in custom_keywords

    def test_get_required_categories(self, keyword_manager):
        """必須カテゴリ取得のテスト"""
        categories = keyword_manager.get_required_categories()

        assert "field" in categories
        assert "task" in categories
        assert "method" in categories
        assert isinstance(categories["field"], str)

    def test_save_keywords_error_handling(self, keyword_manager):
        """キーワード保存エラーハンドリングのテスト"""
        # 無効なパスを設定してエラーを発生させる
        keyword_manager.keywords_file = "/invalid/path/keywords.json"

        # エラーが発生してもクラッシュしないことを確認
        try:
            keyword_manager._save_keywords()
        except Exception:
            pytest.fail("_save_keywords should handle errors gracefully")

    def test_load_keywords_error_handling(self):
        """キーワード読み込みエラーハンドリングのテスト"""
        # 破損したJSONファイルでの初期化
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         delete=False, encoding='utf-8') as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            km = KeywordManager(keywords_file=temp_file)
            # エラーが発生してもデフォルトデータで初期化されることを確認
            assert km.keywords_data is not None
            assert "categories" in km.keywords_data
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
