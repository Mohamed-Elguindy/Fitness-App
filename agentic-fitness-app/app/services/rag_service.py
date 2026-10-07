import os
import json
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    SimpleDirectoryReader,
    Settings
)
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.llms import MockLLM
from llama_index.core.tools import QueryEngineTool
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RouterQueryEngine, RetrieverQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.llms.gemini import Gemini

from app.core.config import settings
from app.utils.prompts import get_rag_diet_query, get_rag_training_query, get_rag_tool_descriptions

class RAGService:
    def __init__(self):
        # We use llama_index's Gemini wrapper here instead of the raw client
        if settings.GEMINI_API_KEY == "dummy_testing_key_for_ci":
            Settings.llm = MockLLM()
        else:
            Settings.llm = Gemini(model="models/gemini-3.8-flash", api_key=settings.GEMINI_API_KEY)
            
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
            
        # Paths
        self.app_root = Path(__file__).resolve().parent.parent.parent
        self.storage_dir = self.app_root / "storage"
        self.data_dir = self.app_root / "data"
        self.chunks_jsonl_path = self.app_root / "experiments" / "reports" / "phase1_hybrid_chunks.jsonl"
        
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize Router
        self.router = self._build_router()

    def _build_index_from_jsonl(self, domain: str) -> VectorStoreIndex:
        text_nodes = []
        if not self.chunks_jsonl_path.exists():
            raise FileNotFoundError(f"Missing chunks file: {self.chunks_jsonl_path}")
            
        with open(self.chunks_jsonl_path, "r", encoding="utf-8") as chunk_file:
            for line in chunk_file:
                chunk_data = json.loads(line)
                if chunk_data["corpus"] == domain:
                    text_node = TextNode(
                        text=chunk_data["text"],
                        metadata={
                            "source_file": chunk_data["source_file"],
                            "title": chunk_data["title"],
                            "section": chunk_data["section"]
                        }
                    )
                    text_nodes.append(text_node)
                    
        if not text_nodes:
            raise ValueError(f"No chunks found for domain: {domain}")
            
        print(f"Building {domain} index from {len(text_nodes)} pre-computed chunks...")
        return VectorStoreIndex(text_nodes)

    def _build_index_from_directory(self, domain: str) -> VectorStoreIndex:
        data_path = self.data_dir / domain
        if not data_path.exists():
            raise FileNotFoundError(f"Missing data directory: {data_path}")
            
        print(f"Reading documents for {domain}...")
        documents = SimpleDirectoryReader(str(data_path)).load_data()
        print(f"Building {domain} index from raw documents...")
        return VectorStoreIndex.from_documents(documents)

    def _get_index(self, domain: str) -> VectorStoreIndex:
        domain_storage_path = self.storage_dir / domain
        
        if domain_storage_path.exists() and any(domain_storage_path.iterdir()):
            print(f"Loading {domain} index from storage...")
            storage_context = StorageContext.from_defaults(persist_dir=str(domain_storage_path))
            return load_index_from_storage(storage_context)
            
        if domain in ["nutrition", "training"]:
            index = self._build_index_from_jsonl(domain)
        elif domain in ["fitness_and_diet", "mentality", "general"]:
            index = self._build_index_from_directory(domain)
        else:
            raise ValueError(f"Unknown domain: {domain}")
            
        print(f"Persisting {domain} index to storage...")
        index.storage_context.persist(persist_dir=str(domain_storage_path))
        
        return index

    def _get_hybrid_retriever(self, domain: str, similarity_top_k: int = 3):
        index = self._get_index(domain)
        text_nodes = list(index.docstore.docs.values())
        actual_top_k = min(similarity_top_k, len(text_nodes)) if text_nodes else 1
        
        vector_retriever = index.as_retriever(similarity_top_k=actual_top_k * 3)
        
        bm25_retriever = BM25Retriever.from_defaults(
            nodes=text_nodes, 
            similarity_top_k=actual_top_k * 3
        )
        
        hybrid_retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            similarity_top_k=actual_top_k * 3,
            num_queries=1,
            mode="reciprocal_rank_fusion"
        )
        
        return hybrid_retriever

    def _build_router(self) -> RouterQueryEngine:
        from llama_index.core.postprocessor import SentenceTransformerRerank
        
        fitness_retriever = self._get_hybrid_retriever("fitness_and_diet")
        mentality_retriever = self._get_hybrid_retriever("mentality")
        general_retriever = self._get_hybrid_retriever("general")
        
        # Initialize the cross-encoder reranker
        reranker = SentenceTransformerRerank(
            model="cross-encoder/ms-marco-MiniLM-L-2-v2",
            top_n=3,
            device="cpu"
        )

        fitness_query_engine = RetrieverQueryEngine.from_args(
            fitness_retriever,
            node_postprocessors=[reranker]
        )
        mentality_query_engine = RetrieverQueryEngine.from_args(
            mentality_retriever,
            node_postprocessors=[reranker]
        )
        general_query_engine = RetrieverQueryEngine.from_args(
            general_retriever,
            node_postprocessors=[reranker]
        )

        tool_descriptions = get_rag_tool_descriptions()

        fitness_tool = QueryEngineTool.from_defaults(
            query_engine=fitness_query_engine,
            description=tool_descriptions["fitness"]
        )

        mentality_tool = QueryEngineTool.from_defaults(
            query_engine=mentality_query_engine,
            description=tool_descriptions["mentality"]
        )
        general_tool = QueryEngineTool.from_defaults(
            query_engine=general_query_engine,
            description=tool_descriptions["general"]
        )

        return RouterQueryEngine(
            selector=LLMSingleSelector.from_defaults(),
            query_engine_tools=[fitness_tool, mentality_tool, general_tool]
        )

    def ask_coach(self, prompt: str) -> str:
        response = self.router.query(prompt)
        return str(response)

    def get_diet_context(self, goal: str, dietary_restrictions: str = "none") -> str:
        query = get_rag_diet_query(goal, dietary_restrictions)
        print(f"RAG Diet Query: {query}")
        retriever = self._get_hybrid_retriever("nutrition", similarity_top_k=2)
        retrieved_nodes = retriever.retrieve(query)
        return "\n\n".join([scored_node.node.text.strip() for scored_node in retrieved_nodes])

    def get_training_context(self, goal: str, days_per_week: int, equipment: str, injuries: str = "none") -> str:
        query = get_rag_training_query(goal, days_per_week, equipment, injuries)
        print(f"RAG Training Query: {query}")
        retriever = self._get_hybrid_retriever("training", similarity_top_k=2)
        retrieved_nodes = retriever.retrieve(query)
        return "\n\n".join([scored_node.node.text.strip() for scored_node in retrieved_nodes])
