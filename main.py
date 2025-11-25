import os
import glob
import argparse
from config import ZOTERO_USER_ID, PDF_FOLDER, NOTE_FOLDER
from pdf_processor import extract_text_from_pdf, summarize_text
from zotero_integrator import get_zotero_item_info
from obsidian_note_creator import create_obsidian_note
from keywords_reconstructor import KeywordsReconstructor


def get_existing_notes():
    """Obsidian vault内の既存のノートファイル名を取得"""
    existing_notes = set()
    try:
        for md_file in glob.glob(os.path.join(NOTE_FOLDER, "*.md")):
            note_name = os.path.splitext(os.path.basename(md_file))[0]
            existing_notes.add(note_name)
        return existing_notes
    except Exception as e:
        print(f"既存ノートの取得中にエラーが発生しました: {e}")
        return set()


def process_pdf(pdf_path):
    """PDFを処理してノートを作成"""
    try:
        print(f"PDFを処理中: {pdf_path}")

        # 1. PDFからテキストを抽出
        try:
            pdf_text = extract_text_from_pdf(pdf_path)
            if not pdf_text:
                print(f"エラー: {pdf_path} からテキストを抽出できませんでした。")
                return False
        except Exception as e:
            print(f"PDF読み込みエラー: {e}")
            return False

        # 2. テキストを要約
        try:
            summary_data = summarize_text(pdf_text)
            if not summary_data:
                print(f"エラー: {pdf_path} の要約を生成できませんでした。")
                # 要約が失敗した場合でも、空の要約でノートを作成する
                summary_data = {
                    'summary': "要約の生成に失敗しました。手動で要約を追加してください。",
                    'abstract': '',
                    'publication': ''
                }
        except Exception as e:
            print(f"要約生成エラー: {e}")
            summary_data = {
                'summary': "要約の生成中にエラーが発生しました。手動で要約を追加してください。",
                'abstract': '',
                'publication': ''
            }

        # 3. Zoteroから関連情報を取得
        try:
            file_name_without_ext = os.path.splitext(
                os.path.basename(pdf_path))[0]
            zotero_data = get_zotero_item_info(file_name_without_ext)
            if not zotero_data:
                print(f"注意: Zoteroで '{file_name_without_ext}' に関連する"
                      f"アイテムが見つかりませんでした。")
        except Exception as e:
            print(f"Zotero情報取得エラー: {e}")
            zotero_data = None

        # 4. Obsidianノートを作成
        try:
            create_obsidian_note(pdf_path, zotero_data, summary_data)
            return True
        except Exception as e:
            print(f"ノート作成エラー: {e}")
            return False

    except Exception as e:
        print(f"PDF処理中に予期せぬエラーが発生しました: {e}")
        return False


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Obsidian PDF自動化ツール')
    parser.add_argument('-k', '--keywords', action='store_true', 
                       help='キーワード再構成を実行する')
    args = parser.parse_args()

    print(f"Zotero User ID: {ZOTERO_USER_ID}")
    print(f"PDF Folder: {PDF_FOLDER}")
    print(f"Note Folder: {NOTE_FOLDER}")

    # PDFフォルダの存在確認
    if not os.path.exists(PDF_FOLDER):
        print(f"エラー: PDFフォルダ '{PDF_FOLDER}' が見つかりません。")
        return

    # 既存のノートを取得
    existing_notes = get_existing_notes()
    print(f"既存のノート数: {len(existing_notes)}")

    # PDFフォルダ内のPDFファイルを取得
    pdf_files = glob.glob(os.path.join(PDF_FOLDER, "*.pdf"))
    print(f"PDFフォルダ内のPDFファイル数: {len(pdf_files)}")

    processed_count = 0
    for pdf_path in pdf_files:
        pdf_name_without_ext = os.path.splitext(os.path.basename(pdf_path))[0]

        # 同名のノートが既に存在するかチェック
        if pdf_name_without_ext in existing_notes:
            print(f"スキップ: '{pdf_name_without_ext}' のノートは既に存在します。")
            continue

        # ノートが存在しない場合、処理を実行
        if process_pdf(pdf_path):
            processed_count += 1

    print(f"処理完了: {processed_count}個の新しいノートを作成しました。")

    # -kオプションが指定された場合のみキーワード再構成を実行
    if args.keywords:
        print("\n" + "="*50)
        print("キーワード再構成を開始します...")

        try:
            reconstructor = KeywordsReconstructor()
            success = reconstructor.reconstruct_keywords()

            if success:
                print("✅ キーワード再構成が正常に完了しました")
            else:
                print("❌ キーワード再構成に失敗しました")
        except Exception as e:
            print(f"❌ キーワード再構成中にエラーが発生しました: {e}")
    else:
        print("\nキーワード再構成はスキップされました。")
        print("キーワード再構成を実行するには -k オプションを使用してください。")


if __name__ == "__main__":
    main()
