import os
from config import NOTE_FOLDER


def create_obsidian_note(pdf_path, zotero_data, summary_text):
    # PDFファイル名からノート名を決定 (拡張子なし)
    pdf_filename_with_ext = os.path.basename(pdf_path)
    note_title = os.path.splitext(pdf_filename_with_ext)[0]
    note_path = os.path.join(NOTE_FOLDER, f"{note_title}.md")

    # ノートコンテンツの生成
    content = f"# {note_title}\n\n"

    # Zotero情報があれば追加
    if zotero_data:
        content += "## 文献情報\n"
        content += f"- **タイトル:** {zotero_data.get('title', 'N/A')}\n"
        creators = zotero_data.get('creators', [])
        creator_names = [
            f"{a.get('firstName', '')} {a.get('lastName', '')}"
            for a in creators
        ]
        content += f"- **著者:** {', '.join(creator_names)}\n"
        content += f"- **発行年:** {zotero_data.get('date', 'N/A')}\n"
        content += f"- **URL:** {zotero_data.get('url', 'N/A')}\n"
        content += "\n"

    # PDFへのリンク（Obsidianの埋め込み形式）
    content += "## 元のPDF\n"
    content += f"![[{pdf_filename_with_ext}]]\n\n"  # ObsidianのPDF埋め込み

    # 要約の追加
    content += "## 要約\n"
    content += summary_text if summary_text else "要約は生成されませんでした。\n"
    content += "\n"

    # その他必要なメタデータやテンプレート内容を追加

    try:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Obsidianノートが作成されました: {note_path}")
    except Exception as e:
        print(f"Obsidianノートの作成中にエラーが発生しました: {e}")

# 使用例:
# create_obsidian_note(
#     "path/to/your/Example Document.pdf",
#     {'title': 'Example Document',
#      'creators': [{'firstName': 'John', 'lastName': 'Doe'}]},
#     "これはPDFの要約です。"
# )
