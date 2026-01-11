# Obsidian Automation

研究論文のPDFファイルを自動的に処理して、Obsidianノートを生成するPythonツールです。Zoteroからメタデータを取得、Google Gemini APIを使用した要約生成、キーワード管理機能を提供します。APIにはgemini-2.5-flashを利用するので基本無料(なはず)です。
<video src="https://github.com/user-attachments/assets/20cf22c6-3504-4726-9719-4a9f61d7449c"></video>

## 🚀 主な機能

- **PDF自動処理**: PDFファイルからテキストを抽出
- **AI要約生成**: Google Gemini APIを使用した論文要約の自動生成
- **Zotero統合**: Zoteroライブラリから論文メタデータを自動取得
- **キーワード管理**: 機械学習キーワードの自動抽出・管理
- **Obsidianノート生成**: 構造化されたMarkdownノートの自動作成
- **テンプレート対応**: カスタマイズ可能なノートテンプレート

## 📋 前提条件

- Python 3.11 以上
- [uv](https://github.com/astral-sh/uv) パッケージマネージャー
- Google Gemini API アクセス
- Zotero アカウント
- Obsidian (ノート管理用)

## 💡 準備

### Obsidianの準備
1. Obsidianをインストール
2. Obsidianを起動しVault(ワークスペース)を作成
3. Vault内に論文を格納するディレクトリとノートを格納するディレクトリを作成
4. Preference/Community pluginsから便利なプラグインを導入(推奨)
   * Callout Manager: 自分オリジナルのコールアウトを作成できます。このプログラムを使う場合、Overviewを登録しておくと見やすくなります。
   * Dataveiw: Noteの情報を元にtableが作成できます。Samples/Dashboard.mdに例があります。(設定でEnable Javascripts queriesをオンにしてください。)
   * PDF++: 論文のスクショを撮ってリンクを貼り付けたり、引用して自分なりのメモを残したりできます。
5. Samples/Dashboard.mdを自分のVaultに追加し、二箇所ある`YOUR_NOTE_FOLDER_HERE`の部分をノートを格納するディレクトリへのパスに置換(推奨)
6. .obsidian/snippetsにSamples/paper.cssを追加し、Preference/Appearance/CSS snippetsからcssを適用(任意)

### Zoteroの準備
1. Zoteroをインストール
2. ZoteroからPDFを転送するプラグイン`ZotMoov`を追加
3. ZotMoovの出力先をObsidianの準備の3で追加した論文を格納するディレクトリに指定
4. Preferences/General/File Renaming/Customize Filename Formatで{{ title truncate="100" }}を指定

## 🛠 環境設定

### 1. uvのインストール

uvがインストールされていない場合は、以下のコマンドでインストールしてください：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrcß

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Homebrew (macOS)
brew install uv

# pipx経由
pipx install uv
```

### 2. プロジェクトのクローンと依存関係のインストール

```bash
# リポジトリをクローン
git clone https://github.com/coco65884/obsidian-automation
cd obsidian-automation

# 依存関係をインストール
uv sync
```

### 3. 仮想環境作成とアクティベート

```bash
# 仮想環境の作成
uv venv

# 仮想環境をアクティベート
source .venv/bin/activate

# Windowsの場合
# .venv\Scripts\activate
```

### 4. 環境変数ファイル（.env）の作成

プロジェクトルートに `.env` ファイルを作成し、以下の環境変数を設定してください。：

```bash
# .env ファイルの例
ZOTERO_API_KEY=your_zotero_api_key_here
ZOTERO_USER_ID=your_zotero_user_id_here
GEMINI_API_KEY=your_gemini_api_key_here
PDF_FOLDER=/path/to/your/pdf/folder
NOTE_FOLDER=/path/to/your/obsidian/vault/folder
TEMPLATE_PATH=./template.md
```

## 🔑 APIキーの取得方法

### Google Gemini API キー

1. [Google AI Studio](https://aistudio.google.com/) にアクセス
2. Googleアカウントでログイン
3. 「Get API key」をクリック
4. 「Create API key」を選択
5. プロジェクトを選択（新規作成も可能）
6. 生成されたAPIキーをコピーして `.env` ファイルの `GEMINI_API_KEY` に設定

### Zotero API キーとユーザーID

#### APIキーの取得：
1. [Zotero](https://www.zotero.org/) にログイン
2. [Settings > Feeds/API](https://www.zotero.org/settings/keys) にアクセス
3. 「Create new private key」をクリック
4. 必要な権限を設定：
   - **Personal Library**: Read access
   - **Default Group Permissions**: Read access (グループライブラリを使用する場合)
5. 「Save Key」をクリック
6. 生成されたAPIキーをコピーして `.env` ファイルの `ZOTERO_API_KEY` に設定

#### ユーザーIDの取得：
1. Zoteroにログイン後、[Feeds/API settings](https://www.zotero.org/settings/keys) ページにアクセス
2. ページ上部に表示される「Your userID for use in API calls is XXXXXX」の数字をコピー
3. この数字を `.env` ファイルの `ZOTERO_USER_ID` に設定

## 📁 ディレクトリ構成

```
obsidian-automation/
├── main.py                     # メイン実行ファイル
├── config.py                   # 設定ファイル
├── pdf_processor.py            # PDF処理
├── zotero_integrator.py        # Zotero統合
├── keyword_manager.py          # キーワード管理
├── obsidian_note_creator.py    # ノート作成
├── template.md                 # ノートテンプレート
├── prompt/                     # プロンプトファイル
│   ├── custom_prompt.md        # AI要約用カスタムプロンプト
│   └── keywords_reconstruction.md # キーワード再構成用プロンプト
├── keywords.json               # キーワードデータベース
├── .env                        # 環境変数ファイル（要作成）
├── tests/                      # テストファイル
├── pyproject.toml              # プロジェクト設定
└── README.md                   # このファイル
```

## 🚦 使用方法

### 基本的な使用方法

```bash
# 仮想環境をアクティベート（まだの場合）
source .venv/bin/activate

# メインスクリプトを実行
python main.py
```

このコマンドを実行すると：
1. `PDF_FOLDER` 内のPDFファイルをスキャン
2. 各PDFからテキストを抽出
3. Google Gemini APIで要約を生成
4. Zoteroからメタデータを取得
5. キーワードを抽出・管理
6. 構造化されたObsidianノートを `NOTE_FOLDER` に作成

## 🎨 カスタマイズ

### ノートテンプレートの編集

`template.md` ファイルを編集することで、生成されるノートの構造をカスタマイズできます。利用可能なプレースホルダー：

- `{{title}}` - 論文タイトル
- `{{authors}}` - 著者一覧
- `{{date}}` - 発表日
- `{{DOI}}` - DOI
- `{{abstractNote}}` - アブストラクト
- `{{publicationTitle}}` - 出版物名
- その他多数のZoteroフィールド

### AI要約プロンプトの編集

`prompt/custom_prompt.md` ファイルを編集することで、AI要約の生成方法をカスタマイズできます。

### キーワード管理

キーワードは `keywords.json` で管理されます。新しいキーワードは自動的に追加されますが、手動で編集することも可能です。
また、`prompt/keywords_reconstruction.md`ではキーワード再構成時の指示を変更することが可能です。

## 🧪 テスト

### テストの実行

```bash
# 仮想環境をアクティベート（まだの場合）
source .venv/bin/activate

# 全てのテストを実行
pytest tests

# 詳細な出力でテスト実行
pytest tests -v

# 特定のテストファイルのみ実行
pytest tests/test_keyword_manager.py -v

# カバレッジレポート付きでテスト実行
pytest tests --cov=. --cov-report=html
```

### テストファイル一覧

- `tests/test_keyword_manager.py` - キーワード管理機能のテスト
- `tests/test_pdf_processor.py` - PDF処理機能のテスト
- `tests/test_zotero_integrator.py` - Zotero統合機能のテスト
- `tests/test_obsidian_note_creator.py` - ノート作成機能のテスト
- `tests/test_main.py` - メイン処理のテスト

## 🐛 トラブルシューティング

### よくある問題

1. **APIキーエラー**
   - `.env` ファイルが正しく作成されているか確認
   - APIキーが有効かブラウザで確認

2. **PDFテキスト抽出エラー**
   - PDFファイルが破損していないか確認
   - PyPDF2で処理できない形式の可能性

3. **Zotero接続エラー**
   - インターネット接続を確認
   - ZoteroのAPIキーとユーザーIDが正しいか確認

4. **フォルダパスエラー**
   - `PDF_FOLDER` と `NOTE_FOLDER` のパスが存在するか確認
   - パスに特殊文字が含まれていないか確認

### ログの確認

プログラム実行時に出力されるログを確認することで、問題の原因を特定できます。

## 🤝 開発に参加する

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b your_git_ID/issue#number`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin your_git_ID/issue#number`)
5. プルリクエストを作成

### 開発環境の設定

```bash
# 開発用依存関係を含めてインストール
uv sync --group dev

# 仮想環境をアクティベート
source .venv/bin/activate
```

## 📞 サポート

問題が発生した場合は、[Issues](https://github.com/coco65884/obsidian-automation/issues) でお知らせください。
