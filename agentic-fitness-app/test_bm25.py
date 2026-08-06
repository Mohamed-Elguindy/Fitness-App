from knowledge_base import get_index
from llama_index.retrievers.bm25 import BM25Retriever

index = get_index("nutrition")
nodes = list(index.docstore.docs.values())
print(f"Got {len(nodes)} nodes from docstore.")

bm25_retriever = BM25Retriever.from_defaults(nodes=nodes)
print("Built BM25Retriever.")
