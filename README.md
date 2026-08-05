# AI Fitness Coach — Compound AI System

A production-grade AI backend that acts as a hyper-personalized 
fitness and mentality coaching engine. Built with FastAPI, 
LlamaIndex, and Groq LLM.

## Architecture

This project combines multiple AI patterns into one system:

- **Agentic RAG** — LlamaIndex RouterQueryEngine dynamically routes 
  queries to the correct knowledge base.
- **Advanced Chunking** — Employs Hybrid Semantic chunking on source PDFs for optimal retrieval.
- **Zero Cold-Start Persistence** — Pre-computed local embeddings are persisted to disk, eliminating startup delays.
- **LLM Generation** — Groq LLM generates personalized meal plans 
  and training programs from calculated targets.
- **Deterministic Logic** — Pure Python calculators for TDEE, macros,
  and training volume — no AI involved in the math.

## Features

- `/coach` — Agentic RAG endpoint that routes fitness and mentality 
  questions to the correct knowledge base.
- `/diet-plan` — Generates a fully personalized meal plan based on 
  user stats, goal, intensity, budget, and number of meals.
- `/training-program` — Generates a weekly training program based on 
  available time, days, goal, and equipment.
- Streamlit UI for interactive testing.

## Tech Stack

- **FastAPI** — REST API framework
- **LlamaIndex** — Agentic RAG, vector search, and storage
- **Groq** — LLM inference (llama-3.3-70b-versatile)
- **HuggingFace Embeddings** — Local embeddings (BAAI/bge-small-en-v1.5)
- **GitHub Actions** — CI/CD for automated PDF data ingestion and RAG testing
- **Pydantic** — Request validation and DTOs
- **Streamlit** — Frontend UI
- **Phoenix** — LLM observability and tracing

## Project Structure
```
agentic-fitness-api/
├── data/
│   ├── fitness_and_diet/    # Legacy nutrition/gym data
│   ├── mentality/           # Motivational quotes and mindset data
│   ├── general/             # Fallback scope definition
│   ├── nutrition_papers/    # Sports science PDFs (auto-chunked by CI/CD)
│   └── training_papers/     # Sports science PDFs (auto-chunked by CI/CD)
├── storage/                 # Pre-computed local vector database
├── ai_core.py               # Agentic RAG router
├── knowledge_base.py        # Storage context and index loader
├── calculator.py            # TDEE, macro, volume calculators
├── diet_builder.py          # LLM meal plan generator
├── program_builder.py       # LLM training program generator
├── schemas.py               # Pydantic DTOs
├── main.py                  # FastAPI endpoints
├── app.py                   # Streamlit UI
└── tests/                   # Pytest suite for RAG evaluation
```

## CI/CD Pipelines
This project includes two automated GitHub Actions workflows:
1. **Data Ingestion (`data-ingestion.yml`)**: Whenever new PDFs are added to `data/*_papers/`, this pipeline automatically chunks the documents, embeds them via BGE-small, and commits the updated vector database (`storage/`) back to the repository.
2. **RAG Evaluation (`rag-eval.yml`)**: On every Pull Request, an automated suite of Golden Queries is run against the database to mathematically guarantee the search precision remains high (similarity score `> 0.70`).

## Setup

1. Clone the repository
2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate    # On Mac/Linux
venv\Scripts\activate       # On Windows
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Create a `.env` file with your API keys
```env
GROQ_API_KEY=your_key_here
API_NINJAS_KEY=your_key_here
```
5. Run the FastAPI server
```bash
uvicorn main:app --reload
```
6. In a separate terminal run the Streamlit UI
```bash
cd agentic-fitness-app
streamlit run app.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/coach` | Ask fitness or mentality questions |
| POST | `/diet-plan` | Generate personalized meal plan |
| POST | `/training-program` | Generate weekly training program |

## How The Routing Works

The `/coach` endpoint uses LlamaIndex's `RouterQueryEngine` with 
`LLMSingleSelector`. When a query arrives the LLM reads the tool 
descriptions and decides which knowledge base to search before 
generating an answer. This is Agentic RAG — retrieval plus 
decision making.
