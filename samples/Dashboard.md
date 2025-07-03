読んでない論文リスト
```dataview 
LIST
FROM "YOUR_NOTE_FOLDER_HERE"
WHERE rating=0
SORT file.name ASC

```

評価済み論文一覧
```dataviewjs
const pages = dv.pages('"YOUR_NOTE_FOLDER_HERE"').where(p => p.rating);

dv.table(
    ["タイトル", "星評価", "コメント"],
    await Promise.all(pages.sort(p => -p.rating).map(async p => {
        // ファイルの内容を取得
        let commentsSection = "";
        
        try {
            const file = app.vault.getAbstractFileByPath(p.file.path);
            if (file) {
                const content = await app.vault.read(file);
                
                if (content && typeof content === 'string') {
                    const lines = content.split('\n');
                    let inCommentsSection = false;
                    let commentsLines = [];
                    
                    for (let line of lines) {
                        if (line.startsWith('# Comments')) {
                            inCommentsSection = true;
                            continue;
                        } else if (line.startsWith('# ') && inCommentsSection) {
                            // 次のセクションが始まったら終了
                            break;
                        } else if (inCommentsSection && line.trim() !== '') {
                            commentsLines.push(line);
                        }
                    }
                    commentsSection = commentsLines.join(' ').trim() || "コメントなし";
                } else {
                    commentsSection = "コメントなし";
                }
            } else {
                commentsSection = "ファイルが見つかりません";
            }
        } catch (error) {
            commentsSection = "読み込みエラー";
        }
        
        return [
            `[[${p.title}]]`,
            "⭐️".repeat(p.rating) + "☆".repeat(5 - p.rating),
            commentsSection
        ];
    }))
);