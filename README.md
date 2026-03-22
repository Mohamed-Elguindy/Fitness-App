# AI Fitness Coach — Compound AI System

A production-grade AI backend that acts as a hyper-personalized 
fitness and mentality coaching engine. Built with FastAPI, 
LlamaIndex, and Groq LLM.

## Architecture

This project combines multiple AI patterns into one system:

- **Agentic RAG** — LlamaIndex RouterQueryEngine dynamically routes 
  queries to the correct knowledge base
- **LLM Generation** — Groq LLM generates personalized meal plans 
  and training programs from calculated targets
- **Deterministic Logic** — Pure Python calculators for TDEE, macros,
  and training volume — no AI involved in the math

## Features

- `/coach` — Agentic RAG endpoint that routes fitness and mentality 
  questions to the correct knowledge base
- `/diet-plan` — Generates a fully personalized meal plan based on 
  user stats, goal, intensity, budget, and number of meals
- `/training-program` — Generates a weekly training program based on 
  available time, days, goal, and equipment
- Streamlit UI for interactive testing

## Tech Stack

- **FastAPI** — REST API framework
- **LlamaIndex** — Agentic RAG and vector search
- **Groq** — LLM inference (llama-3.3-70b-versatile)
- **HuggingFace Embeddings** — Local embeddings (BAAI/bge-small-en-v1.5)
- **Pydantic** — Request validation and DTOs
- **Streamlit** — Frontend UI
- **Phoenix** — LLM observability and tracing

## Project Structure
```
agentic-fitness-api/
├── data/
│   ├── fitness_and_diet/    # Nutrition and gym progression data
│   ├── mentality/           # Motivational quotes and mindset data
│   └── general/             # Fallback scope definition
├── ai_core.py               # Agentic RAG router
├── calculator.py            # TDEE, macro, volume calculators
├── diet_builder.py          # LLM meal plan generator
├── program_builder.py       # LLM training program generator
├── schemas.py               # Pydantic DTOs
├── main.py                  # FastAPI endpoints
└── app.py                   # Streamlit UI
```

## Setup

1. Clone the repository
2. Create a virtual environment and activate it
```
   python -m venv venv
   venv\Scripts\activate
```
3. Install dependencies
```
   pip install fastapi uvicorn llama-index python-dotenv groq
   pip install llama-index-llms-groq llama-index-embeddings-huggingface
   pip install streamlit arize-phoenix openinference-instrumentation-llama-index
```
4. Create a `.env` file with your API keys
```
   GROQ_API_KEY=your_key_here
   API_NINJAS_KEY=your_key_here
```
5. Run the FastAPI server
```
   uvicorn main:app --reload
```
6. In a separate terminal run the Streamlit UI
```
   streamlit run app.py
```
7. Open `http://localhost:8501` for the UI
8. Open `http://127.0.0.1:8000/docs` for the API docs

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
```
