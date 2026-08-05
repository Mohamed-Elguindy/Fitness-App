import sys
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import chunking_experiment as ce

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

def small_to_big_chunks(doc):
    text = "\n\n".join(page.text for page in doc.pages)
    chunks = []
    
    for section, body in ce.split_sections(text):
        sentences = ce.split_sentences(body)
        for i, sent in enumerate(sentences):
            start = max(0, i - 3)
            end = min(len(sentences), i + 4)
            window_text = " ".join(sentences[start:end])
            chunks.append({
                "strategy": "small_to_big",
                "corpus": doc.corpus,
                "source_file": doc.source_file,
                "section": section,
                "embed_text": sent,
                "return_text": window_text
            })
    return chunks

def run_evaluation():
    print("Loading documents...")
    docs = ce.load_documents()
    
    print("Generating chunks...")
    chunks_dict = {
        "fixed": [{"embed_text": c.text, "return_text": c.text, "source_file": c.source_file} for doc in docs for c in ce.fixed_chunks(doc)],
        "structure": [{"embed_text": c.text, "return_text": c.text, "source_file": c.source_file} for doc in docs for c in ce.structure_chunks(doc)],
        "hybrid": [{"embed_text": c.text, "return_text": c.text, "source_file": c.source_file} for doc in docs for c in ce.hybrid_chunks(doc)],
        "small_to_big": [c for doc in docs for c in small_to_big_chunks(doc)]
    }
    
    print("Loading embedding model...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    
    results = {}
    for strategy, chunks in chunks_dict.items():
        print(f"\nEmbedding {len(chunks)} {strategy} chunks...")
        embed_texts = [c["embed_text"] for c in chunks]
        chunk_embeddings = model.encode(embed_texts, normalize_embeddings=True, show_progress_bar=True)
        
        results[strategy] = {}
        for q in QUERIES:
            q_emb = model.encode([q], normalize_embeddings=True)
            sims = cosine_similarity(q_emb, chunk_embeddings)[0]
            top_indices = np.argsort(sims)[::-1][:3]
            
            top_chunks = []
            for idx in top_indices:
                top_chunks.append({
                    "score": float(sims[idx]),
                    "text": chunks[idx]["return_text"],
                    "source": chunks[idx]["source_file"]
                })
            results[strategy][q] = top_chunks

    output_path = ce.APP_ROOT / "experiments" / "reports" / "chunking_eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {output_path}")

if __name__ == "__main__":
    run_evaluation()
