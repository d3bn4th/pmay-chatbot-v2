from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import asyncio
import uuid
from core.vector_store import query_collection, add_to_vector_collection
from core.document_processor import process_document
from core.llm import re_rank_cross_encoders, call_llm
from core.constants import SYSTEM_PROMPT, GREETING_RESPONSES

app = FastAPI(title="PMAY Chatbot API")

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

        async def generate_response_stream():
            try:
                # Removed initial 'Stream started.' message
                # yield f"data: {json.dumps({'type': 'text', 'content': 'Stream started.'})}\n\n"
                # print("DEBUG: Initial 'Stream started.' message yielded.")

                user_input_lower = chat_request.message.lower()
                if user_input_lower in GREETING_RESPONSES:
                    # Send greeting in SSE format with type 'text'
                    yield f"data: {json.dumps({'type': 'text', 'content': GREETING_RESPONSES[user_input_lower]})}\n\n"
                    print(f"Yielding greeting: {GREETING_RESPONSES[user_input_lower]}")
                    return

                # Get documents from vector store
                results = query_collection(chat_request.message)
                documents = results.get("documents", [])
                metadata = results.get("metadatas", []) # Assuming metadata is returned with documents

                print(f"Retrieved {len(documents)} documents from vector store")
                print("First document sample:", documents[0][:100] if documents else "No documents")
                
                if not documents:
                    no_info_response = "I apologize, but I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or ask about a different aspect of PMAY?"
                    # Send no info response in SSE format with type 'text'
                    yield f"data: {json.dumps({'type': 'text', 'content': no_info_response})}\n\n"
                    print(f"Yielding no info: {no_info_response}")
                    return

                # Get reranked documents, their indices, and scores
                try:
                    relevant_text, relevant_text_ids, relevant_scores = re_rank_cross_encoders(documents, chat_request.message)
                    print(f"Reranked documents. Got {len(relevant_text_ids)} relevant documents")
                    print("Relevant text sample:", relevant_text[:100] if relevant_text else "No relevant text")
                except Exception as e:
                    print(f"Error in reranking: {str(e)}")
                    # Fallback to first document if reranking fails
                    relevant_text = documents[0]
                    relevant_text_ids = [0]
                    relevant_scores = [0.5] # Assign a default score for fallback
                
                if not relevant_text:
                    no_info_response = "I apologize, but I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or ask about a different aspect of PMAY?"
                    # Send no relevant text response in SSE format with type 'text'
                    yield f"data: {json.dumps({'type': 'text', 'content': no_info_response})}\n\n"
                    print(f"Yielding no relevant text: {no_info_response}")
                    return

                # Stream the LLM response
                async for chunk in call_llm(relevant_text, chat_request.message, SYSTEM_PROMPT):
                    # print(f"DEBUG: Processing chunk from LLM: {chunk[:50]}...") # Log first 50 chars of chunk
                    # Send each chunk in SSE format with type 'text'
                    sse_message = f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                    yield sse_message
                    # print("DEBUG: Yielded SSE text chunk")
                    await asyncio.sleep(0) # Force FastAPI to flush the chunk
                
                # After streaming is complete, send the sources
                # print("DEBUG: LLM streaming complete. Preparing sources.")
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
                # print("DEBUG: Yielded SSE sources chunk")
                await asyncio.sleep(0) # Force FastAPI to flush the sources chunk
                
            except Exception as e:
                print(f"Error in generate_response_stream: {str(e)}")
                error_message = f"I apologize, but I encountered an error while processing your request: {str(e)}"
                yield f"data: {json.dumps({'type': 'text', 'content': error_message})}\n\n"

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 