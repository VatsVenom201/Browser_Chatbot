# SiteSense - Webpage AI Assistant

SiteSense is a smart browser extension backed by a Python FastAPI server that lets you chat with webpages, summarize content, and extract key insights instantly using AI. Built with a unified Side Panel frontend, it leverages Retrieval-Augmented Generation (RAG) and the lightning-fast Groq API (Llama-3) to give you an intelligent assistant directly inside your browser.

## 🚀 Key Features

*   **Chat with the Webpage (RAG)**: Ask questions about the page you're reading. The backend chunks the webpage's text, generates embeddings, performs a semantic search, and dynamically answers your questions using context.
*   **Full Page Summarization**: Instantly get a comprehensive, well-structured summary of the active webpage without having to read a long article.
*   **Selected Text Summarization**: Highlight specific text on the page and get a focused summary for just that portion.
*   **Dynamic Drawer UI**: Clean, responsive side-panel UI with a persistent session to maintain context across your workflow.

## 🏗️ Architecture Overview

The system is split into two primary components: a **Browser Extension** for the frontend and a **Python API** for the backend engine.

### 1. Browser Extension (Frontend)
Located in the `extension/` directory. It uses the Chrome Extension Manifest V3 framework, structured as follows:
*   **`manifest.json`**: Configures permissions (`activeTab`, `scripting`, `sidePanel`, `storage`).
*   **`background.js`**: Service worker that ensures session tracking via UUID creation per installation.
*   **`content.js`**: A content script injected into web pages to extract page outer HTML, parse selection, and grab the body text effortlessly.
*   **`sidepanel.html/js/css`**: The core interactive UI injected into the browser's side panel. It communicates with the backend via REST endpoints for all heavy lifting.

### 2. Backend (LLM/RAG Pipeline)
Located in the `backend/` directory. Uses a robust stack consisting of:
*   **FastAPI & Uvicorn (`app.py`)**: High-performance asynchronous REST API handling CORS, chunking logic, and proxying streams to the user.
*   **RAG Engine (`rag_pipeline.py`)**: Uses **LangChain** (`RecursiveCharacterTextSplitter`) to divide the scraped HTML text into chunks. Vectors are embedded via HuggingFace and stored dynamically in an ephemeral **ChromaDB** container per user session. 
*   **AI Engine**: Powered by Meta's **Llama 3** model, serviced via the **Groq API** to deliver near-instant responses and summarization logic (`summarizer.py`).
*   **HTML Cleaner (`html_cleaner.py`)**: Handles aggressive sanitization of DOM elements, CSS, and JS code to extract pure readability.

## 🛠️ Technology Stack

**Frontend**: HTML, CSS, JavaScript (Chrome Extension API / Manifest V3)
**Backend API**: Python 3.10+, FastAPI, Uvicorn, Requests
**AI & Vectors**: LangChain, ChromaDB, HuggingFace (`sentence-transformers`)
**LLM Processing**: Meta Llama 3 (via Groq API)

---

## ⚙️ Installation & Setup

### 1. Setting up the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Create a `.env` file in the `backend` directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
5. Run the server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

### 2. Setting up the Extension

1. Open your Chromium-based browser (Chrome, Edge, Brave, etc.).
2. Navigate to your extensions page (`chrome://extensions/` or `edge://extensions/`).
3. Enable **Developer mode** (usually a toggle in the top right corner).
4. Click **Load unpacked** and select the `extension` folder located inside this repository.
5. Click the SiteSense extension icon next to your browser's search bar to open the Side Panel.

*(Note: In `sidepanel.js`, ensure `API_BASE` points to your active backend server: `http://localhost:8000` for local testing or your deployed Render URL for production).*

## 💡 Usage Guide
1. Navigate to any textual webpage.
2. Open the SiteSense side panel by clicking the extension logo.
3. Click "Analyze Page" to allow the RAG system to embed the content.
4. Start typing questions directly into the chatbox and press Enter.
5. Use "Summarize Page" to get a quick breakdown, or highlight text anywhere on the page and click "Summarize Selected Text".
