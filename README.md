# Veritas: A Grounded AI Agent for PDFs
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/Diegolinop/veritas/pulls)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Read in Portuguese](https://img.shields.io/badge/Leia%20em-Portugu%C3%AAs%20(BR)-blue)](README.pt-br.md)

Veritas is a local application that allows you to interact with an AI agent that answers questions based **solely** on the content of the PDF documents you provide. By grounding the AI's responses in your uploaded text, Veritas minimizes hallucinations and ensures accurate, context-specific answers. All processing occurs on your local machine, guaranteeing complete data privacy.

## Features

- **100% Local & Private**: Everything runs on your machine. Your documents and conversations never leave your computer.
- **PDF-Powered Context**: The AI agent is constrained to your provided PDFs, ensuring verifiable and relevant answers.
- **Efficient Retrieval**: Documents are parsed, vectorized, and cached for fast and accurate semantic search.
- **LM Studio Integration**: Leverages local models served via LM Studio for both language generation and embeddings, offering flexibility in model choice.


## Prerequisites

Before you begin, ensure you have the following installed and configured:

1.  **Python 3.8 or higher**
    *   Download from [python.org](https://www.python.org/downloads/).
    *   Verify installation: Open a command prompt and run `python --version`.

2.  **LM Studio**
    *   Download and install from [LM Studio's official website](https://lmstudio.ai/).
    *   **Required Settings**: After installation, open LM Studio and enable **Developer Mode** or **Power User Mode** in the Settings.


## Installation & Setup

### Step 1: Download and Configure Models in LM Studio

1.  **Launch LM Studio**.
2.  **Download Models**:
    *   In the "Search" tab, find and download a suitable **Language Model (LLM)** (e.g., a Llama 2 or Mistral variant).
    *   Find and download an **Embeddings Model** (e.g., `all-MiniLM-L6-v2` or `bge-small-en-v1.5` are common choices).
3.  **Load Models for the Server**:
    *   Go to the **"Local Server"** tab.
    *   Under **"LLM"**, select the language model you downloaded.
    *   Under **"Embeddings"**, select the embeddings model you downloaded.
    *   **Do not start the server yet.**

### Step 2: Set Up the Veritas Environment

1.  **Run the setup script**:
    *   Double-click the `setup.bat` file in the Veritas project directory.
    *   This script will:
        *   Create a Python virtual environment.
        *   Install all required dependencies (e.g., `fastapi`, `scikit-learn`, `pypdf`).
        *   Create the necessary directories (like `documents/`).

### Step 3: Prepare Your Documents

1.  Place the PDF files you want to query into the `documents/` directory created by the setup script.

### Step 4: Start the Application

1.  **Start the LM Studio Server**:
    *   Go back to the **"Local Server"** tab in LM Studio.
    *   Ensure the correct models are selected.
    *   Click the **"Start Server"** button. Note the server URL (typically `http://localhost:1234/v1`).

2.  **Launch Veritas**:
    *   Double-click the `app.bat` file.
    *   Wait for the script to process your PDFs. This step reads, chunks, and creates vector embeddings for all documents in the documents/ folder. **The process may take a moment depending on the number and size of the documents.**
    *   Once complete, your default browser should open automatically to `http://127.0.0.1:8888`.


## Usage

1.  **Chat Interface**: The web interface will open. Type your question in the input box and press Enter.
2.  **Review Answers**: The AI agent will process your query, search through the vectorized content of your PDFs, and generate a response based solely on that content.
3.  **Reset**: Use the "Reset Chat" button to clear the current conversation history.


## Troubleshooting

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| `setup.bat` fails. | Python not installed or not in PATH. | Reinstall Python, ensuring you check "Add Python to PATH" during installation. |
| LM Studio server connection error. | LM Studio server is not running. | Go to the "Local Server" tab in LM Studio and click "Start Server". |
| | Incorrect model loaded. | Ensure both an LLM and an Embeddings model are selected and loaded in the "Local Server" tab. |
| App fails to process PDFs. | No PDFs in the `documents/` folder. | Add PDF files to the `documents/` directory and restart `app.bat`. |
| The AI gives generic answers. | The retrieval didn't find relevant context. | Rephrase your question to use keywords that might be in the PDFs. |


## License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License** (CC BY-NC-SA 4.0). This means you are free to share and adapt the material for non-commercial purposes, as long as you give appropriate credit and license any new creations under the identical terms.

See the [LICENSE](LICENSE) file for full details.


## Acknowledgments

- **[LM Studio](https://lmstudio.ai/)**: For providing an incredibly easy way to run local LLMs and embeddings models.
- **[FastAPI](https://fastapi.tiangolo.com/)**: For the modern, high-performance web framework.
- **[Scikit-learn](https://scikit-learn.org/)**: For the simple and effective vector search functionality.