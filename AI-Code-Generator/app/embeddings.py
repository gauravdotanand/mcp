from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple
import logging

# Initialize the embedding model (using a lightweight model for code)
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dimensional embeddings

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a given text"""
    try:
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return None

def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings"""
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    except Exception as e:
        logging.error(f"Error calculating similarity: {e}")
        return 0.0

def find_most_similar_samples(
    query_embedding: List[float], 
    sample_embeddings: List[Tuple[int, List[float]]], 
    top_k: int = 3
) -> List[int]:
    """Find the most similar samples based on embedding similarity"""
    similarities = []
    
    for sample_id, sample_embedding in sample_embeddings:
        if sample_embedding is not None:
            similarity = calculate_similarity(query_embedding, sample_embedding)
            similarities.append((sample_id, similarity))
    
    # Sort by similarity (highest first) and return top_k sample IDs
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [sample_id for sample_id, _ in similarities[:top_k]]

def create_search_text(title: str, code_sample: str, coding_style_summary: str = None) -> str:
    """Create searchable text for embedding generation"""
    search_parts = [title]
    
    # Add coding style summary if available
    if coding_style_summary:
        search_parts.append(coding_style_summary)
    
    # Add key parts of the code (first 500 chars for search)
    code_preview = code_sample[:500] if code_sample else ""
    search_parts.append(code_preview)
    
    return " ".join(search_parts) 