from config import HF_API_KEY
from typing import List
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_API_KEY

embedding_model = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
)

def get_embeddings(texts: List[str]) -> List[List[float]]:
    try:
        # returns nested list [[...], [...]]
        return embedding_model.embed_documents(texts)
    except Exception as e:
        print(f"HuggingFace Embeddings Error: {e}")
        raise e
