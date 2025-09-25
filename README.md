# RAG-PDF Chat
*A local, private chatbot that answers questions using your PDF documents as its only knowledge source.*

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Read in Portuguese](https://img.shields.io/badge/Leia%20em-Portugu%C3%AAs%20(BR)-blue)](README.pt-br.md)

This Retrieval-Augmented Generation tool is a local application that allows you to interact with an AI agent that answers questions based **solely** on the content of the PDF documents you provide. By grounding the AI's responses in your uploaded text, the tool minimizes hallucinations and ensures accurate, context-specific answers. All processing occurs on your local machine, guaranteeing complete data privacy.


## Prerequisites

Before you begin, ensure you have the following installed and configured:

1.  **Windows Operating System**
    *   This application requires LM Studio, which is currently only available for Windows

2.  **Python 3.8 or higher**
    *   Download from [python.org](https://www.python.org/downloads/)
    *   Verify installation: Open a command prompt and run `python --version`

3.  **LM Studio**
    *   Download and install from [LM Studio's official website](https://lmstudio.ai/)
    *   **Required Settings**: After installation, open LM Studio and enable **Developer Mode** or **Power User Mode** in the settings


## Installation & Setup

### Step 1: Download and Configure Models in LM Studio

1.  **Launch LM Studio**
2.  **Download Models**:
    *   In the "Search" tab, find and download a suitable **Language Model (LLM)** (e.g., a Llama 3 or Mistral variant)
    *   Find and download an **Embeddings Model** (e.g., `Qwen3-Embedding-0.6B` or `embeddinggemma-300m` are common choices)
3.  **Startup the Local Server**:
    *   Go to the **"Developer"** tab
    *   Toggle the local server button or use (Ctrl + .)

### Step 2: Set Up the RAG Environment

1.  **Run the setup script**:
    *   Double-click the `setup.bat` file in the `rag-pdf` project directory
    *   This script will:
        *   Create a Python virtual environment
        *   Install all required dependencies (e.g., `fastapi`, `scikit-learn`, `pypdf`)
        *   Create the necessary directories (like `documents/`)
    * Alternatively, you can create a virtual environment manually and install the dependencies from requirements.txt

### Step 3: Prepare Your Documents

1.  Place the PDF files you want to query into the `documents/` directory created by the setup script

### Step 4: Start the Application

1.  **Start the LM Studio Server**:
    *   Go back to the **"Developer"** tab in LM Studio
    *   On the **"Select a model to load"** section, select the models you downloaded
    *   Make sure the server status is **"running"**. If it is not, start the server by following the instructions in Step 1.3 ("Startup the Local Server").

2.  **Launch the application**:
    *   Double-click the `app.bat` file
    *   Wait for the script to process your PDFs. This step reads, chunks, and creates vector embeddings for all documents in the documents/ folder. **The process may take a moment depending on the number and size of the documents**
    *   Once complete, your default browser should open automatically to `http://127.0.0.1:8888`
    *   You might need to refresh the page if it starts up before your server


## Usage

1.  **Chat Interface**: The web interface will open. Type your question in the input box and press Enter
2.  **Review Answers**: The AI agent will process your query, search through the vectorized content of your PDFs, and generate a response based solely on that content
3.  **Reset**: Use the "Reset Chat" button to clear the current conversation history


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

See the [LICENSE](LICENSE.md) file for full details.