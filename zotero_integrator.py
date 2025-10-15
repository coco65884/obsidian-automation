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

    # 検索結果のタイトルを表示（デバッグ用）
    if items:
        print("検索結果のタイトル一覧:")
        for i, item in enumerate(items[:5]):  # 最初の5件のみ表示
            try:
                # pyzoteroライブラリの型定義問題回避
                # type: ignore
                item_data = item['data'] if 'data' in item else {}
                item_title = item_data.get('title', 'タイトルなし')
                item_type = item_data.get('itemType', '不明')
                print(f"  {i+1}. [{item_type}] {item_title}")
                print(f"      正規化: '{normalize_filename(item_title)}'")
            except Exception as e:
                print(f"  {i+1}. エラー: {e}")

    # より柔軟なマッチング戦略
    matched_item = None

    # 1. 完全一致を探す
    for item in items:
        try:
            item_data = item.get('data', {})
            item_title = item_data.get('title', '')
            if normalize_filename(item_title) == normalized_search_title:
                print(f"完全一致でヒット: {item_title}")
                matched_item = item
                break
        except Exception as e:
            print(f"完全一致検索でエラー: {e}")
            continue

    # 2. 部分一致を探す（完全一致が見つからない場合）
    if not matched_item:
        for item in items:
            try:
                item_data = item.get('data', {})
                item_title = item_data.get('title', '')
                normalized_item_title = normalize_filename(item_title)

                # より柔軟な部分一致（両方向）
                if (normalized_search_title in normalized_item_title or
                        normalized_item_title in normalized_search_title):
                    print(f"部分一致でヒット: {item_title}")
                    matched_item = item
                    break

                # キーワードベースの一致も試す
                search_words = normalized_search_title.split()
                item_words = normalized_item_title.split()
                common_words = set(search_words) & set(item_words)
                # 共通単語が十分ある場合
                min_words = min(3, len(search_words) // 2)
                if len(common_words) >= min_words:
                    common_str = ', '.join(common_words)
                    print(f"キーワード一致でヒット: {item_title} "
                          f"(共通単語: {common_str})")
                    matched_item = item
                    break

            except Exception as e:
                print(f"部分一致検索でエラー: {e}")
                continue

    # マッチしたアイテムを処理
    if matched_item:
        try:
            item_data = matched_item.get('data', {})

            # 添付ファイルなら親アイテムを取得
            if (item_data.get('itemType') == 'attachment' and
                    'parentItem' in item_data):
                parent_id = item_data['parentItem']
                parent_item = z.item(parent_id)
                if parent_item and 'data' in parent_item:
                    print('親アイテム（論文本体）を取得しました')
                    return parent_item['data']

            # それ以外はそのまま返す
            return item_data

        except Exception as e:
            print(f"アイテム処理でエラー: {e}")
            return None

    print("Zoteroでタイトル一致するアイテムが見つかりませんでした。")
    return None

# 使用例:
# pdf_filename = "Example Document.pdf"
# zotero_info = get_zotero_item_info(os.path.splitext(pdf_filename)[0])
# if zotero_info:
#     print("Zotero情報:", zotero_info.get('title'))
# else:
#     print("Zoteroで関連するアイテムが見つかりませんでした。")
