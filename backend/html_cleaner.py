import trafilatura
from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """
    Use hybrid extraction:
    1. Try trafilatura.extract(html)
    2. If result too small, fallback to BeautifulSoup
    """
    text = trafilatura.extract(html_content)
    if text is not None and len(text) > 200:
        return text

    # Fallback to BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.extract()
    return soup.get_text(separator="\n", strip=True)
