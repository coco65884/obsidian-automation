import os
import glob
from config import ZOTERO_USER_ID, PDF_FOLDER, NOTE_FOLDER
from pdf_processor import extract_text_from_pdf, summarize_text
from zotero_integrator import get_zotero_item_info
from obsidian_note_creator import create_obsidian_note


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
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            print(f"エラー: {pdf_path} からテキストを抽出できませんでした。")
            return False

        # 2. テキストを要約
        summary = summarize_text(pdf_text)
        if not summary:
            print(f"エラー: {pdf_path} の要約を生成できませんでした。")
            return False

        # 3. Zoteroから関連情報を取得
        file_name_without_ext = os.path.splitext(os.path.basename(pdf_path))[0]
        zotero_data = get_zotero_item_info(file_name_without_ext)
        if not zotero_data:
            print(
                f"注意: Zoteroで '{file_name_without_ext}' に関連するアイテムが見つかりませんでした。")

        # 4. Obsidianノートを作成
        create_obsidian_note(pdf_path, zotero_data, summary)
        return True

    except Exception as e:
        print(f"PDF処理中に予期せぬエラーが発生しました: {e}")
        return False


def main():
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


if __name__ == "__main__":
    main()
