import time
from knowledge_base import get_index, get_hybrid_retriever
from llama_index.retrievers.bm25 import BM25Retriever
import os

# Turn off noisy logs
import logging
logging.getLogger("llama_index").setLevel(logging.WARNING)

def run_experiment():
    print("=======================================")
    print("PHASE 4: HYBRID RETRIEVAL EXPERIMENT")
    print("=======================================\n")
    
    # Let's test a very tricky keyword that Dense Embeddings usually struggle with
    # but BM25 is perfect at finding.
    test_query = "Ashwagandha KSM-66"
    domain = "nutrition"
    
    print(f"Loading indices for domain: {domain}...")
    
    # 1. Setup Dense Retriever
    index = get_index(domain)
    dense_retriever = index.as_retriever(similarity_top_k=2)
    
    # 2. Setup BM25 Retriever
    domain_bm25_path = os.path.join(os.path.dirname(__file__), "..", "storage", f"{domain}_bm25")
    if os.path.exists(domain_bm25_path):
        bm25_retriever = BM25Retriever.from_persist_dir(domain_bm25_path)
    else:
        nodes = list(index.docstore.docs.values())
        bm25_retriever = BM25Retriever.from_defaults(nodes=nodes)
    bm25_retriever.similarity_top_k = 2
    
    # 3. Setup Hybrid Retriever (60% Dense / 40% BM25)
    hybrid_retriever = get_hybrid_retriever(domain, similarity_top_k=2)
    
    print(f"\n[TEST QUERY]: '{test_query}'\n")
    
    # --- TEST 1: PURE DENSE ---
    start = time.time()
    dense_nodes = dense_retriever.retrieve(test_query)
    print(f"--- DENSE EMBEDDINGS (Semantic) --- [{time.time()-start:.3f}s]")
    for i, node in enumerate(dense_nodes):
        print(f"Rank {i+1} [Score: {node.score:.3f}]: {node.text[:100]}...")
        
    print("\n")
    
    # --- TEST 2: PURE BM25 ---
    start = time.time()
    bm25_nodes = bm25_retriever.retrieve(test_query)
    print(f"--- BM25 (Keyword) --- [{time.time()-start:.3f}s]")
    for i, node in enumerate(bm25_nodes):
        print(f"Rank {i+1} [Score: {node.score:.3f}]: {node.text[:100]}...")
        
    print("\n")
    
    # --- TEST 3: HYBRID RRF ---
    start = time.time()
    hybrid_nodes = hybrid_retriever.retrieve(test_query)
    print(f"--- HYBRID (60% Dense + 40% BM25) --- [{time.time()-start:.3f}s]")
    for i, node in enumerate(hybrid_nodes):
        # QueryFusionRetriever normalizes RRF scores
        print(f"Rank {i+1} [Score: {node.score:.3f}]: {node.text[:100]}...")

if __name__ == "__main__":
    run_experiment()
