"""RAG: store brand guidelines in ChromaDB and retrieve the relevant ones."""
import chromadb

client = chromadb.PersistentClient(path="./brand_db")
col = client.get_or_create_collection("brand")


def index_guidelines(path="brand_guidelines.txt"):
    lines = [l.strip() for l in open(path, encoding="utf-8") if l.strip()]
    col.upsert(ids=[f"g{i}" for i in range(len(lines))], documents=lines)
    return len(lines)


def get_guidelines(query, k=5):
    index_guidelines()  # re-index so edits to the file are picked up
    r = col.query(query_texts=[query], n_results=min(k, col.count()))
    return r["documents"][0]