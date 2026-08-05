import time
from knowledge_base import get_index

print("--- FIRST RUN (Building) ---")
start = time.time()
get_index("fitness_and_diet")
get_index("nutrition")
print(f"First run took: {time.time() - start:.2f}s")

print("\n--- SECOND RUN (Loading) ---")
start = time.time()
get_index("fitness_and_diet")
get_index("nutrition")
print(f"Second run took: {time.time() - start:.2f}s")
