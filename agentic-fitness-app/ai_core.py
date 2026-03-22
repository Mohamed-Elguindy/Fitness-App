import os
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import threading
threading.Thread(target=lambda: None, daemon=True).start()
import phoenix as px
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from phoenix.otel import register  

load_dotenv()

#session = px.launch_app()

#tracer_provider = register(
#    project_name="fitness-coach-agent" # Optional, but keeps things organized in the UI)

#LlamaIndexInstrumentor().instrument(skip_dep_check=True)

Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Load documents
fitness_docs = SimpleDirectoryReader("data/fitness_and_diet").load_data()
mentality_docs = SimpleDirectoryReader("data/mentality").load_data()
general_docs = SimpleDirectoryReader("data/general").load_data()

# Build indices
fitness_index = VectorStoreIndex.from_documents(fitness_docs)
mentality_index = VectorStoreIndex.from_documents(mentality_docs)
general_index = VectorStoreIndex.from_documents(general_docs)

# Wrap as tools with descriptions
fitness_tool = QueryEngineTool.from_defaults(
    query_engine=fitness_index.as_query_engine(),
    description="Useful for answering physiological, nutritional, and workout programming questions about bulking, cutting, and gym exercises like bench press, deadlift, and lat pulldown."
)

mentality_tool = QueryEngineTool.from_defaults(
    query_engine=mentality_index.as_query_engine(
        similarity_top_k=1,
        response_mode="compact"
    ),
    description="Useful for addressing discipline, lack of motivation, fatigue, wanting to quit, or any psychological barriers using intense tough-love advice."
)
general_tool = QueryEngineTool.from_defaults(
    query_engine=general_index.as_query_engine(),
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