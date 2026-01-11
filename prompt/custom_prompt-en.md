Please output the summarized result in the following format. Pay attention to the following points:
- Do not output any text other than the format.
- Output in JSON format: {"abstract":"summary of abstract", "overview":"paper overview", "publication":"conference name"}.
- Follow the format in {} below, and summarize based on the instructions written after the dash (-) for what should be written in each section.
- Write the Markdown format directly in "" within the overview.
- Escape backslashes used in LaTeX formulas when outputting (e.g., \\alpha)
- When using LaTeX formulas, use inline notation (notation enclosed with $ and $). (e.g., $\sum_{k=0}{n}x_{k}$)
- LaTeX formulas do not need to be surrounded by () as a whole. Also, () used within formulas do not need to be escaped like \( or \).
- Leave technical terms untranslated and keep them in English.
- Sections with only one line of output do not need - or * at the beginning.
- Do not include blank lines between sections.
- Since this is a paper translation, use academic writing style rather than conversational tone.

{ 
"abstract": "
Summarize the Abstract section here
",
"overview" : "
### **Contributions**
- Describe the contributions of the paper concisely and clearly.
- It is desirable to make the points written at the end of the Introduction clearer and write them in bullet points.
### **Terminology**
- Briefly explain field-specific technical terms or terms that require explanation that appear in the paper in bullet points.
- The reader is assumed to be a graduate student with basic knowledge of machine learning, so explanations of basic technical terms such as LLM or Fine-tuning are unnecessary.
- Too many terms make it difficult to read, so prioritize terms necessary to understand the proposed method in the paper.
### **Novelty**  
- Briefly describe in bullet points the points where this research has novelty compared to previous research and points where it is superior.
- This section has three subsections: Existing Issues, Proposed Method, and Results
- In the Existing Issues section, briefly describe the limitations of previous methods and unsolved problems.
- In the Proposed Method section, describe the name of the method proposed by this research, expected effects (purpose of introduction), and a brief overview of the method.
- In the Results section, describe how much the issues have been improved compared to existing methods.
- Keep in mind to describe each section concisely.
### **Method**  
- Briefly explain the main technologies and methods adopted in this research.
- Output in a format that visually shows the flow and blocks of the proposed method clearly.
### **Challenges**  
- Briefly describe discussion points, constraints, and future challenges regarding the research results and proposed method.
### **Related Literature**  
- Introduce major references related to this research or papers to read next.
- Keep paper titles as they are without translation, and output in the following format:
- PaperTitle (first author name et al., year): Brief overview (in English)
### **Keywords**
- Output 5 or more keywords related to this research in English.
- Add # at the beginning of keywords without spaces.
- Do not use keywords that are meaningless by themselves (such as Zero).
- Always include the following items and output them in order from the top:
- Broad category of the field (ML for theory-oriented papers, CV for papers related to image processing, etc.)
- Task genre (SemanticSegmentation, Classification, etc.)
- If there is a baseline model, its name (ViT, DiffusionModel, CLIP, etc.)
- Broad category of the method (KnowledgeDistillation, etc.)
- To maintain consistency with existing keywords, select from the following existing keywords as much as possible, and propose new keywords if not available:
{KEYWORDS_SECTION}
",
"publication": "conference name
- Output only the conference name. (e.g., ICML, CVPR)
- Year is not necessary.
- If it is a journal, use the journal name.
- If it is a survey paper, use 'survey'.
"
}
