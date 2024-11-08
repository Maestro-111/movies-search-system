import chromadb
import os
from chromadb.config import Settings


persist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../movies/movie"))


chroma_client = chromadb.PersistentClient(path=persist_path,settings=Settings())
movies_collection = chroma_client.get_or_create_collection(name="movies_embeddings",
                                                           metadata={"hnsw:space": "cosine"})
