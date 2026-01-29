---
title: "{{title}}"
authors:
{{authors_block}}
field: "{{field}}"
publication: "{{publicationTitle}}"
year: "{{date | format('YYYY')}}"
citekey: "{{citekey}}"
dateread: '{{importDate | format("YYYY-MM-DD")}}'
doi: "{{DOI}}"
url: "{{url}}"
type: "{{itemType}}"
rating: 0
---

> [!Data]
> **Local Link** 
> [[{{title}}.pdf]]

> [!Abstract]
> {{abstractNote}}
>

> [!Glossary]
{{glossary}}

# Contribution
## Task
{{task}}
## Claim
{{claim}}
## Novelty
{{novelty}}

# KeyIdea
{{keyidea}}

# Method
{{method}}

# Result
{{result}}

# Ablation
{{ablation}}

# Memo

# Comments

# Citation
{{bibliography.slice(4)}}

>[!Info]
{{info_block}}

> [!Keyword]-
> Field: #{{field}}
> Theme: #{{theme}}
> {{keyword}}