from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import asyncio
import uuid
import os
from datetime import datetime
from core.vector_store import query_collection, add_to_vector_collection, list_uploaded_documents
from core.document_processor import process_document
from core.llm import re_rank_cross_encoders, call_llm, call_llm_with_self_consistency
from core.constants import SYSTEM_PROMPT
from core.config import update_self_consistency_config, get_self_consistency_config, validate_config
from core.greeting_cache import get_greeting_response, get_cache_stats, clear_cache
from core.fallback_handler import fallback_handler, FallbackType
from werkzeug.utils import secure_filename

app = FastAPI(title="PMAY Chatbot API")

# Serve the docs directory as static files at /docs
import os
DOCS_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs')
app.mount("/docs", StaticFiles(directory=DOCS_PATH), name="docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[dict]] = None

class DocumentUploadResponse(BaseModel):
    message: str
    chunks_added: int

class FeedbackRequest(BaseModel):
    message_id: str
    feedback: str  # 'up' or 'down'
    content: str

class SelfConsistencyConfigRequest(BaseModel):
    enable_self_consistency: Optional[bool] = None
    num_candidates: Optional[int] = None
    similarity_threshold: Optional[float] = None
    min_cluster_size: Optional[int] = None
    temperature_variation: Optional[bool] = None
    prompt_variations: Optional[bool] = None

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.body()
        print("Raw request body:", body)
        try:
            parsed_json = json.loads(body)
            print("Parsed JSON:", parsed_json)
        except Exception as e:
            print("JSON parse error:", e)
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Validate against ChatRequest model after raw logging
        try:
            chat_request = ChatRequest(**parsed_json)
        except Exception as e:
            print(f"ChatRequest validation error: {e}")
            raise HTTPException(status_code=422, detail=f"Validation Error: {e}")

        # Get model from request if present
        model = parsed_json.get("model")

        async def generate_response_stream():
            try:
                user_input_lower = chat_request.message.lower()
                
                # Check for greeting responses first (efficient caching)
                greeting_response = get_greeting_response(chat_request.message)
                if greeting_response:
                    print(f"Using cached greeting response for: {chat_request.message}")
                    # Send greeting response in SSE format with type 'text'
                    yield f"data: {json.dumps({'type': 'text', 'content': greeting_response})}\n\n"
                    return
                
                # Check for ambiguous questions
                if fallback_handler.is_ambiguous_question(chat_request.message):
                    print(f"Detected ambiguous question: {chat_request.message}")
                    ambiguous_response = fallback_handler.get_fallback_response(FallbackType.AMBIGUOUS_QUESTION, chat_request.message)
                    yield f"data: {json.dumps({'type': 'text', 'content': ambiguous_response})}\n\n"
                    return
                
                # Get documents from vector store
                results = query_collection(chat_request.message)
                documents = results.get("documents", [])
                metadata = results.get("metadatas", []) # Assuming metadata is returned with documents

                print(f"Retrieved {len(documents)} documents from vector store")
                print("First document sample:", documents[0][:100] if documents else "No documents")
                
                # Check if we should use fallback due to no documents
                if not documents:
                    print(f"No documents found for query: {chat_request.message}")
                    fallback_response = fallback_handler.get_enhanced_fallback_response(
                        FallbackType.NO_DOCUMENTS, 
                        chat_request.message, 
                        documents_found=0
                    )
                    yield f"data: {json.dumps({'type': 'text', 'content': fallback_response})}\n\n"
                    return

                # Get reranked documents, their indices, and scores
                reranking_success = True
                try:
                    relevant_text, relevant_text_ids, relevant_scores = re_rank_cross_encoders(documents, chat_request.message)
                    print(f"Reranked documents. Got {len(relevant_text_ids)} relevant documents")
                    print("Relevant text sample:", relevant_text[:100] if relevant_text else "No relevant text")
                except Exception as e:
                    print(f"Error in reranking: {str(e)}")
                    reranking_success = False
                    # Fallback to first document if reranking fails
                    relevant_text = documents[0]
                    relevant_text_ids = [0]
                    relevant_scores = [0.5] # Assign a default score for fallback
                
                # Check if we should use fallback due to no relevant text
                if not relevant_text:
                    print(f"No relevant text found after reranking for query: {chat_request.message}")
                    fallback_response = fallback_handler.get_enhanced_fallback_response(
                        FallbackType.NO_RELEVANT_TEXT, 
                        chat_request.message, 
                        documents_found=len(documents)
                    )
                    yield f"data: {json.dumps({'type': 'text', 'content': fallback_response})}\n\n"
                    return

                # Stream the LLM response with self-consistency prompting
                llm_success = True
                try:
                    async for chunk in call_llm_with_self_consistency(relevant_text, chat_request.message, SYSTEM_PROMPT, model=model):
                        # Send each chunk in SSE format with type 'text'
                        sse_message = f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                        yield sse_message
                        await asyncio.sleep(0) # Force FastAPI to flush the chunk
                except Exception as e:
                    print(f"Error in LLM streaming: {str(e)}")
                    llm_success = False
                    # Use fallback response for LLM errors
                    fallback_response = fallback_handler.get_fallback_response(FallbackType.LLM_ERROR, chat_request.message)
                    yield f"data: {json.dumps({'type': 'text', 'content': fallback_response})}\n\n"
                    return
                
                # After streaming is complete, send the sources
                sources = []
                for idx, score in zip(relevant_text_ids, relevant_scores):
                    if idx < len(metadata):
                        sources.append({
                            "text": documents[idx][:200] + "...",  # Truncate long texts
                            "score": float(score),
                            "metadata": metadata[idx] if metadata else {}
                        })
                
                sse_sources_message = f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
                yield sse_sources_message
                await asyncio.sleep(0) # Force FastAPI to flush the sources chunk
                
            except Exception as e:
                print(f"Error in generate_response_stream: {str(e)}")
                # Use enhanced fallback for general errors
                fallback_response = fallback_handler.get_enhanced_fallback_response(
                    FallbackType.GENERAL_ERROR, 
                    chat_request.message, 
                    error_details=str(e)
                )
                yield f"data: {json.dumps({'type': 'text', 'content': fallback_response})}\n\n"

        return StreamingResponse(
            generate_response_stream(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        # Save the uploaded file to the docs/ directory
        docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        safe_filename = secure_filename(file.filename)
        file_path = os.path.join(docs_dir, safe_filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        # Now process the document as before
        splits = process_document(content, file.filename)
        if not splits:
            raise HTTPException(status_code=400, detail="Invalid or empty document")
        chunks_added = add_to_vector_collection(splits, file.filename)
        return DocumentUploadResponse(
            message=f"Successfully processed {file.filename}",
            chunks_added=chunks_added
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/upload")
async def get_uploaded_documents():
    try:
        documents = list_uploaded_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(feedback: FeedbackRequest):
    try:
        log_entry = {
            "message_id": feedback.message_id,
            "feedback": feedback.feedback,
            "content": feedback.content
        }
        log_line = json.dumps(log_entry) + "\n"
        log_path = os.path.join(os.path.dirname(__file__), "..", "feedback.log")
        with open(log_path, "a") as f:
            f.write(log_line)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/config/self-consistency")
async def get_self_consistency_config_endpoint():
    """Get current self-consistency configuration."""
    try:
        config = get_self_consistency_config()
        is_valid, error_message = validate_config()
        return {
            "config": config,
            "is_valid": is_valid,
            "error_message": error_message if not is_valid else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/self-consistency")
async def update_self_consistency_config_endpoint(request: SelfConsistencyConfigRequest):
    """Update self-consistency configuration."""
    try:
        # Extract non-None values from request
        config_updates = {}
        for field, value in request.dict().items():
            if value is not None:
                config_updates[field] = value
        
        if not config_updates:
            raise HTTPException(status_code=400, detail="No configuration updates provided")
        
        # Update configuration
        update_self_consistency_config(**config_updates)
        
        # Validate updated configuration
        is_valid, error_message = validate_config()
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid configuration: {error_message}")
        
        # Return updated configuration
        config = get_self_consistency_config()
        return {
            "message": "Configuration updated successfully",
            "config": config,
            "is_valid": is_valid
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/stats")
async def get_cache_stats_endpoint():
    """Get greeting cache statistics."""
    try:
        stats = get_cache_stats()
        return {
            "cache_type": "greeting_cache",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cache/clear")
async def clear_cache_endpoint():
    """Clear the greeting cache."""
    try:
        clear_cache()
        return {
            "message": "Greeting cache cleared successfully",
            "cache_type": "greeting_cache"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if core components are working
        cache_stats = get_cache_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "greeting_cache": "operational",
                "fallback_handler": "operational"
            },
            "cache_stats": cache_stats
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 