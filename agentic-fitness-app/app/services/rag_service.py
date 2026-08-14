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
from llama_index.core.query_engine import RouterQueryEngine, RetrieverQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.llms.gemini import Gemini

from app.core.config import settings

class RAGService:
    def __init__(self):
        # We use llama_index's Gemini wrapper here instead of the raw client
        if settings.GEMINI_API_KEY == "dummy_testing_key_for_ci":
            Settings.llm = MockLLM()
        else:
            Settings.llm = Gemini(model="models/gemini-3.6-flash", api_key=settings.GEMINI_API_KEY)
            
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
        nodes = []
        if not self.chunks_jsonl_path.exists():
            raise FileNotFoundError(f"Missing chunks file: {self.chunks_jsonl_path}")
            
        with open(self.chunks_jsonl_path, "r", encoding="utf-8") as f:
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

    def _build_index_from_directory(self, domain: str) -> VectorStoreIndex:
        data_path = self.data_dir / domain
        if not data_path.exists():
            raise FileNotFoundError(f"Missing data directory: {data_path}")
            
        print(f"Reading documents for {domain}...")
        docs = SimpleDirectoryReader(str(data_path)).load_data()
        print(f"Building {domain} index from raw documents...")
        return VectorStoreIndex.from_documents(docs)

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
        nodes = list(index.docstore.docs.values())
        actual_k = min(similarity_top_k, len(nodes)) if nodes else 1
        
        vector_retriever = index.as_retriever(similarity_top_k=actual_k * 3)
        return vector_retriever

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

        fitness_qe = RetrieverQueryEngine.from_args(
            fitness_retriever,
            node_postprocessors=[reranker]
        )
        mentality_qe = RetrieverQueryEngine.from_args(
            mentality_retriever,
            node_postprocessors=[reranker]
        )
        general_qe = RetrieverQueryEngine.from_args(
            general_retriever,
            node_postprocessors=[reranker]
        )

        fitness_tool = QueryEngineTool.from_defaults(
            query_engine=fitness_qe,
            description="Useful for answering physiological, nutritional, and workout programming questions about bulking, cutting, and gym exercises like bench press, deadlift, and lat pulldown."
        )

        mentality_tool = QueryEngineTool.from_defaults(
            query_engine=mentality_qe,
            description="Useful for addressing discipline, lack of motivation, fatigue, wanting to quit, or any psychological barriers using intense tough-love advice."
        )
        general_tool = QueryEngineTool.from_defaults(
            query_engine=general_qe,
            description="Useful for any question that is NOT related to fitness, gym training, nutrition, bulking, cutting, or workout mentality. Use this for all off-topic questions."
        )

        return RouterQueryEngine(
            selector=LLMSingleSelector.from_defaults(),
            query_engine_tools=[fitness_tool, mentality_tool, general_tool]
        )

    def ask_coach(self, prompt: str) -> str:
        response = self.router.query(prompt)
        return str(response)

    def get_diet_context(self, goal: str, dietary_restrictions: str = "none") -> str:
        query = f"What are the most important sports science rules for meal timing, protein distribution, and nutrient partitioning for a {goal} diet? Special considerations: {dietary_restrictions}."
        print(f"RAG Diet Query: {query}")
        retriever = self._get_hybrid_retriever("nutrition", similarity_top_k=2)
        nodes = retriever.retrieve(query)
        return "\n\n".join([n.node.text.strip() for n in nodes])

    def get_training_context(self, goal: str, days_per_week: int, equipment: str, injuries: str = "none") -> str:
        query = f"What are the scientific rules for exercise selection, fatigue management, and volume for a {goal} program that trains {days_per_week} days a week using {equipment} equipment? Special injury considerations: {injuries}."
        print(f"RAG Training Query: {query}")
        retriever = self._get_hybrid_retriever("training", similarity_top_k=2)
        nodes = retriever.retrieve(query)
        return "\n\n".join([n.node.text.strip() for n in nodes])
