import fitz  # PyMuPDF

def process_document(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    # Chunk into 500-character blocks
    return [text[i:i+500] for i in range(0, len(text), 500)]
