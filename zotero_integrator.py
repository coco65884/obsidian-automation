from pyzotero import zotero
from config import ZOTERO_USER_ID, ZOTERO_API_KEY
import re


def normalize_filename(filename):
    """ファイル名を正規化（大文字小文字、スペース、ハイフンなどを統一）"""
    # 小文字に変換
    normalized = filename.lower()
    # スペース、ハイフン、アンダースコアを統一
    normalized = re.sub(r'[_\-\s]+', ' ', normalized)
    # 複数のスペースを単一のスペースに
    normalized = re.sub(r'\s+', ' ', normalized)
    # 前後のスペースを削除
    normalized = normalized.strip()
    return normalized


def get_zotero_item_info(file_name_without_ext):
    z = zotero.Zotero(ZOTERO_USER_ID, 'user', ZOTERO_API_KEY)
    search_title = file_name_without_ext.strip()
    normalized_search_title = normalize_filename(search_title)
    print(f"Zoteroタイトル検索: '{search_title}' (正規化: '{normalized_search_title}')")

    # タイトルで部分一致検索
    items = z.items(q=search_title)
    print(f"Zotero検索ヒット件数: {len(items)}")

    # 完全一致・部分一致で最初にヒットしたものを探す
    for item in items:
        item_title = item['data'].get('title', '')
        if (normalize_filename(item_title) == normalized_search_title or
                normalized_search_title in normalize_filename(item_title)):
            print(f"ヒット: {item_title}")
            # 添付ファイルなら親アイテムを取得
            if (item['data'].get('itemType') == 'attachment' and
                    'parentItem' in item['data']):
                parent_id = item['data']['parentItem']
                parent_item = z.item(parent_id)
                if parent_item and 'data' in parent_item:
                    print('親アイテム（論文本体）を取得しました')
                    return parent_item['data']
            # それ以外はそのまま返す
            return item['data']

    print("Zoteroでタイトル一致するアイテムが見つかりませんでした。")
    return None

# 使用例:
# pdf_filename = "Example Document.pdf"
# zotero_info = get_zotero_item_info(os.path.splitext(pdf_filename)[0])
# if zotero_info:
#     print("Zotero情報:", zotero_info.get('title'))
# else:
#     print("Zoteroで関連するアイテムが見つかりませんでした。")
