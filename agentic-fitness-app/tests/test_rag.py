import pytest
from knowledge_base import get_index

def test_nutrition_index_retrieval():
    """Test that the persisted nutrition index retrieves high-quality context."""
    index = get_index("nutrition")
    retriever = index.as_retriever(similarity_top_k=3)
    
    # Test query
    nodes = retriever.retrieve("creatine loading protocol")
    
    # We expect the response to contain actual retrieved source nodes
    assert len(nodes) > 0, "No chunks were retrieved!"
    
    # Check if the score of the top chunk is reasonably high (baseline check)
    top_score = nodes[0].score
    assert top_score > 0.70, f"Top retrieval score ({top_score}) is below baseline!"
    
    # Check if text contains relevant keywords to ensure semantic matching worked
    text = nodes[0].text.lower()
    assert "creatine" in text, "Top chunk is missing the subject keyword."

def test_training_index_retrieval():
    """Test that the persisted training index retrieves high-quality context."""
    index = get_index("training")
    retriever = index.as_retriever(similarity_top_k=3)
    
    nodes = retriever.retrieve("hypertrophy rest periods")
    assert len(nodes) > 0, "No chunks were retrieved for training!"
    assert nodes[0].score > 0.70, "Top retrieval score is below baseline for training!"
