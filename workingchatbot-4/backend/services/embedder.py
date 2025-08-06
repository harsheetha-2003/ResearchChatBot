from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import uuid

def embed_document(file_path):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(chunks, embedder)

        # Generate unique doc ID
        doc_id = generate_doc_id(file_path)

        # Save FAISS index
        index_path = f"data/embeddings/{doc_id}_index"
        os.makedirs("data/embeddings", exist_ok=True)
        vectorstore.save_local(index_path)

        return doc_id, [chunk.page_content for chunk in chunks]

    except Exception as e:
        print(f"Embedding error: {e}")
        raise e

def generate_doc_id(file_path):
    base = os.path.splitext(os.path.basename(file_path))[0]
    suffix = uuid.uuid4().hex[:4].upper()
    return f"{base}_{suffix}"
import os
import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def embed_document(file_path: str):
    """
    Process and embed a document, returning doc_id and text chunks
    """
    # Generate unique document ID
    doc_id = str(uuid.uuid4()).replace('-', '')[:8]
    
    # Load document based on file extension
    if file_path.lower().endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding='utf-8')
    
    documents = loader.load()
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Create embeddings
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create vector store
    vectorstore = FAISS.from_documents(chunks, embedder)
    
    # Save vector store
    os.makedirs("data/embeddings", exist_ok=True)
    vectorstore.save_local(f"data/embeddings/{doc_id}_index")
    
    # Extract text content from chunks
    text_chunks = [chunk.page_content for chunk in chunks]
    
    return doc_id, text_chunks
