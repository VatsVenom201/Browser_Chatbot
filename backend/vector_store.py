import chromadb
from typing import Dict

# In-memory ephemeral client for session storage
client = chromadb.Client()

# Dictionary to store chromadb collections per session
vector_sessions: Dict[str, chromadb.Collection] = {}

def get_or_create_collection(session_id: str):
    if session_id not in vector_sessions:
        collection_name = f"session_{session_id.replace('-', '_')}"
        try:
            collection = client.create_collection(name=collection_name)
        except chromadb.errors.UniqueConstraintError:
            collection = client.get_collection(name=collection_name)
        vector_sessions[session_id] = collection
    return vector_sessions[session_id]
