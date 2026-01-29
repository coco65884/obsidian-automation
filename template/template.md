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
> {{glossary}}

# Contribution
{{task}}
{{claim}}
{{novelty}}

# KeyIdea
{{keyidea}}

# Method
{{method}}

# Result
{{result}}
{{discussion}}

# Ablation
{{ablation}}

# Comments

# Citation
{{bibliography.slice(4)}}

>[!Info]
{{info_block}}

> [!Keyword]-
> Field: #{{field}}
> Theme: #{{theme}}
> {{keyword}}