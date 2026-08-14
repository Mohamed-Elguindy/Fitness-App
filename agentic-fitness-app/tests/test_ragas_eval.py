import pytest
import os
import instructor
import google.generativeai as genai
from pydantic import BaseModel, Field
from app.services.rag_service import RAGService
from app.core.config import settings

class RagasEvaluation(BaseModel):
    faithfulness_score: int = Field(..., description="Score from 0 to 5. 5 means the answer is completely supported by the context without hallucination.")
    faithfulness_reasoning: str = Field(..., description="Step-by-step reasoning for the faithfulness score.")
    relevance_score: int = Field(..., description="Score from 0 to 5. 5 means the answer perfectly addresses the user query.")
    relevance_reasoning: str = Field(..., description="Step-by-step reasoning for the relevance score.")

@pytest.fixture(scope="module")
def rag_service():
    return RAGService()

@pytest.fixture(scope="module")
def judge_client():
    if settings.GEMINI_API_KEY == "dummy_testing_key_for_ci":
        pytest.skip("Skipping RAGAS eval in standard CI due to missing API Key.")
        
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # We use a cold, analytical model (temperature 0.0) for objective grading
    client = instructor.from_gemini(
        client=genai.GenerativeModel(model_name="models/gemini-3.6-flash", generation_config={"temperature": 0.0}),
        mode=instructor.Mode.GEMINI_JSON
    )
    return client

def run_ragas_evaluation(query: str, rag_service: RAGService, judge_client) -> RagasEvaluation:
    """Executes the RAG pipeline and evaluates its output using the LLM judge."""
    
    # 1. Run the RAG pipeline to get Answer + Context
    response = rag_service.router.query(query)
    
    final_answer = str(response)
    context_blocks = [n.node.text for n in response.source_nodes]
    retrieved_context = "\n\n---\n\n".join(context_blocks)
    
    # 2. Build the Evaluation Prompt
    eval_prompt = f"""
You are an impartial AI Judge. Your task is to evaluate the quality of a RAG (Retrieval-Augmented Generation) pipeline.

USER QUERY: 
{query}

RETRIEVED CONTEXT:
{retrieved_context}

AI'S FINAL ANSWER:
{final_answer}

Evaluate the AI's final answer on two metrics:
1. Faithfulness (0-5): Does the final answer rely STRICTLY on the retrieved context? If it hallucinates outside knowledge not present in the context, penalize it heavily.
2. Relevance (0-5): Did the final answer actually answer the user's query directly and accurately?
"""
    
    # 3. Request the structured JSON evaluation
    eval_result = judge_client.chat.completions.create(
        response_model=RagasEvaluation,
        messages=[
            {"role": "system", "content": "You are a strict, objective grading system."},
            {"role": "user", "content": eval_prompt}
        ]
    )
    
    return eval_result

def test_ragas_fitness_query(rag_service, judge_client):
    """Evaluates if the fitness index can accurately pull and synthesize technical protein data."""
    query = "What is the optimal protein intake for muscle growth?"
    result = run_ragas_evaluation(query, rag_service, judge_client)
    
    print(f"\n[Fitness Query Eval] Faithfulness: {result.faithfulness_score}/5 | Relevance: {result.relevance_score}/5")
    print(f"Reasoning: {result.faithfulness_reasoning} | {result.relevance_reasoning}")
    
    assert result.faithfulness_score >= 4, f"Faithfulness too low: {result.faithfulness_reasoning}"
    assert result.relevance_score >= 4, f"Relevance too low: {result.relevance_reasoning}"

def test_ragas_mentality_query(rag_service, judge_client):
    """Evaluates if the mentality index accurately pulls tough-love motivation without making up facts."""
    query = "I want to quit the gym because it is too hard. Give me tough love."
    result = run_ragas_evaluation(query, rag_service, judge_client)
    
    print(f"\n[Mentality Query Eval] Faithfulness: {result.faithfulness_score}/5 | Relevance: {result.relevance_score}/5")
    print(f"Reasoning: {result.faithfulness_reasoning} | {result.relevance_reasoning}")
    
    assert result.faithfulness_score >= 4, f"Faithfulness too low: {result.faithfulness_reasoning}"
    assert result.relevance_score >= 4, f"Relevance too low: {result.relevance_reasoning}"
