import torch
from pathlib import Path
import ollama
from sentence_transformers import CrossEncoder
import numpy as np
from typing import List, Tuple

# Create models directory if it doesn't exist
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

def get_local_cross_encoder():
    """Get or download the cross-encoder model for reranking."""
    model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    model_path = MODELS_DIR / model_name.replace("/", "_")
    
    if not model_path.exists():
        model = CrossEncoder(model_name, device="cuda" if torch.cuda.is_available() else "cpu")
        model.save(str(model_path))
    else:
        model = CrossEncoder(str(model_path), device="cuda" if torch.cuda.is_available() else "cpu")
    
    return model

def re_rank_cross_encoders(documents: List[str], prompt: str) -> Tuple[str, List[int]]:
    """Rerank documents using cross-encoder model."""
    if not documents:
        return "", []
        
    try:
        # Ensure documents is a list of strings
        documents = [str(doc) for doc in documents if doc]
        if not documents:
            return "", []
            
        relevant_text = ""
        relevant_text_ids = []
        encoder_model = get_local_cross_encoder()
        
        # Create pairs of (query, document) for ranking
        pairs = [(prompt, doc) for doc in documents]
        
        # Get scores for each pair
        scores = encoder_model.predict(pairs)
        
        # Convert scores to numpy array if it's not already
        scores = np.array(scores)
        
        # Get top 3 documents
        top_k = min(3, len(documents))
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        # Combine top documents and their indices
        for idx in top_indices:
            idx_int = int(idx)  # Convert numpy.int64 to Python int
            if 0 <= idx_int < len(documents):  # Ensure index is valid
                relevant_text += documents[idx_int] + "\n\n"
                relevant_text_ids.append(idx_int)
        
        return relevant_text, relevant_text_ids
        
    except Exception as e:
        print(f"Error in re_rank_cross_encoders: {str(e)}")
        # Return first document as fallback
        if documents:
            return documents[0], [0]
        return "", []

def call_llm(context: str, prompt: str, system_prompt: str) -> str:
    """Call the LLM with the given context and prompt."""
    try:
        # Ensure context is a string
        if isinstance(context, (list, tuple)):
            context = "\n".join(str(item) for item in context)
        elif not isinstance(context, str):
            context = str(context)

        # Create the full prompt with specific formatting instructions
        full_prompt = f"""{system_prompt}

Context: {context}

User: {prompt}

Assistant: Please provide a clear and concise response. Use only these formatting rules:
- Use **bold** for emphasis
- Use bullet points (-) for lists
- Use regular text for paragraphs
- Do not use numbered lists, code blocks, or tables
- Keep formatting simple and consistent

Response:"""
        
        # Call the LLM
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Context: {context}\n\nQuestion: {prompt}",
                },
            ],
            options={
                "num_gpu": 1,
                "num_thread": 4,
                "max_tokens": 1000
            }
        )
        
        # Debug print
        print("Response type:", type(response))
        print("Response message:", response.message)
        
        # Extract the content from the response
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            content = response.message.content
            
            # Clean up the response to ensure it's markdown-safe
            # Remove any complex markdown features
            content = content.replace('```', '')  # Remove code blocks
            content = content.replace('~~~', '')  # Remove alternative code blocks
            content = content.replace('|', '-')   # Replace tables with dashes
            content = content.replace('`', '')    # Remove inline code
            
            # Convert numbered lists to bullet points
            import re
            content = re.sub(r'^\d+\.\s+', '- ', content, flags=re.MULTILINE)
            
            # Ensure proper spacing for bullet points
            content = content.replace('\n-', '\n\n-')  # Add space before bullet points
            content = content.replace('\n*', '\n\n*')  # Add space before asterisk lists
            
            # Remove any remaining numbered lists
            content = re.sub(r'\n\d+\.\s+', '\n\n- ', content)
            
            # Ensure double newlines between paragraphs
            content = re.sub(r'\n\n+', '\n\n', content)
            
            return content.strip()
        else:
            print("Unexpected response format:", response)
            return "I apologize, but I encountered an error while processing your request. Please try again."
        
    except Exception as e:
        print(f"Error in call_llm: {str(e)}")
        raise Exception(f"Error generating response: {str(e)}") 