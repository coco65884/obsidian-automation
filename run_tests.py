#!/usr/bin/env python3
"""
テスト実行スクリプト

使用方法:
    python run_tests.py                # 全テスト実行
    python run_tests.py keyword        # キーワード管理のテストのみ
    python run_tests.py pdf            # PDF処理のテストのみ
    python run_tests.py zotero         # Zotero統合のテストのみ
    python run_tests.py note           # ノート作成のテストのみ
    python run_tests.py main           # メイン処理のテストのみ
"""

import sys
import subprocess


def run_tests(test_target=None):
    """指定されたテストを実行"""

    base_cmd = ["python", "-m", "pytest"]

    if test_target:
        test_mapping = {
            'keyword': 'tests/test_keyword_manager.py',
            'pdf': 'tests/test_pdf_processor.py',
            'zotero': 'tests/test_zotero_integrator.py',
            'note': 'tests/test_obsidian_note_creator.py',
            'main': 'tests/test_main.py'
        }

        if test_target in test_mapping:
            base_cmd.append(test_mapping[test_target])
            print(f"実行中: {test_target} モジュールのテスト")
        else:
            print(f"未知のテスト対象: {test_target}")
            print("利用可能な対象: keyword, pdf, zotero, note, main")
            return 1
    else:
        print("実行中: 全てのテスト")

    try:
        result = subprocess.run(base_cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nテスト実行が中断されました")
        return 1
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
        return 1


def main():
    """メイン関数"""
    test_target = sys.argv[1] if len(sys.argv) > 1 else None

    print("Obsidian Automation テストスイート")
    print("=" * 50)

    exit_code = run_tests(test_target)

    if exit_code == 0:
        print("\n✅ 全てのテストが成功しました！")
    else:
        print("\n❌ いくつかのテストが失敗しました")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
