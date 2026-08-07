import time
from app.services.rag_service import RAGService
from app.core.config import settings

rag_service = RAGService()

start = time.time()
print("Starting query...")
res = rag_service.ask_coach("What is the best way to bulk up?")
end = time.time()

print(f"Time taken: {end - start:.2f} seconds")
print("Response:", str(res)[:100], "...")
