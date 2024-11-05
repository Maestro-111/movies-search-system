from chromadb import Client
from chromadb.config import Settings
import chromadb


chroma_client = chromadb.Client()
movies_collection = chroma_client.create_collection(name="movies_embeddings",
                                                    metadata={"hnsw:space": "cosine"}
                                                    )

