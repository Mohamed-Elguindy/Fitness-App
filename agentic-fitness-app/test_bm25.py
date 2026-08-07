from app.services.rag_service import RAGService
from llama_index.retrievers.bm25 import BM25Retriever

rag_service = RAGService()
index = rag_service._get_index("fitness_and_diet")
nodes = list(index.docstore.docs.values())
print(f"Got {len(nodes)} nodes from docstore.")

bm25_retriever = BM25Retriever.from_defaults(nodes=nodes)
print("Built BM25Retriever.")
