from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

from html_cleaner import clean_html
from rag_pipeline import process_and_store_text, chat_with_rag
from summarizer import summarize_text

app = FastAPI(title="Webpage RAG Backend")

# Allowing all origins for extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    session_id: str
    html: str
    url: str

class ChatRequest(BaseModel):
    session_id: str
    question: str

class SummarizeRequest(BaseModel):
    session_id: str
    text: str
    mode: str

@app.get("/")
async def root():
    return {"message": "Webpage RAG Backend is running! Use the Chrome Extension to interact."}

@app.post("/analyze")
async def analyze_page(req: AnalyzeRequest):
    cleaned_text = clean_html(req.html)
    num_chunks = process_and_store_text(req.session_id, cleaned_text)
    return {"status": "success", "num_chunks": num_chunks}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    return StreamingResponse(
        chat_with_rag(req.session_id, req.question),
        media_type="text/plain"
    )

@app.post("/summarize")
async def summarize_endpoint(req: SummarizeRequest):
    return StreamingResponse(
        summarize_text(req.text, req.mode),
        media_type="text/plain"
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
