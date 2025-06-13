# PMAY Chatbot Backend

This folder contains all backend Python code for the PMAY Chatbot project.

## Structure

- `core/` - Shared logic (vector store, LLM, document processing, constants)
- `api/` - FastAPI app and endpoints
- `utils/` - Helper utilities (add your own as needed)

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   uvicorn api.main:app --reload
   ```

## Endpoints
- `POST /chat` - Chat with the bot
- `POST /upload` - Upload a document for ingestion 