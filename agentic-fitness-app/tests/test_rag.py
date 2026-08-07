import pytest
from app.services.rag_service import RAGService

@pytest.fixture(scope="module")
def rag_service():
    return RAGService()

def test_fitness_and_diet_index_retrieval(rag_service):
    """Test that the persisted fitness_and_diet index retrieves high-quality context."""
    index = rag_service._get_index("fitness_and_diet")
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

def test_mentality_index_retrieval(rag_service):
    """Test that the persisted mentality index retrieves high-quality context."""
    index = rag_service._get_index("mentality")
    retriever = index.as_retriever(similarity_top_k=3)
    
    nodes = retriever.retrieve("motivation and discipline")
    assert len(nodes) > 0, "No chunks were retrieved for mentality!"
    assert nodes[0].score > 0.70, "Top retrieval score is below baseline for mentality!"
