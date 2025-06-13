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
            parsed_json = await request.json()
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

        async def generate_response():
            try:
                user_input_lower = chat_request.message.lower()
                if user_input_lower in GREETING_RESPONSES:
                    response_content = GREETING_RESPONSES[user_input_lower]
                    yield f"{response_content}\n"
                    print(f"Yielding: {response_content}\n")
                    return

                # Get documents from vector store
                results = query_collection(chat_request.message)
                documents = results.get("documents", [])
                
                print(f"Retrieved {len(documents)} documents from vector store")
                print("First document sample:", documents[0][:100] if documents else "No documents")
                
                if not documents:
                    no_info_response = "I apologize, but I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or ask about a different aspect of PMAY?"
                    yield f"{no_info_response}\n"
                    print(f"Yielding: {no_info_response}\n")
                    return

                # Get reranked documents and their indices
                try:
                    relevant_text, relevant_text_ids = re_rank_cross_encoders(documents, chat_request.message)
                    print(f"Reranked documents. Got {len(relevant_text_ids)} relevant documents")
                    print("Relevant text sample:", relevant_text[:100] if relevant_text else "No relevant text")
                except Exception as e:
                    print(f"Error in reranking: {str(e)}")
                    # Fallback to first document if reranking fails
                    relevant_text = documents[0]
                    relevant_text_ids = [0]
                
                if not relevant_text:
                    no_info_response = "I apologize, but I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or ask about a different aspect of PMAY?"
                    yield f"{no_info_response}\n"
                    print(f"Yielding: {no_info_response}\n")
                    return

                # Generate response using the LLM
                try:
                    full_response = call_llm(
                        context=relevant_text,
                        prompt=chat_request.message,
                        system_prompt=SYSTEM_PROMPT
                    )
                    
                    # Append sources to the full response
                    if relevant_text_ids:
                        full_response += "\n\n**Sources:**\n"
                        for doc_id in relevant_text_ids:
                            if isinstance(doc_id, int) and doc_id < len(documents):
                                source_title = documents[doc_id][:100] + "..." if len(documents[doc_id]) > 100 else documents[doc_id]
                                full_response += f"- [{source_title}](#{doc_id})\n"
                    
                    yield f"{full_response}\n"
                    print(f"Yielding: {full_response}\n")
                except Exception as e:
                    print(f"Error in LLM call: {str(e)}")
                    error_message = "I apologize, but I encountered an error while processing your request. Please try again."
                    yield f"{error_message}\n"
                    print(f"Yielding: {error_message}\n")

            except Exception as e:
                print(f"Error in chat endpoint (generate_response): {str(e)}")
                error_message = f"Error: {str(e)}"
                yield f"{error_message}\n"
                print(f"Yielding: {error_message}\n")

        return StreamingResponse(generate_response(), media_type="text/event-stream")
    except Exception as e:
        print(f"Unhandled error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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