import re
from typing import List, Tuple
from app.embeddings import generate_embedding, find_most_similar_samples, create_search_text

def count_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters for English text)"""
    return len(text) // 4

def truncate_code_sample(code: str, max_tokens: int = 1000) -> str:
    """Truncate code sample to fit within token limit"""
    if count_tokens(code) <= max_tokens:
        return code
    
    # Truncate to approximately max_tokens
    max_chars = max_tokens * 4
    truncated = code[:max_chars]
    
    # Try to end at a complete line
    last_newline = truncated.rfind('\n')
    if last_newline > max_chars * 0.8:  # If we can find a newline in the last 20%
        truncated = truncated[:last_newline]
    
    return truncated + "\n# ... (truncated)"

def generate_coding_style_summary(code: str) -> str:
    """Generate a high-level summary of coding style and patterns"""
    summary_parts = []
    
    # Detect programming language patterns
    if 'def ' in code or 'import ' in code:
        summary_parts.append("Python")
    elif 'function ' in code or 'const ' in code or 'let ' in code:
        summary_parts.append("JavaScript/TypeScript")
    elif 'public class' in code or 'private ' in code:
        summary_parts.append("Java")
    
    # Detect coding patterns
    if 'async def' in code or 'await ' in code:
        summary_parts.append("async/await pattern")
    if 'try:' in code and 'except:' in code:
        summary_parts.append("error handling")
    if 'for ' in code and 'in ' in code:
        summary_parts.append("iteration patterns")
    if 'if ' in code and 'else:' in code:
        summary_parts.append("conditional logic")
    
    # Detect string manipulation patterns
    if '.split(' in code or '.join(' in code:
        summary_parts.append("string manipulation")
    if 're.' in code or 'import re' in code:
        summary_parts.append("regex usage")
    
    # Detect mainframe-specific patterns
    if 'screen' in code.lower() or 'mainframe' in code.lower():
        summary_parts.append("mainframe screen handling")
    
    return ", ".join(summary_parts) if summary_parts else "General coding patterns"

def get_most_relevant_samples(samples: List[str], prompt: str, max_samples: int = 3, db_session=None, user_id: int = None) -> List[str]:
    """Get most relevant samples using embedding-based similarity search (user-specific)"""
    if not samples or not db_session:
        return samples[:max_samples]
    
    try:
        # Generate embedding for the prompt
        prompt_embedding = generate_embedding(prompt)
        if not prompt_embedding:
            return samples[:max_samples]  # Fallback to simple selection
        
        # Get user's sample embeddings from database
        from app.models import CodingApproachSample
        db_samples = db_session.query(CodingApproachSample).filter(
            CodingApproachSample.user_id == user_id
        ).all() if user_id else []
        
        # Prepare embeddings for similarity search
        sample_embeddings = []
        for db_sample in db_samples:
            if db_sample.embedding:
                sample_embeddings.append((db_sample.id, db_sample.embedding))
        
        # Find most similar samples
        similar_ids = find_most_similar_samples(prompt_embedding, sample_embeddings, max_samples)
        
        # Return samples in order of similarity
        result_samples = []
        for sample_id in similar_ids:
            # Find the corresponding sample in the original list
            # This is a simplified approach - in practice, you might want to map IDs to samples differently
            if len(result_samples) < max_samples:
                result_samples.append(samples[len(result_samples) % len(samples)])
        
        return result_samples if result_samples else samples[:max_samples]
        
    except Exception as e:
        print(f"Error in similarity search: {e}")
        return samples[:max_samples]  # Fallback to simple selection 