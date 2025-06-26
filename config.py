# config.py (または main スクリプトの先頭)
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # .env ファイルから環境変数を読み込む

ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY")
ZOTERO_USER_ID = os.getenv("ZOTERO_USER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH")

required_vars = [
    ZOTERO_API_KEY, ZOTERO_USER_ID, GEMINI_API_KEY, OBSIDIAN_VAULT_PATH
]
if not all(required_vars):
    print("エラー: 環境変数が正しく設定されていません。")
    print("ZOTERO_API_KEY, ZOTERO_USER_ID, GEMINI_API_KEY, "
          "OBSIDIAN_VAULT_PATH を .env ファイルで設定してください。")
    exit(1)

# Gemini API の設定
genai.configure(api_key=GEMINI_API_KEY)
