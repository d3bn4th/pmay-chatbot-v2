import torch
from pathlib import Path
import ollama
from ollama import AsyncClient, Message
from sentence_transformers import CrossEncoder
import numpy as np
from typing import List, Tuple, Dict, Any
import asyncio
import re
from datetime import datetime
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from .config import SELF_CONSISTENCY_CONFIG, LLM_CONFIG, TEXT_CONFIG, LOGGING_CONFIG

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

def calculate_text_similarity(texts: List[str]) -> np.ndarray:
    """
    Calculate cosine similarity between texts using TF-IDF vectors.
    
    Args:
        texts: List of text strings to compare
        
    Returns:
        Similarity matrix as numpy array
    """
    if len(texts) < 2:
        return np.array([[1.0]])
    
    try:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=TEXT_CONFIG["similarity_ngram_range"],
            max_features=TEXT_CONFIG["similarity_max_features"]
        )
        
        # Handle empty or very short texts
        processed_texts = []
        for text in texts:
            if not text or len(text.strip()) < 10:
                processed_texts.append("placeholder text for similarity calculation")
            else:
                processed_texts.append(text)
        
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix
        
    except Exception as e:
        print(f"Error calculating text similarity: {str(e)}")
        # Return identity matrix as fallback
        return np.eye(len(texts))

def cluster_similar_responses(responses: List[str], similarity_threshold: float = None) -> List[List[int]]:
    """
    Cluster responses based on text similarity.
    
    Args:
        responses: List of response strings
        similarity_threshold: Threshold for considering responses similar
        
    Returns:
        List of clusters, where each cluster is a list of response indices
    """
    if similarity_threshold is None:
        similarity_threshold = SELF_CONSISTENCY_CONFIG["similarity_threshold"]
        
    if len(responses) <= 1:
        return [[0]] if responses else []
    
    # Calculate similarity matrix
    similarity_matrix = calculate_text_similarity(responses)
    
    # Find clusters using similarity threshold
    clusters = []
    used_indices = set()
    
    for i in range(len(responses)):
        if i in used_indices:
            continue
            
        # Start a new cluster
        cluster = [i]
        used_indices.add(i)
        
        # Find similar responses
        for j in range(i + 1, len(responses)):
            if j not in used_indices and similarity_matrix[i][j] >= similarity_threshold:
                cluster.append(j)
                used_indices.add(j)
        
        clusters.append(cluster)
    
    return clusters

def select_majority_response(responses: List[str], clusters: List[List[int]]) -> Tuple[str, Dict[str, Any]]:
    """
    Select the majority response from clustered responses.
    
    Args:
        responses: List of all candidate responses
        clusters: List of clusters (each cluster is a list of response indices)
        
    Returns:
        Tuple of (selected_response, metadata)
    """
    if not responses:
        return "", {"method": "no_responses", "clusters": [], "cluster_sizes": []}
    
    if len(responses) == 1:
        return responses[0], {"method": "single_response", "clusters": clusters, "cluster_sizes": [1]}
    
    # Find the largest cluster
    cluster_sizes = [len(cluster) for cluster in clusters]
    largest_cluster_idx = cluster_sizes.index(max(cluster_sizes))
    largest_cluster = clusters[largest_cluster_idx]
    
    # If largest cluster has only one response, return it
    if len(largest_cluster) == 1:
        selected_response = responses[largest_cluster[0]]
        metadata = {
            "method": "single_largest_cluster",
            "clusters": clusters,
            "cluster_sizes": cluster_sizes,
            "selected_cluster_size": 1
        }
        return selected_response, metadata
    
    # For larger clusters, select the response with the highest average similarity to others
    cluster_responses = [responses[i] for i in largest_cluster]
    similarity_matrix = calculate_text_similarity(cluster_responses)
    
    # Calculate average similarity for each response in the cluster
    avg_similarities = []
    for i in range(len(cluster_responses)):
        similarities = [similarity_matrix[i][j] for j in range(len(cluster_responses)) if i != j]
        avg_similarity = np.mean(similarities) if similarities else 0.0
        avg_similarities.append(avg_similarity)
    
    # Select response with highest average similarity
    best_idx = avg_similarities.index(max(avg_similarities))
    selected_response = cluster_responses[best_idx]
    
    metadata = {
        "method": "majority_cluster_highest_similarity",
        "clusters": clusters,
        "cluster_sizes": cluster_sizes,
        "selected_cluster_size": len(largest_cluster),
        "cluster_avg_similarities": avg_similarities
    }
    
    return selected_response, metadata

async def generate_candidate_responses(context: str, prompt: str, system_prompt: str, num_candidates: int = 5) -> List[str]:
    """
    Generate multiple candidate responses for self-consistency prompting.
    
    Args:
        context: Context information for the LLM
        prompt: User's question
        system_prompt: System prompt for the LLM
        num_candidates: Number of candidate responses to generate
        
    Returns:
        List of candidate response strings
    """
    candidates = []
    
    # Add slight variations to the prompt to encourage diversity
    if SELF_CONSISTENCY_CONFIG["prompt_variations"]:
        prompt_variations = [
            prompt,
            f"Please answer: {prompt}",
            f"Question: {prompt}",
            f"Can you help me with: {prompt}",
            f"I need information about: {prompt}"
        ]
    else:
        prompt_variations = [prompt]
    
    for i in range(num_candidates):
        try:
            # Use different prompt variations to encourage diverse responses
            current_prompt = prompt_variations[i % len(prompt_variations)]
            
            # Add temperature variation to the system prompt
            if SELF_CONSISTENCY_CONFIG["temperature_variation"]:
                temperature_variation = LLM_CONFIG["base_temperature"] + (i * LLM_CONFIG["temperature_range"] / num_candidates)
                current_system_prompt = f"{system_prompt}\n\nPlease provide a response with creativity level {i+1}."
            else:
                temperature_variation = LLM_CONFIG["base_temperature"]
                current_system_prompt = system_prompt
            
            # Generate response without streaming
            client = AsyncClient()
            response = await client.chat(
                model="llama3.2:1b",
                messages=[
                    {
                        "role": "system",
                        "content": current_system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Context: {context}\n\nQuestion: {current_prompt}",
                    },
                ],
                stream=False,
                options={
                    "num_gpu": LLM_CONFIG["num_gpu"],
                    "num_thread": LLM_CONFIG["num_thread"],
                    "max_tokens": LLM_CONFIG["max_tokens"],
                    "temperature": temperature_variation,
                }
            )
            
            if response and 'message' in response and 'content' in response['message']:
                candidate = response['message']['content'].strip()
                if candidate:
                    candidates.append(candidate)
                    
        except Exception as e:
            print(f"Error generating candidate {i+1}: {str(e)}")
            continue
    
    return candidates

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

async def call_llm_with_self_consistency(context: str, prompt: str, system_prompt: str):
    """
    Call the LLM with self-consistency prompting.
    This function generates multiple candidate responses and selects the best one.
    """
    if not SELF_CONSISTENCY_CONFIG["enable_self_consistency"]:
        # Fall back to original single response method
        async for chunk in call_llm(context, prompt, system_prompt):
            yield chunk
        return
    
    try:
        # Generate multiple candidate responses
        if LOGGING_CONFIG["enable_debug_logs"]:
            print(f"Generating {SELF_CONSISTENCY_CONFIG['num_candidates']} candidate responses...")
        candidates = await generate_candidate_responses(
            context, 
            prompt, 
            system_prompt, 
            SELF_CONSISTENCY_CONFIG['num_candidates']
        )
        
        if not candidates:
            # Fall back to original method if no candidates generated
            async for chunk in call_llm(context, prompt, system_prompt):
                yield chunk
            return
        
        if LOGGING_CONFIG["enable_debug_logs"]:
            print(f"Generated {len(candidates)} candidate responses")
        
        # Cluster similar responses
        clusters = cluster_similar_responses(candidates)
        
        if LOGGING_CONFIG["log_clustering_info"]:
            print(f"Found {len(clusters)} clusters: {[len(c) for c in clusters]}")
        
        # Select the majority response
        selected_response, metadata = select_majority_response(candidates, clusters)
        
        if LOGGING_CONFIG["log_selection_metadata"]:
            print(f"Selected response using method: {metadata['method']}")
        
        # Post-process the selected response
        processed_response = postprocess_markdown_response(selected_response, TEXT_CONFIG["max_response_length"])
        
        # Stream the response in chunks to maintain compatibility
        chunk_size = TEXT_CONFIG["chunk_size"]
        for i in range(0, len(processed_response), chunk_size):
            chunk = processed_response[i:i + chunk_size]
            if chunk:
                yield chunk
                await asyncio.sleep(0.01)  # Small delay to simulate streaming
        
    except Exception as e:
        print(f"Error in self-consistency prompting: {str(e)}")
        # Fall back to original method
        async for chunk in call_llm(context, prompt, system_prompt):
            yield chunk

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