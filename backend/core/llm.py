import torch
from pathlib import Path
import ollama
from ollama import AsyncClient, Message
from sentence_transformers import CrossEncoder
import numpy as np
from typing import List, Tuple
import asyncio
import re
from datetime import datetime

# Create models directory if it doesn't exist
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

def get_local_cross_encoder():
    """Get or download the cross-encoder model for reranking."""
    model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    model_path = MODELS_DIR / model_name.replace("/", "_")
    
    if not model_path.exists():
        model = CrossEncoder(model_name, device="cuda" if torch.cuda.is_available() else "cpu", activation_fn=torch.nn.Sigmoid())
        model.save(str(model_path))
    else:
        model = CrossEncoder(str(model_path), device="cuda" if torch.cuda.is_available() else "cpu", activation_fn=torch.nn.Sigmoid())
    
    return model

def re_rank_cross_encoders(documents: List[str], prompt: str) -> Tuple[str, List[int], List[float]]:
    """Rerank documents using cross-encoder model."""
    if not documents:
        return "", [], []
        
    try:
        # Ensure documents is a list of strings
        documents = [str(doc) for doc in documents if doc]
        if not documents:
            return "", [], []
            
        relevant_text = ""
        relevant_text_ids = []
        relevant_scores = []
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
            if 0 <= idx_int < len(documents):
                relevant_text += documents[idx_int] + "\n\n"
                relevant_text_ids.append(idx_int)
                relevant_scores.append(float(scores[idx_int]))
        
        return relevant_text, relevant_text_ids, relevant_scores
        
    except Exception as e:
        print(f"Error in re_rank_cross_encoders: {str(e)}")
        # Return first document as fallback with a dummy score
        if documents:
            return documents[0], [0], [0.5]
        return "", [], []

def postprocess_markdown_response(text: str, max_length: int = 1200) -> str:
    """
    Post-process LLM output to:
    - Remove future dates (e.g., 'June 2025', 'January 2026')
    - Ensure valid Markdown (basic cleanup)
    - Truncate if too long
    """
    # Remove future dates (years > current year)
    current_year = datetime.now().year
    text = re.sub(r"(January|February|March|April|May|June|July|August|September|October|November|December) [12][0-9]{3,}",
                 lambda m: m.group(0) if int(m.group(0).split()[-1]) <= current_year else "", text)
    # Remove any year > current year
    text = re.sub(r"\b(20[3-9][0-9]|21[0-9]{2,})\b", "", text)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text

async def call_llm(context: str, prompt: str, system_prompt: str):
    """Call the LLM with the given context and prompt. This function is an async generator."""
    try:
        # Ensure context is a string
        if isinstance(context, (list, tuple)):
            context = "\n".join(str(item) for item in context)
        elif not isinstance(context, str):
            context = str(context)

        # Add ambiguity instruction to the system prompt
        system_prompt_with_ambiguity = system_prompt + "\n\nIf the user's question is ambiguous or unclear, respond with: 'Your question is too ambiguous. Please provide more details.' Do not attempt to answer ambiguous questions."

        # Create the full prompt with specific formatting instructions
        full_prompt = f"""{system_prompt_with_ambiguity}

Context: {context}

User: {prompt}

Assistant: Please provide a clear and concise response. Use only these formatting rules:
- Use **bold** for emphasis
- Use bullet points (-) for lists
- Use regular text for paragraphs
- Do not use numbered lists, code blocks, or tables
- Keep formatting simple and consistent

Response:"""
        
        # print("DEBUG: Before AsyncClient.chat call")
        # Call the LLM with streaming enabled using AsyncClient
        client = AsyncClient()
        response_stream = await client.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt_with_ambiguity,
                },
                {
                    "role": "user",
                    "content": f"Context: {context}\n\nQuestion: {prompt}",
                },
            ],
            stream=True,
            options={
                "num_gpu": 1,
                "num_thread": 4,
                "max_tokens": 1000,
            }
        )
        # print("DEBUG: After AsyncClient.chat call, before iterating chunks")
        
        # Iterate over the streamed chunks from the AsyncClient
        i = 0
        async for chunk_data in response_stream:
            if 'message' in chunk_data and 'content' in chunk_data['message']:
                content_to_yield = chunk_data['message']['content']
                if content_to_yield:
                    # Post-process the chunk for Markdown and accuracy
                    content_to_yield = postprocess_markdown_response(content_to_yield)
                    yield content_to_yield  # Yield the cleaned content chunk directly
            else:
                print(f"DEBUG LLM: Chunk {i} has no message or content in its dictionary: {chunk_data}")
            i += 1
        print("DEBUG: Finished yielding chunks")
        
    except Exception as e:
        print(f"Error in call_llm: {str(e)}")
        # In a streaming scenario, yield an error message to the frontend
        yield f"I apologize, but I encountered an error while processing your request: {str(e)}"