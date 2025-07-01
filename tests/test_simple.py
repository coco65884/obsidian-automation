"""
簡単なテストファイル - テスト環境の動作確認用
"""


def test_basic():
    """基本的なテスト"""
    assert 1 + 1 == 2


def test_string():
    """文字列テスト"""
    assert "hello" + " world" == "hello world"


class TestBasic:
    """基本的なテストクラス"""

    def test_list(self):
        """リストのテスト"""
        test_list = [1, 2, 3]
        assert len(test_list) == 3
        assert 2 in test_list

    def test_dict(self):
        """辞書のテスト"""
        test_dict = {"key": "value"}
        assert test_dict["key"] == "value"
        assert "key" in test_dict
