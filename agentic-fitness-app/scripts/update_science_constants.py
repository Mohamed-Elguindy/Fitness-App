import json
import os
import sys
from pathlib import Path
from pydantic import BaseModel, Field
import instructor
from groq import Groq

# Add app root to path so we can import modules
app_root = Path(__file__).resolve().parent.parent
sys.path.append(str(app_root))

from app.services.rag_service import RAGService
from app.core.config import settings

# 1. Define the Strict Pydantic Schema for the JSON we want
class ProteinMultipliers(BaseModel):
    bulk: float = Field(description="Optimal protein multiplier for bulking (g/kg)")
    cut: float = Field(description="Optimal protein multiplier for cutting (g/kg)")
    maintenance: float = Field(description="Optimal protein multiplier for maintenance (g/kg)")

class ModifierSet(BaseModel):
    lean: int = Field(description="Calorie amount for lean surplus/deficit")
    moderate: int = Field(description="Calorie amount for moderate surplus/deficit")
    aggressive: int = Field(description="Calorie amount for aggressive surplus/deficit")

class CaloricModifiers(BaseModel):
    bulk_surplus: ModifierSet
    cut_deficit: ModifierSet

class TrainingVolumeStats(BaseModel):
    optimal_sets_per_exercise: int = Field(description="Optimal number of sets per exercise")
    optimal_exercises: int = Field(description="Optimal number of exercises per session")
    optimal_weekly_sets_per_muscle: int = Field(description="Optimal number of sets per muscle group per week")
    rep_range: str = Field(description="Optimal rep range, e.g., '3-6' or '6-12'")
    rest_seconds: int = Field(description="Optimal rest between sets in seconds")

class TrainingVolume(BaseModel):
    strength: TrainingVolumeStats
    hypertrophy: TrainingVolumeStats

class Supplements(BaseModel):
    creatine_maintenance_g: float = Field(description="Maintenance dose of creatine in grams")
    creatine_loading_g: float = Field(description="Loading phase dose of creatine in grams")

class Metadata(BaseModel):
    last_updated: str
    sources: list[str]

class ScienceConstants(BaseModel):
    protein_multipliers: ProteinMultipliers
    caloric_modifiers: CaloricModifiers
    training_volume: TrainingVolume
    supplements: Supplements
    metadata: Metadata

def build_constants() -> dict:
    print("Initializing RAG Service to fetch scientific context...")
    rag = RAGService()
    
    print("Retrieving nutrition science chunks...")
    nutrition_retriever = rag._get_hybrid_retriever("nutrition")
    nutrition_nodes = nutrition_retriever.retrieve("What is the optimal protein intake for bulking, cutting, and maintenance? What is the optimal caloric surplus and deficit? What is the optimal creatine dosage?")
    nutrition_context = "\n\n".join([n.node.text for n in nutrition_nodes])

    print("Retrieving training science chunks...")
    training_retriever = rag._get_hybrid_retriever("training")
    training_nodes = training_retriever.retrieve("What is the optimal training volume, sets, reps, optimal weekly sets per muscle, and rest periods for strength versus hypertrophy?")
    training_context = "\n\n".join([n.node.text for n in training_nodes])

    print("Connecting to Groq for structured extraction...")
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    # We use instructor to guarantee Pydantic schema validation from Groq
    instructor_client = instructor.from_groq(client, mode=instructor.Mode.JSON)

    system_prompt = """
    You are a senior sports scientist. Extract the exact optimal physiological constants 
    from the provided research chunks. You MUST return a valid JSON matching the exact schema provided.
    If the context does not explicitly mention a value, use standard sports science consensus (e.g. 1.6 for bulk, 2.2 for cut, 5g creatine maintenance).
    """

    full_context = f"NUTRITION CONTEXT:\n{nutrition_context}\n\nTRAINING CONTEXT:\n{training_context}"

    print("Asking Groq LLM to read chunks and dynamically build the JSON schema...")
    extracted_data = instructor_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=ScienceConstants,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_context}
        ]
    )
    
    print("Groq successfully returned strictly validated Pydantic model!")
    return extracted_data.model_dump()

def main():
    try:
        constants = build_constants()
        
        output_path = app_root / "data" / "science_constants.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(constants, f, indent=2)
            
        print(f"Successfully autonomously generated and validated constants.")
        print(f"Saved to {output_path}")
    except Exception as e:
        print(f"Extraction failed: {str(e)}")

if __name__ == "__main__":
    main()
