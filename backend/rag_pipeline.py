import json
import httpx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embeddings import get_embeddings
from vector_store import get_or_create_collection
from config import GROQ_API_KEY
from typing import List, Dict, Any, AsyncGenerator

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def process_and_store_text(session_id: str, text: str) -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = splitter.split_text(text)
    
    if not chunks:
        return 0

    embeddings = get_embeddings(chunks)
    collection = get_or_create_collection(session_id)
    
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )
    return len(chunks)

async def stream_groq_response(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant", # llama-3.3-70b-versatile , for better performance
        "messages": messages,
        "stream": True
    }
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", GROQ_API_URL, headers=headers, json=payload, timeout=30.0) as response:
            if response.status_code != 200:
                body = await response.aread()
                yield f"[Groq API Error {response.status_code}: {body.decode()[:300]}]"
                return
            async for chunk in response.aiter_lines():
                if chunk.startswith("data: "):
                    data_str = chunk[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except json.JSONDecodeError:
                        continue

def create_rag_prompt(context: str, question: str) -> List[Dict[str, str]]:
    
    system_prompt = f"""You are an AI assistant helping a user understand a webpage.

Context from webpage:
{context}

User question:
{question}

Answer clearly using only the webpage context."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

async def chat_with_rag(session_id: str, question: str) -> AsyncGenerator[str, None]:
    collection = get_or_create_collection(session_id)
    
    if collection.count() == 0:
        yield "Please analyze a page first to load the context."
        return

    question_embedding = get_embeddings([question])[0]
    
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=self_or_less(5, collection.count())
    )
    
    context = ""
    if results and results["documents"] and len(results["documents"]) > 0:
        context = "\n\n".join(results["documents"][0])
        
    messages = create_rag_prompt(context, question)
    
    async for token in stream_groq_response(messages):
        yield token

def self_or_less(request_n: int, total_count: int) -> int:
    return request_n if total_count >= request_n else total_count
