import os
import json
from pathlib import Path
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    SimpleDirectoryReader,
    Settings
)
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Define paths
APP_ROOT = Path(__file__).resolve().parent
STORAGE_DIR = APP_ROOT / "storage"
DATA_DIR = APP_ROOT / "data"
CHUNKS_JSONL_PATH = APP_ROOT / "experiments" / "reports" / "phase1_hybrid_chunks.jsonl"

# Set the global embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def build_index_from_jsonl(domain: str) -> VectorStoreIndex:
    """Build index from the pre-chunked JSONL file (for nutrition and training)."""
    nodes = []
    if not CHUNKS_JSONL_PATH.exists():
        raise FileNotFoundError(f"Missing chunks file: {CHUNKS_JSONL_PATH}")
        
    with open(CHUNKS_JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if data["corpus"] == domain:
                node = TextNode(
                    text=data["text"],
                    metadata={
                        "source_file": data["source_file"],
                        "title": data["title"],
                        "section": data["section"]
                    }
                )
                nodes.append(node)
                
    if not nodes:
        raise ValueError(f"No chunks found for domain: {domain}")
        
    print(f"Building {domain} index from {len(nodes)} pre-computed chunks...")
    return VectorStoreIndex(nodes)

def build_index_from_directory(domain: str) -> VectorStoreIndex:
    """Build index from raw files using SimpleDirectoryReader (for legacy domains)."""
    data_path = DATA_DIR / domain
    if not data_path.exists():
        raise FileNotFoundError(f"Missing data directory: {data_path}")
        
    print(f"Reading documents for {domain}...")
    docs = SimpleDirectoryReader(str(data_path)).load_data()
    print(f"Building {domain} index from raw documents...")
    return VectorStoreIndex.from_documents(docs)

def get_index(domain: str) -> VectorStoreIndex:
    """
    Get the index for a domain. Loads from disk if it exists, otherwise builds and persists it.
    """
    domain_storage_path = STORAGE_DIR / domain
    
    # 1. If it exists on disk, load it instantly
    if domain_storage_path.exists() and any(domain_storage_path.iterdir()):
        print(f"Loading {domain} index from storage...")
        storage_context = StorageContext.from_defaults(persist_dir=str(domain_storage_path))
        return load_index_from_storage(storage_context)
        
    # 2. If it doesn't exist, we must build it
    if domain in ["nutrition", "training"]:
        index = build_index_from_jsonl(domain)
    elif domain in ["fitness_and_diet", "mentality", "general"]:
        index = build_index_from_directory(domain)
    else:
        raise ValueError(f"Unknown domain: {domain}")
        
    # 3. Persist the newly built index for future use
    print(f"Persisting {domain} index to storage...")
    index.storage_context.persist(persist_dir=str(domain_storage_path))
    
    return index
