import time
from ai_core import ask_coach

start = time.time()
print("Starting query...")
res = ask_coach("What is the best way to bulk up?")
end = time.time()

print(f"Time taken: {end - start:.2f} seconds")
print("Response:", str(res)[:100], "...")
