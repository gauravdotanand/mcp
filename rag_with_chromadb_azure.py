import chromadb
from chromadb.config import Settings
from openai import AzureOpenAI
import os
from pypdf import PdfReader

# Dummy Azure OpenAI credentials (replace with real ones for production)
AZURE_OPENAI_ENDPOINT = "https://dummy-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY = "dummy-api-key"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "dummy-embedding-deployment"
AZURE_OPENAI_API_VERSION = "2023-05-15"

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
)

def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding

# PDF extraction and chunking

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return [c for c in chunks if c.strip()]

# Find a PDF file in the current directory (or use a dummy path)
pdf_path = None
for fname in os.listdir('.'):
    if fname.lower().endswith('.pdf'):
        pdf_path = fname
        break
if not pdf_path:
    pdf_path = "dummy.pdf"  # Replace with your PDF file
    print(f"No PDF found. Please place a PDF in the directory and update 'pdf_path'.")

# Extract and chunk PDF text
if os.path.exists(pdf_path):
    full_text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(full_text, chunk_size=300, overlap=50)
else:
    chunks = ["This is a dummy chunk. Please provide a real PDF file."]

# Prepare embeddings and metadata for each chunk
embeddings = [get_embedding(chunk) for chunk in chunks]
metadatas = [{"chunk_index": i, "source": pdf_path} for i in range(len(chunks))]

# Initialize ChromaDB client (in-memory for demo)
chroma_client = chromadb.Client(Settings(
    persist_directory=None  # In-memory
))

# Create a collection for documents
collection = chroma_client.create_collection(name="rag-demo")

# Add chunks to ChromaDB with embeddings and metadata
for i, (text, embedding, metadata) in enumerate(zip(chunks, embeddings, metadatas)):
    collection.add(
        ids=[f"doc_{i}"],
        documents=[text],
        embeddings=[embedding],
        metadata=[metadata]
    )

# Sample user query
query = "Summarize the main points from the document."
query_embedding = get_embedding(query)

# Retrieve top-2 most similar chunks
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2,
    include=["documents", "distances"]
)

print("Query:", query)
print("Top results:")
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    print(f"- {doc[:200]}... (distance: {dist:.4f})") 