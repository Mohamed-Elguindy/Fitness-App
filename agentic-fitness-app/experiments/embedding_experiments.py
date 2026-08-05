import json
import time
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

APP_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_JSONL_PATH = APP_ROOT / "experiments" / "reports" / "phase1_hybrid_chunks.jsonl"
OUTPUT_JSON_PATH = APP_ROOT / "experiments" / "reports" / "embedding_results.json"

QUERIES = [
    "optimal protein intake per meal for muscle protein synthesis",
    "weekly training volume for hypertrophy",
    "carbohydrate timing before resistance training",
    "rest period recommendations for strength training",
    "creatine loading protocol and dosing",
    "rep range for strength versus hypertrophy",
    "overtraining symptoms and recovery protocols",
    "training frequency per muscle group per week"
]

def load_chunks():
    chunks = []
    with open(CHUNKS_JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def run_model_experiment(model_name: str, chunks: list, queries: list):
    print(f"\nLoading model {model_name}...")
    model = SentenceTransformer(model_name)
    
    texts = [c["text"] for c in chunks]
    
    print(f"Embedding {len(texts)} chunks with {model_name}...")
    start_time = time.time()
    chunk_embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    embed_time = time.time() - start_time
    print(f"Embedding took {embed_time:.2f} seconds.")
    
    results = {}
    
    for q in queries:
        q_emb = model.encode([q], normalize_embeddings=True)
        sims = cosine_similarity(q_emb, chunk_embeddings)[0]
        top_indices = np.argsort(sims)[::-1][:3]
        
        top_chunks = []
        for idx in top_indices:
            top_chunks.append({
                "score": float(sims[idx]),
                "text": chunks[idx]["text"],
                "source": chunks[idx]["source_file"]
            })
            
        results[q] = top_chunks
        
    return {
        "model": model_name,
        "embed_time": embed_time,
        "results": results
    }

def main():
    chunks = load_chunks()
    
    small_results = run_model_experiment("BAAI/bge-small-en-v1.5", chunks, QUERIES)
    base_results = run_model_experiment("BAAI/bge-base-en-v1.5", chunks, QUERIES)
    
    output = {
        "small": small_results,
        "base": base_results,
        "num_chunks": len(chunks)
    }
    
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        
    print(f"\nResults written to {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()
