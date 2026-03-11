from rag_pipeline import stream_groq_response
from html_cleaner import clean_html
from typing import AsyncGenerator

async def summarize_text(text: str, mode: str) -> AsyncGenerator[str, None]:
    # text is already clean - for full_page it's browser innerText, for selected_text it's raw selection
    # Just truncate to safe limit
    text = text[:30000]
        
    prompt = f"Please provide a concise and comprehensive summary of the following text:\n\n{text}"
    messages = [
        {"role": "system", "content": "You are a helpful AI summarization assistant."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        async for token in stream_groq_response(messages):
            yield token
    except Exception as e:
        yield f"\n\n[Error summarizing page: {str(e)}]"
