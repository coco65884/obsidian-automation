import os
import re
from config import NOTE_FOLDER, TEMPLATE_PATH
from datetime import datetime


def load_template():
    """テンプレートファイルを読み込む"""
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"テンプレートファイルの読み込み中にエラーが発生しました: {e}")
        return None


def format_date(date_string, format_pattern):
    """日付文字列を指定されたフォーマットに変換"""
    if not date_string:
        return ''

    try:
        # Liquid記法からPythonの日付フォーマットに変換
        python_format = format_pattern
        python_format = python_format.replace('YYYY', '%Y')
        python_format = python_format.replace('MM', '%m')
        python_format = python_format.replace('DD', '%d')
        python_format = python_format.replace('HH', '%H')
        python_format = python_format.replace('mm', '%M')
        python_format = python_format.replace('ss', '%S')

        # 様々な日付形式に対応
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y',
            '%Y-%m',
        ]

        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                break
            except ValueError:
                continue

        if parsed_date:
            formatted_result = parsed_date.strftime(python_format)
            print(f"日付フォーマット変換: {date_string} -> {formatted_result}")
            print(f"使用パターン: {format_pattern}")
            return formatted_result
        else:
            # パースできない場合は元の文字列を返す
            print(f"日付のパースに失敗: {date_string}")
            return date_string
    except Exception as e:
        print(f"日付フォーマット変換エラー: {e}")
        return date_string


def clean_filename(filename):
    """ファイル名として使用できない文字を削除またはエスケープ"""
    if not filename:
        return filename

    # Obsidianリンクで問題となる文字を置換
    unsafe_chars = ['[', ']', '|', '#', '^', '\\', '{', '}']
    for char in unsafe_chars:
        filename = filename.replace(char, '')

    # コロンを削除（YAMLで問題となる）
    filename = filename.replace(':', '')

    # 連続するスペースを単一スペースに
    filename = ' '.join(filename.split())

    return filename.strip()


def replace_zotero_placeholders(content, zotero_data):
    """Zoteroの{{}}記法をAPIデータで置換"""
    if not zotero_data:
        return content

    print("Zoteroデータで置換を開始...")
    print(f"利用可能なZoteroフィールド: {list(zotero_data.keys())}")

    # Liquid記法のフォーマット機能を処理
    # {{importDate | format("YYYY-MM-DD")}} のような形式
    format_pattern = r'\{\{(\w+)\s*\|\s*format\(["\']([^"\']+)["\']\)\}\}'

    def replace_format_placeholder(match):
        field_name = match.group(1)
        format_spec = match.group(2)

        # フィールド名のマッピング
        field_mapping = {
            'importDate': 'dateAdded',
            'date': 'date',
        }

        actual_field = field_mapping.get(field_name, field_name)
        field_value = zotero_data.get(actual_field, '')

        # importDateが空の場合は現在の日付を使用
        if field_name == 'importDate' and not field_value:
            field_value = datetime.now().strftime('%Y-%m-%d')
            print(f"importDateが空のため現在の日付を使用: {field_value}")

        if field_value:
            formatted_value = format_date(field_value, format_spec)
            print(f"フォーマット置換: {match.group(0)} -> {formatted_value}")
            return formatted_value
        else:
            print(f"フィールドが見つかりません: {field_name}")
            return ''

    content = re.sub(format_pattern, replace_format_placeholder, content)

    # 基本的なフィールドの置換
    title = zotero_data.get('title', '')
    clean_title = clean_filename(title)

    replacements = {
        '{{title}}': clean_title,  # クリーンなタイトルを使用
        '{{date}}': zotero_data.get('date', ''),
        '{{year}}': (zotero_data.get('date', '')[:4]
                     if zotero_data.get('date') else ''),
        '{{url}}': zotero_data.get('url', ''),
        '{{DOI}}': zotero_data.get('DOI', ''),
        '{{abstractNote}}': zotero_data.get('abstractNote', ''),
        '{{publicationTitle}}': zotero_data.get('publicationTitle', ''),
        '{{journalAbbreviation}}': zotero_data.get('journalAbbreviation', ''),
        '{{volume}}': zotero_data.get('volume', ''),
        '{{issue}}': zotero_data.get('issue', ''),
        '{{pages}}': zotero_data.get('pages', ''),
        '{{publisher}}': zotero_data.get('publisher', ''),
        '{{place}}': zotero_data.get('place', ''),
        '{{ISBN}}': zotero_data.get('ISBN', ''),
        '{{ISSN}}': zotero_data.get('ISSN', ''),
        '{{language}}': zotero_data.get('language', ''),
        '{{series}}': zotero_data.get('series', ''),
        '{{seriesNumber}}': zotero_data.get('seriesNumber', ''),
        '{{edition}}': zotero_data.get('edition', ''),
        '{{numPages}}': zotero_data.get('numPages', ''),
        '{{accessDate}}': zotero_data.get('accessDate', ''),
        '{{archive}}': zotero_data.get('archive', ''),
        '{{archiveLocation}}': zotero_data.get('archiveLocation', ''),
        '{{libraryCatalog}}': zotero_data.get('libraryCatalog', ''),
        '{{callNumber}}': zotero_data.get('callNumber', ''),
        '{{rights}}': zotero_data.get('rights', ''),
        '{{extra}}': zotero_data.get('extra', ''),
        '{{itemType}}': zotero_data.get('itemType', ''),
        '{{citekey}}': zotero_data.get('citekey', ''),
        '{{importDate}}': zotero_data.get('dateAdded', ''),
        '{{tags}}': ', '.join([tag.get('tag', '')
                              for tag in zotero_data.get('tags', [])]),
        '{{collections}}': ', '.join([col.get('name', '')
                                      for col in zotero_data.get('collections', [])]),
    }

    # 著者の処理
    creators = zotero_data.get('creators', [])
    if creators:
        # 著者名のリストを作成
        author_names = []
        for creator in creators:
            if creator.get('creatorType') == 'author':
                first_name = creator.get('firstName', '')
                last_name = creator.get('lastName', '')
                if first_name and last_name:
                    author_names.append(f"{first_name} {last_name}")
                elif last_name:
                    author_names.append(last_name)
                elif first_name:
                    author_names.append(first_name)

        replacements['{{authors}}'] = ', '.join(author_names)
        replacements['{{author}}'] = ', '.join(author_names)

        # 最初の著者のみ
        if author_names:
            replacements['{{firstAuthor}}'] = author_names[0]
        else:
            replacements['{{firstAuthor}}'] = ''
    else:
        replacements['{{authors}}'] = ''
        replacements['{{author}}'] = ''
        replacements['{{firstAuthor}}'] = ''

    # 置換を実行
    print(f"置換処理開始 - 対象プレースホルダー数: {len(replacements)}")
    for placeholder, value in replacements.items():
        if placeholder in content:
            print(f"置換実行: {placeholder} -> '{value}'")
            content = content.replace(placeholder, str(value))
        else:
            if placeholder == '{{title}}':
                print("{{title}}が見つかりません。コンテンツにtitleが含まれているか確認:")
                if 'title' in content:
                    title_lines = [line for line in content.split(
                        '\n') if 'title' in line]
                    print(f"titleを含む行: {title_lines}")
                else:
                    print("コンテンツにtitleが含まれていません")

    # YAMLフロントマターのtitle行から引用符と波括弧を除去（{{title}}置換後）
    # "タイトル" または {タイトル} -> タイトル の形式に修正
    title_yaml_pattern = r'^(\s*title:\s*)["\']*[{]*([^"\'{}]+)[}]*["\']*(.*)$'
    if re.search(title_yaml_pattern, content, flags=re.MULTILINE):
        print("YAML frontmatterのtitle行から引用符・波括弧を除去中...")
        before_match = re.search(
            title_yaml_pattern, content, flags=re.MULTILINE)
        if before_match:
            print(f"修正前のtitle行: {before_match.group(0)}")
        content = re.sub(title_yaml_pattern, r'\1\2\3',
                         content, flags=re.MULTILINE)
        after_match = re.search(r'^(\s*title:\s*)(.+)$',
                                content, flags=re.MULTILINE)
        if after_match:
            print(f"修正後のtitle行: {after_match.group(0)}")

    # Obsidianリンク内の波括弧を除去
    # [[{タイトル}.pdf]] -> [[タイトル.pdf]]
    obsidian_link_pattern = r'\[\[{([^}]+)}\.(pdf|md)\]\]'
    if re.search(obsidian_link_pattern, content):
        print("Obsidianリンクから波括弧を除去中...")
        before_links = re.findall(obsidian_link_pattern, content)
        print(f"修正前のリンク: {before_links}")
        content = re.sub(obsidian_link_pattern, r'[[\1.\2]]', content)
        after_links = re.findall(r'\[\[([^]]+\.(?:pdf|md))\]\]', content)
        print(f"修正後のリンク: {after_links}")

    # 正規表現を使用した高度な置換
    # {{authors:lastName}} のような形式に対応
    author_pattern = r'\{\{authors:(\w+)\}\}'
    if creators:
        author_fields = []
        for creator in creators:
            if creator.get('creatorType') == 'author':
                # 動的にフィールド名を取得
                field_value = creator.get('\\1', '')
                if field_value:
                    author_fields.append(field_value)
        content = re.sub(author_pattern, ', '.join(author_fields), content)
    else:
        content = re.sub(author_pattern, '', content)

    # テンプレート固有の置換
    # {%- for creator in creators -%} のようなLiquid記法を処理
    if '{%- for creator in creators -%}' in content:
        if creators:
            creator_lines = []
            for creator in creators:
                if creator.get('creatorType') == 'author':
                    first_name = creator.get('firstName', '')
                    last_name = creator.get('lastName', '')
                    creator_lines.append(f'  - "{last_name}, {first_name}"')
            content = content.replace(
                '{%- for creator in creators -%}\n    - "{{creator.lastName}}, {{creator.firstName}}"\n  {%- endfor %}', '\n'.join(creator_lines))
        else:
            content = content.replace(
                '{%- for creator in creators -%}\n    - "{{creator.lastName}}, {{creator.firstName}}"\n  {%- endfor %}', '')

    # {%- if abstractNote %} のような条件分岐を処理
    if '{%- if abstractNote %}' in content:
        if zotero_data.get('abstractNote'):
            content = content.replace(
                '{%- if abstractNote %}\n\n{%- endif -%}', zotero_data.get('abstractNote', ''))
        else:
            content = content.replace(
                '{%- if abstractNote %}\n\n{%- endif -%}', '')

    # {{bibliography.slice(4)}} のような特殊な記法を処理
    if '{{bibliography.slice(4)}}' in content:
        citation = make_citation(zotero_data)
        content = content.replace('{{bibliography.slice(4)}}', citation)

    # {% for type, creators in creators | groupby("creatorType") %} のような複雑な記法を処理
    if '{% for type, creators in creators | groupby("creatorType") %}' in content:
        if creators:
            creator_info = []
            for creator in creators:
                creator_type = creator.get('creatorType', 'unknown')
                first_name = creator.get('firstName', '')
                last_name = creator.get('lastName', '')
                name = creator.get('name', '')

                if name:
                    creator_info.append(
                        f'> **{creator_type.capitalize()}**: {name}')
                elif last_name and first_name:
                    creator_info.append(
                        f'> **{creator_type.capitalize()}**: {last_name}, {first_name}')
                elif last_name:
                    creator_info.append(
                        f'> **{creator_type.capitalize()}**: {last_name}')
                elif first_name:
                    creator_info.append(
                        f'> **{creator_type.capitalize()}**: {first_name}')

            # 複雑なLiquid記法を置換
            content = re.sub(r'{% for type, creators in creators \| groupby\("creatorType"\) %}-%}.*?{%- endfor %}',
                             '\n'.join(creator_info), content, flags=re.DOTALL)
        else:
            content = re.sub(
                r'{% for type, creators in creators \| groupby\("creatorType"\) %}-%}.*?{%- endfor %}', '', content, flags=re.DOTALL)

    # authors_blockの置換
    if '{{authors_block}}' in content:
        content = content.replace('{{authors_block}}', make_authors_block(
            zotero_data.get('creators', [])))

    # info_blockの置換
    if '{{info_block}}' in content:
        content = content.replace(
            '{{info_block}}', make_info_block(zotero_data))

    # デバッグ: {{title}}が残っているかチェック
    if '{{title}}' in content:
        print("警告: {{title}}が置換されていません")
        print("元のタイトル:", title)
        print("クリーンなタイトル:", clean_title)
    else:
        print(f"{{title}}の置換が完了しました: '{title}' -> '{clean_title}'")

    return content


def make_citation(zotero_data):
    """Zoteroデータから引用形式を生成"""
    if not zotero_data:
        return "<!-- 参考文献は手動で追加してください -->"

    # 著者名を取得（姓、名の順）
    creators = zotero_data.get('creators', [])
    author_names = []
    for creator in creators:
        if creator.get('creatorType') == 'author':
            first = creator.get('firstName', '')
            last = creator.get('lastName', '')
            if first and last:
                author_names.append(f"{last}, {first}")
            elif last:
                author_names.append(last)
            elif first:
                author_names.append(first)

    # 基本情報を取得
    title = zotero_data.get('title', '')
    date = zotero_data.get('date', '')
    year = date[:4] if date else ''
    doi = zotero_data.get('DOI', '')
    url = zotero_data.get('url', '')
    item_type = zotero_data.get('itemType', '')

    # 引用形式を構築（実際のノートの形式に合わせる）
    citation_parts = []

    # 著者名（最初の著者のみ）
    if author_names:
        first_author = author_names[0]
        if len(author_names) > 1:
            # 他の著者名を取得
            other_authors = []
            for i in range(1, len(author_names)):
                name_parts = author_names[i].split(', ')
                if len(name_parts) == 2:
                    other_authors.append(name_parts[1] + ' ' + name_parts[0])
                else:
                    other_authors.append(author_names[i])

            authors_str = first_author + ', ' + ', '.join(other_authors)
        else:
            authors_str = first_author

        citation_parts.append(authors_str)

    # タイトル（引用符付き）
    if title:
        citation_parts.append(f"'{title}'")

    # 出版情報
    if item_type == 'preprint':
        citation_parts.append('arXiv')
        if date:
            month_names = ['', 'January', 'February', 'March', 'April', 'May',
                           'June', 'July', 'August', 'September', 'October',
                           'November', 'December']
            date_parts = date.split('-')
            day = date_parts[2]
            month = month_names[int(date_parts[1])]
            citation_parts.append(f"{day} {month} {year}")

    # DOIまたはURL
    if doi:
        citation_parts.append(
            f"[https://doi.org/{doi}](https://doi.org/{doi})")
    elif url:
        citation_parts.append(f"[{url}]({url})")

    if citation_parts:
        return '. '.join(citation_parts) + '.'
    else:
        return "<!-- 参考文献は手動で追加してください -->"


def make_authors_block(creators):
    if not creators:
        return "  - ''"
    lines = []
    for creator in creators:
        if creator.get('creatorType') == 'author':
            last = creator.get('lastName', '')
            first = creator.get('firstName', '')
            if last or first:
                lines.append(f'  - {last}, {first}')
    return '\n'.join(lines) if lines else "  - ''"


def make_info_block(zotero_data):
    creators = zotero_data.get('creators', [])
    lines = []

    # 著者を処理（FirstAuthor:: と Author:: の形式）
    first_author = True
    for creator in creators:
        if creator.get('creatorType') == 'author':
            last = creator.get('lastName', '')
            first = creator.get('firstName', '')
            name = creator.get('name', '')

            if name:
                author_name = name
            elif last and first:
                author_name = f"{last}, {first}"
            elif last:
                author_name = last
            elif first:
                author_name = first
            else:
                continue

            if first_author:
                lines.append(f'> **FirstAuthor**: {author_name}')
                first_author = False
            else:
                lines.append(f'> **Author**: {author_name}')

    # その他の情報
    lines.append(f'> **Title**: {zotero_data.get("title", "")}')
    year = zotero_data.get("date", "")
    if year:
        lines.append(f'> **Year**: {year[:4]}')
    if zotero_data.get("citekey"):
        lines.append(f'> **Citekey**: {zotero_data.get("citekey", "")}')
    if zotero_data.get("itemType"):
        lines.append(f'> **itemType**: {zotero_data.get("itemType", "")}')

    return '\n'.join(lines)


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

        # >[!Overview]の部分に要約を挿入
        if ">[!Overview]+" in content:
            if summary_text:
                # 要約の各行の先頭に > を付ける
                summary_lines = summary_text.split('\n')
                formatted_summary_lines = []
                for line in summary_lines:
                    if line.strip():  # 空行でない場合
                        if not line.startswith('>'):
                            formatted_summary_lines.append(f"> {line}")
                        else:
                            formatted_summary_lines.append(line)
                    else:  # 空行の場合
                        formatted_summary_lines.append("> ")

                formatted_summary = '\n'.join(formatted_summary_lines)

                # [!Overview]+の下に要約を挿入
                content = content.replace(
                    ">[!Overview]+", f">[!Overview]+\n{formatted_summary}")
            else:
                # 要約がない場合は[!Overview]はそのまま残し、下にメッセージを追加
                content = content.replace(
                    ">[!Overview]+", ">[!Overview]+\n> 要約は生成されませんでした。")

        # Zoteroの{{}}記法を置換
        content = replace_zotero_placeholders(content, zotero_data)

        # 古いプレースホルダーもサポート（後方互換性のため）
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
