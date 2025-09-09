import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "chroma_persistent_storage"
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection("document_qa_collection")


results = collection.get(include=["documents", "embeddings", "metadatas"])

for i in range(len(results["documents"])):
    print(f"Document: {results['documents'][i]}")
    print(f"Metadata: {results['metadatas'][i]}")
    print(f"Embedding (first 10 values): {results['embeddings'][i][:10]}")
    print()
