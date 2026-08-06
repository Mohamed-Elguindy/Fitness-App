import os
import warnings
warnings.filterwarnings("ignore")

# Fix for macOS memory corruption crash in HuggingFace Tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# Tracing disabled due to SQLite lock issues
from dotenv import load_dotenv
load_dotenv()

Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
from knowledge_base import get_hybrid_retriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Load Hybrid Retrievers (Semantic + Keyword)
fitness_retriever = get_hybrid_retriever("fitness_and_diet")
mentality_retriever = get_hybrid_retriever("mentality")
general_retriever = get_hybrid_retriever("general")

# Convert Retrievers to Query Engines
fitness_qe = RetrieverQueryEngine.from_args(fitness_retriever)
mentality_qe = RetrieverQueryEngine.from_args(mentality_retriever)
general_qe = RetrieverQueryEngine.from_args(general_retriever)

# Wrap as tools with descriptions
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

# Build the router
router = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[fitness_tool, mentality_tool, general_tool]
)

# The brain function
def ask_coach(prompt: str) -> str:
    response = router.query(prompt)
    return str(response)

# Test both routes 
#print("--- FITNESS TEST ---")
#print(ask_coach("How many calories should I eat to bulk?"))

#print("--- MENTALITY TEST ---")
#print(ask_coach("I feel like quitting my workout today"))
#input("Press Enter to close the Phoenix server and exit...")

# Gracefully shut down the Phoenix server to release the database file
#px.close_app()