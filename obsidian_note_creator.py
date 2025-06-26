import os
from config import NOTE_FOLDER, TEMPLATE_PATH


def load_template():
    """テンプレートファイルを読み込む"""
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"テンプレートファイルの読み込み中にエラーが発生しました: {e}")
        return None


def create_obsidian_note(pdf_path, zotero_data, summary_text):
    # PDFファイル名からノート名を決定 (拡張子なし)
    pdf_filename_with_ext = os.path.basename(pdf_path)
    note_title = os.path.splitext(pdf_filename_with_ext)[0]
    note_path = os.path.join(NOTE_FOLDER, f"{note_title}.md")

    # テンプレートを読み込み
    template_content = load_template()
    if not template_content:
        print("テンプレートファイルが見つからないため、デフォルトのノートを作成します。")
        # デフォルトのノート作成
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
        content += f"![[{pdf_filename_with_ext}]]\n\n"

        # 要約の追加
        content += "## 要約\n"
        content += summary_text if summary_text else "要約は生成されませんでした。\n"
        content += "\n"
    else:
        # テンプレートを使用してノートを作成
        content = template_content

        # タイトルを置換
        content = content.replace("{title}", note_title)

        # [!Overview]の部分に要約を挿入
        if "[!Overview]" in content:
            if summary_text:
                # [!Overview]を要約で置換
                content = content.replace("[!Overview]", summary_text)
            else:
                # 要約がない場合は[!Overview]を削除
                content = content.replace("[!Overview]", "要約は生成されませんでした。")

        # Zotero情報があれば、テンプレート内のプレースホルダーを置換
        if zotero_data:
            # タイトル
            if "{zotero_title}" in content:
                content = content.replace("{zotero_title}",
                                          zotero_data.get('title', 'N/A'))

            # 著者
            if "{zotero_authors}" in content:
                creators = zotero_data.get('creators', [])
                creator_names = [
                    f"{a.get('firstName', '')} {a.get('lastName', '')}"
                    for a in creators
                ]
                content = content.replace("{zotero_authors}",
                                          ', '.join(creator_names))

            # 発行年
            if "{zotero_date}" in content:
                content = content.replace("{zotero_date}",
                                          zotero_data.get('date', 'N/A'))

            # URL
            if "{zotero_url}" in content:
                content = content.replace("{zotero_url}",
                                          zotero_data.get('url', 'N/A'))

        # PDFファイル名を置換
        if "{pdf_filename}" in content:
            content = content.replace("{pdf_filename}", pdf_filename_with_ext)

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
