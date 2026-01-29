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
> {{abstract}}

> [!Glossary]
{{glossary}}

# Contribution
## Content
### Task
{{task}}
### Setting
{{setting}}
### Input
{{input}}
### Output
{{output}}
### Dataset
{{dataset}}

## Main Argument
### Claim
{{claim}}
### Existing Issue
{{issue}}
### Improvement
{{improve}}

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