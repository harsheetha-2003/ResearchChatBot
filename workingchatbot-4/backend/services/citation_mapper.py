def map_citations(chunks):
    citations = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        page = meta.get("page", "unknown")
        excerpt = chunk["content"][:150] + "..."
        citations.append({
            "page": page,
            "excerpt": excerpt,
            "confidence": "high"
        })
    return citations
def map_citations(chunks, query):
    """
    Map chunks to citations with relevance scoring
    """
    citations = []
    
    for i, chunk in enumerate(chunks):
        # Simple relevance scoring based on query terms
        content = chunk.get("content", "")
        query_terms = query.lower().split()
        relevance_score = sum(1 for term in query_terms if term in content.lower())
        
        if relevance_score > 0:
            citations.append({
                "source": f"Chunk {i+1}",
                "excerpt": content[:200] + "..." if len(content) > 200 else content,
                "confidence": "high" if relevance_score >= 2 else "medium",
                "metadata": chunk.get("metadata", {})
            })
    
    # Sort by relevance
    citations.sort(key=lambda x: x["confidence"], reverse=True)
    
    return citations[:3]  # Return top 3 citations
