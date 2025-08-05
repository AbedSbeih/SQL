from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import os

# Directory containing PDFs
pdf_directory = r"C:\Users\DELL\Documents\GradProj\real_data"

# ---------- Extract text from PDF ----------
def extract_text_from_pdf(pdf_file_path):
    text = ""
    reader = PdfReader(pdf_file_path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

# ---------- Create text chunks ----------
def make_chunks(text, chunk_size=500, overlap=50):
    """Split text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    return text_splitter.split_text(text)

# ---------- Setup ChromaDB ----------
client = chromadb.Client()
collection = client.create_collection(name="pdf_collection")

# ---------- PDF files ----------
pdf_files = ["University_Admission_FAQs_English.pdf", "دليل الطالب.pdf"]

# ---------- Process PDFs and store chunks ----------
doc_id = 1
for pdf_file in pdf_files:
    pdf_path = os.path.join(pdf_directory, pdf_file)
    file_found = False

    
    if os.path.exists(pdf_path):
            print(f"📄 Reading {pdf_file} ...")
            pdf_text = extract_text_from_pdf(pdf_path)
            chunks = make_chunks(pdf_text)

            # Store each chunk with filename metadata
            for chunk in chunks:
                collection.add(
                    ids=[str(doc_id)],
                    documents=[chunk],
                    metadatas=[{"filename": pdf_file}]
                )
                doc_id += 1

            print(f"✅ Added {len(chunks)} chunks from {pdf_file} to ChromaDB.")
            file_found = True
            

    if not file_found:
        print(f"⚠️ File not found: {pdf_file}")
        print(f"   Searched in: {pdf_directory}")

# ---------- Query ChromaDB ----------
query = "الحصول على المنح الدراسية"
results = collection.query(
    query_texts=[query],
    n_results=5  # retrieve top 5 chunks
)

# ---------- Display results ----------
print("\n🔍 Query:", query)
for doc, meta, score in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
):
    print(f"📄 From file: {meta['filename']}")
    print(f"📝 Content snippet: {doc[:300]}...")
    print(f"📊 Similarity Score: {score:.4f}")
    print("-" * 60)
