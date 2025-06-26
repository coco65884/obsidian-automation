from pyzotero import zotero
import os


def get_zotero_item_info(file_name_without_ext):
    z = zotero.Zotero(ZOTERO_USER_ID, 'user', ZOTERO_API_KEY)
    items = z.items()

    for item in items:
        # 添付ファイルをチェックしてPDFファイル名と一致するか確認
        if 'data' in item and 'attachments' in item['data']:
            for attachment in item['data']['attachments']:
                if 'filename' in attachment and attachment['filename'].startswith(file_name_without_ext):
                    # 関連する親アイテム（論文など）の情報を取得
                    if 'parentItem' in attachment['data']:
                        parent_id = attachment['data']['parentItem']
                        parent_item = z.item(parent_id)
                        if parent_item:
                            return parent_item['data']
    return None

# 使用例:
# pdf_filename = "Example Document.pdf"
# zotero_info = get_zotero_item_info(os.path.splitext(pdf_filename)[0])
# if zotero_info:
#     print("Zotero情報:", zotero_info.get('title'))
# else:
#     print("Zoteroで関連するアイテムが見つかりませんでした。")
