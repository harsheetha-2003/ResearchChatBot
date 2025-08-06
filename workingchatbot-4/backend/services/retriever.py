import re
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from services.chat_history import save_chat_entry
 
# ✅ Section-aware filtering logic with expanded synonyms
SECTION_HEADERS = {
    "methods": ["materials and methods", "methodology", "experimental procedures"],
    "results": ["results", "findings", "key findings", "observations"],
    "conclusion": ["conclusion", "conclusions", "summary", "final thoughts", "takeaways", "closing remarks"],
    "analysis": ["nutrient composition analysis", "data analysis", "statistical analysis"]
}
 
def get_relevant_section(text, query, chunks):
    query_lower = query.lower()
    matched_section = None
 
    for section, keywords in SECTION_HEADERS.items():
        if any(keyword in query_lower for keyword in keywords):
            matched_section = section
            break
 
    if matched_section:
        # ✅ Loosened regex to match section headers inline or with minimal formatting
        pattern = r"(?i)(" + "|".join(SECTION_HEADERS[matched_section]) + r")[^\n]{0,100}([\s\S]{0,1500})"
        match = re.search(pattern, text)
        if match:
            print(f"[DEBUG] Matched section: {matched_section}")
            return match.group(2).strip()
 
    # ✅ Semantic fallback: find most relevant chunk
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    query_embedding = embedder.embed_query(query)
 
    best_score = -1
    best_chunk = None
    for chunk in chunks:
        content = chunk.get("content", "")
        chunk_embedding = embedder.embed_documents([content])[0]
        score = sum([a * b for a, b in zip(query_embedding, chunk_embedding)])
        if score > best_score:
            best_score = score
            best_chunk = content
 
    if best_chunk:
        print("[DEBUG] Used semantic fallback matching.")
        return best_chunk.strip()
 
    # ✅ Fallback: try to extract last 1000 characters assuming conclusion is near the end
    print("[DEBUG] No section matched. Using end-of-document fallback.")
    return text[-1000:].strip()
 
def retrieve_chunks(doc_id, query, exact_match=False):
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
 
    vectorstore = FAISS.load_local(
        f"data/embeddings/{doc_id}_index",
        embedder,
        allow_dangerous_deserialization=True
    )
 
    # ✅ Retrieve top matching documents
    docs = vectorstore.similarity_search(query, k=15)
 
    chunks = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in docs
    ]
 
    # ✅ Combine all chunk content into one context
    full_context = "\n\n".join([doc.page_content for doc in docs])
 
    # ✅ Apply section-aware filtering or semantic fallback
    filtered_context = get_relevant_section(full_context, query, chunks)
 
    # ✅ Build answer
    text = filtered_context.strip()
    text = text.replace("\n", " ").replace("  ", " ")
    text = re.sub(r"\[\d+(,\d+)*\]", "", text)
 
    # ✅ Out-of-scope detection
    if len(text) < 100 or "not found" in text.lower():
        answer = "This content is not present in the uploaded research paper."
    else:
        answer = text[:1000] + "..." if len(text) > 1000 else text
 
    # ✅ Save to chat history
    save_chat_entry(doc_id, query, answer)
 
    return {
        "chunks": chunks,
        "answer": answer
    }