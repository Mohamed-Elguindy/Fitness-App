import time
from app.services.rag_service import RAGService
from app.core.config import settings

rag_service = RAGService()

print("--- FIRST RUN (Building) ---")
start = time.time()
rag_service._get_index("fitness_and_diet")
rag_service._get_index("mentality")
print(f"First run took: {time.time() - start:.2f}s")

print("\n--- SECOND RUN (Loading) ---")
start = time.time()
rag_service._get_index("fitness_and_diet")
rag_service._get_index("mentality")
print(f"Second run took: {time.time() - start:.2f}s")
