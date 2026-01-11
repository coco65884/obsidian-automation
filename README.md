# Obsidian Automation

A Python tool that automatically processes research paper PDF files and generates Obsidian notes. It retrieves metadata from Zotero, generates summaries using the Google Gemini API, and provides keyword management functionality. This tool uses gemini-2.5-flash API, which should be basically free.

<video src="https://github.com/user-attachments/assets/20cf22c6-3504-4726-9719-4a9f61d7449c"></video>

## 🚀 Key Features

- **Automatic PDF Processing**: Extract text from PDF files
- **AI Summary Generation**: Automatic paper summarization using Google Gemini API
- **Zotero Integration**: Automatic retrieval of paper metadata from Zotero library
- **Keyword Management**: Automatic extraction and management of machine learning keywords
- **Obsidian Note Generation**: Automatic creation of structured Markdown notes
- **Template Support**: Customizable note templates

## 📋 Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Google Gemini API access
- Zotero account
- Obsidian (for note management)

## 💡 Preparation

### Obsidian Setup
1. Install Obsidian
2. Launch Obsidian and create a Vault (workspace)
3. Create directories within the Vault for storing papers and notes
4. Install useful plugins from Preference/Community plugins (recommended)
   * Callout Manager: Create custom callouts. If using this program, registering "Overview" will improve readability.
   * Dataview: Create tables based on note information. See Samples/Dashboard.md for an example. (Enable "Enable Javascript queries" in settings.)
   * PDF++: Take screenshots of papers and paste links, or cite and leave your own notes.
5. Add Samples/Dashboard.md to your Vault and replace `YOUR_NOTE_FOLDER_HERE` in two locations with the path to your notes directory (recommended)
6. Add Samples/paper.css to .obsidian/snippets and apply the CSS from Preference/Appearance/CSS snippets (optional)

### Zotero Setup
1. Install Zotero
2. Add the `ZotMoov` plugin to transfer PDFs from Zotero
3. Set ZotMoov's output destination to the paper storage directory created in Obsidian Setup step 3
4. In Preferences/General/File Renaming/Customize Filename Format, specify {{ title truncate="100" }}

## 🛠 Environment Setup

### 1. Installing uv

If uv is not installed, install it using the following commands:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Homebrew (macOS)
brew install uv

# via pipx
pipx install uv
```

### 2. Clone the Project and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/coco65884/obsidian-automation
cd obsidian-automation

# Install dependencies
uv sync
```

### 3. Create and Activate Virtual Environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# For Windows
# .venv\Scripts\activate
```

### 4. Create Environment Variables File (.env)

Create a `.env` file in the project root and set the following environment variables:

```bash
# .env file example
ZOTERO_API_KEY=your_zotero_api_key_here
ZOTERO_USER_ID=your_zotero_user_id_here
GEMINI_API_KEY=your_gemini_api_key_here
PDF_FOLDER=/path/to/your/pdf/folder
NOTE_FOLDER=/path/to/your/obsidian/vault/folder
TEMPLATE_PATH=./template.md
```

## 🔑 How to Obtain API Keys

### Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key"
4. Select "Create API key"
5. Select a project (or create a new one)
6. Copy the generated API key and set it in the `.env` file as `GEMINI_API_KEY`

### Zotero API Key and User ID

#### Obtaining the API Key:
1. Log in to [Zotero](https://www.zotero.org/)
2. Go to [Settings > Feeds/API](https://www.zotero.org/settings/keys)
3. Click "Create new private key"
4. Set the required permissions:
   - **Personal Library**: Read access
   - **Default Group Permissions**: Read access (if using group libraries)
5. Click "Save Key"
6. Copy the generated API key and set it in the `.env` file as `ZOTERO_API_KEY`

#### Obtaining the User ID:
1. After logging in to Zotero, go to the [Feeds/API settings](https://www.zotero.org/settings/keys) page
2. Copy the number displayed at the top of the page: "Your userID for use in API calls is XXXXXX"
3. Set this number in the `.env` file as `ZOTERO_USER_ID`

## 📁 Directory Structure

```
obsidian-automation/
├── main.py                     # Main execution file
├── config.py                   # Configuration file
├── pdf_processor.py            # PDF processing
├── zotero_integrator.py        # Zotero integration
├── keyword_manager.py          # Keyword management
├── obsidian_note_creator.py    # Note creation
├── template.md                 # Note template
├── prompt/                     # Prompt files
│   ├── custom_prompt.md        # Custom prompt for AI summarization (Japanese)
│   ├── custom_prompt-en.md     # Custom prompt for AI summarization (English)
│   ├── keywords_reconstruction.md  # Prompt for keyword reconstruction (Japanese)
│   └── keywords_reconstruction-en.md  # Prompt for keyword reconstruction (English)
├── keywords.json               # Keyword database
├── .env                        # Environment variables file (needs to be created)
├── tests/                      # Test files
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🚦 Usage

### Basic Usage

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Run main script
python main.py
```

Running this command will:
1. Scan PDF files in `PDF_FOLDER`
2. Extract text from each PDF
3. Generate summaries with Google Gemini API
4. Retrieve metadata from Zotero
5. Extract and manage keywords
6. Create structured Obsidian notes in `NOTE_FOLDER`

## ⚠️ Important Note for English Users

**Note:** By default, error messages are displayed in Japanese, and the prompts provided in the `prompt/` directory are written in Japanese.

To use English prompts:
- **Option 1**: Copy the content from `prompt/custom_prompt-en.md` to `prompt/custom_prompt.md` (overwrite the original file)
- **Option 2**: Copy the content from `prompt/keywords_reconstruction-en.md` to `prompt/keywords_reconstruction.md` (overwrite the original file)
- **Option 3**: Modify the code to use the `-en.md` files directly

Alternatively, you can modify the prompt files to use your preferred language for AI-generated summaries and keyword management.

## 🎨 Customization

### Editing Note Template

You can customize the structure of generated notes by editing the `template.md` file. Available placeholders:

- `{{title}}` - Paper title
- `{{authors}}` - Author list
- `{{date}}` - Publication date
- `{{DOI}}` - DOI
- `{{abstractNote}}` - Abstract
- `{{publicationTitle}}` - Publication name
- Many other Zotero fields

### Editing AI Summary Prompt

You can customize how AI summaries are generated by editing the `prompt/custom_prompt.md` (or `prompt/custom_prompt-en.md` for English) file.

### Keyword Management

Keywords are managed in `keywords.json`. New keywords are automatically added, but you can also edit manually.
You can also change the instructions for keyword reconstruction in `prompt/keywords_reconstruction.md` (or `prompt/keywords_reconstruction-en.md` for English).

## 🧪 Testing

### Running Tests

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Run all tests
pytest tests

# Run tests with detailed output
pytest tests -v

# Run specific test file only
pytest tests/test_keyword_manager.py -v

# Run tests with coverage report
pytest tests --cov=. --cov-report=html
```

### Test Files List

- `tests/test_keyword_manager.py` - Tests for keyword management features
- `tests/test_pdf_processor.py` - Tests for PDF processing features
- `tests/test_zotero_integrator.py` - Tests for Zotero integration features
- `tests/test_obsidian_note_creator.py` - Tests for note creation features
- `tests/test_main.py` - Tests for main processing

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Verify that the `.env` file is correctly created
   - Confirm API keys are valid in your browser

2. **PDF Text Extraction Error**
   - Check if the PDF file is corrupted
   - May be a format that PyPDF2 cannot process

3. **Zotero Connection Error**
   - Check internet connection
   - Verify Zotero API key and user ID are correct

4. **Folder Path Error**
   - Confirm that `PDF_FOLDER` and `NOTE_FOLDER` paths exist
   - Check if paths contain special characters

### Checking Logs

You can identify the cause of problems by checking the logs output during program execution.

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b your_git_ID/issue#number`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin your_git_ID/issue#number`)
5. Create a Pull Request

### Development Environment Setup

```bash
# Install including development dependencies
uv sync --group dev

# Activate virtual environment
source .venv/bin/activate
```

## 📞 Support

If you encounter any issues, please let us know in [Issues](https://github.com/coco65884/obsidian-automation/issues).
