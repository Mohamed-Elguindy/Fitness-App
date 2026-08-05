# Phase 1: Chunking Strategy Comparison

This report evaluates four different chunking strategies for the sports science RAG pipeline.

## Strategies Evaluated
1. **Fixed Token Window:** 800 tokens with 150 token overlap. Naive splitting.
2. **Structure:** Splits strictly on document headings/sections.
3. **Hybrid Semantic:** Splits on sections, then uses local embedding similarity (`bge-small`) to find semantic breaks in oversized sections.
4. **Small-to-Big (Sentence Window):** Embeds a single sentence, but retrieves a 7-sentence window (the target sentence + 3 before + 3 after) to provide context.

## Evaluation Methodology (LLM-as-Judge Proxy)
We embedded all chunks using `BAAI/bge-small-en-v1.5` and ran 8 domain-specific test queries. The top 3 chunks for each query were evaluated for **Relevance** and **Completeness** (1-5 scale).

## Results Summary (Average Scores across 8 queries)

| Strategy | Avg Relevance (1-5) | Avg Completeness (1-5) | Overall Score |
|---|---:|---:|---:|
| Fixed | 2.5 | 2.1 | **2.3** |
| Structure | 2.8 | 2.4 | **2.6** |
| Small-to-Big | 3.4 | 3.1 | **3.25** |
| **Hybrid Semantic** | **4.1** | **4.4** | **4.25** |

### Qualitative Analysis

**1. Fixed & Structure (The Losers)**
These strategies consistently struggled with context dilution. Because the chunks were so large (often 1000+ tokens), specific protocols (like creatine dosing) were buried in massive blocks of text. The embedding model failed to rank them highly because the dense technical keywords were diluted by surrounding fluff.

**2. Small-to-Big (The Precision Trap)**
`Small-to-Big` had the highest raw cosine similarity scores (often hitting >0.88). Because it only embeds a single sentence, if that sentence perfectly matches the query, it skyrockets to the top. 
*The problem:* It often retrieved sentences from the **References** section (e.g., a paper title containing all the keywords). Even when it hit actual content, the 7-sentence surrounding window was sometimes disjointed (e.g., crossing over a page break or a section header), resulting in messy context for the LLM. 

**3. Hybrid Semantic (The Winner)**
The Hybrid strategy was the clear winner. By respecting document sections but using local embeddings to split large blocks precisely when the topic shifts, it produced chunks that were:
1. **Dense enough** to trigger high similarity scores.
2. **Complete enough** to contain the entire thought/protocol without disjointed boundaries.

For example, on the *"creatine loading protocol"* query, Hybrid cleanly extracted the exact paragraph detailing the 4-6 week saturation timeline, while Small-to-Big extracted a reference citation.

## Decision
**Winner: Hybrid Semantic Chunking.** 
We will proceed with the Hybrid chunks (`phase1_hybrid_chunks.jsonl`) for building the persisted indices in Phase 3.
