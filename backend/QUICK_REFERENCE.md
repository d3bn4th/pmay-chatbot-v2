# PMAY Chatbot Backend - Quick Reference

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start required services
ollama serve
redis-server

# Run the application
uvicorn api.main:app --reload
```

## 📁 Key Files & Their Purpose

| File | Purpose | Key Functions |
|------|---------|---------------|
| `api/main.py` | Main API endpoints | Chat, upload, feedback, config |
| `api/tts.py` | Text-to-speech API | Audio generation for English/Hindi |
| `core/config.py` | System configuration | Self-consistency, LLM, logging settings |
| `core/constants.py` | System prompts | Chatbot personality and behavior |
| `core/llm.py` | Language model integration | LLM calls, self-consistency, reranking |
| `core/vector_store.py` | Document storage | ChromaDB operations, query caching |
| `core/document_processor.py` | PDF processing | Text extraction, semantic chunking |
| `core/greeting_cache.py` | Response caching | Greeting patterns, TTL cache |
| `core/fallback_handler.py` | Error handling | Fallback responses, error types |
| `core/redis_cache.py` | FAQ caching | Redis-based FAQ storage |

## 🔄 Data Flow

### Chat Request
```
User Input → Cache Check → RAG Query → LLM → Response
     ↓
1. Check greeting/FAQ cache
2. Query vector store
3. Rerank documents
4. Generate response
5. Apply self-consistency (optional)
```

### Document Upload
```
PDF → Text Extraction → Chunking → Embeddings → ChromaDB
```

## 🗄️ Caching Layers

1. **Greeting Cache** (TTLCache, 24h)
   - Common conversational inputs
   - Pattern matching with regex

2. **Query Cache** (LRUCache, 128 entries)
   - Vector store query results
   - Reduces repeated searches

3. **TTS Cache** (TTLCache, 5min)
   - Audio file caching
   - Automatic cleanup

4. **Redis Cache**
   - FAQ responses
   - Persistent storage

## ⚙️ Configuration

### Self-Consistency Settings
```python
SELF_CONSISTENCY_CONFIG = {
    "enable_self_consistency": False,
    "num_candidates": 3,
    "similarity_threshold": 0.8,
    "min_cluster_size": 2,
}
```

### LLM Settings
```python
LLM_CONFIG = {
    "model": "llama3.2:3b",
    "max_tokens": 1000,
    "base_temperature": 0.4,
}
```

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Main chat interface |
| `/upload` | POST | Upload documents |
| `/upload` | GET | List documents |
| `/feedback` | POST | Submit feedback |
| `/tts/english` | POST | English TTS |
| `/tts/hindi` | POST | Hindi TTS |
| `/config/self-consistency` | GET/POST | Config management |
| `/cache/stats` | GET | Cache statistics |
| `/cache/clear` | DELETE | Clear caches |
| `/health` | GET | Health check |

## 🛠️ Error Handling

### Fallback Types
- `NO_DOCUMENTS`: No relevant docs found
- `NO_RELEVANT_TEXT`: Docs found but not relevant
- `RERANKING_FAILED`: Cross-encoder failed
- `LLM_ERROR`: Language model error
- `GENERAL_ERROR`: Unexpected error
- `AMBIGUOUS_QUESTION`: Unclear input

### Response Strategy
1. Identify error type
2. Select appropriate fallback
3. Generate helpful response
4. Suggest alternative topics

## 📊 Monitoring

### Health Checks
- Ollama service (port 11434)
- Redis service (port 6379)
- ChromaDB availability
- Model file existence

### Cache Statistics
- Hit rates
- Cache sizes
- TTL information
- Memory usage

## 🔧 Development

### Adding New Features
1. **Core Logic**: Add to `core/` modules
2. **API Endpoints**: Add to `api/main.py`
3. **Configuration**: Update `core/config.py`
4. **Testing**: Add to test files

### Common Patterns
```python
# Cache check
response = get_greeting_response(user_input)
if response:
    return response

# Vector store query
results = query_collection(prompt, n_results=5)

# LLM call
response = await call_llm(context, prompt, system_prompt)

# Fallback handling
fallback = FallbackHandler()
response = fallback.get_fallback_response(error_type)
```

## 🧪 Testing

```bash
# Run comprehensive tests
python test_enhanced_chatbot.py

# Test self-consistency
python test_self_consistency.py

# Demo self-consistency
python demo_self_consistency.py
```

## 📈 Performance Tips

1. **Caching**: Leverage multi-level caching
2. **Async**: Use async/await for I/O operations
3. **Batching**: Process multiple requests efficiently
4. **Cleanup**: Regular cache and file cleanup
5. **Monitoring**: Track response times and errors

## 🔍 Debugging

### Common Issues
1. **Ollama not running**: Check port 11434
2. **Redis connection**: Check port 6379
3. **Model files missing**: Check `models/` directory
4. **ChromaDB errors**: Check `demo-rag-chroma/` directory

### Logging
- Enable debug logs in `core/config.py`
- Check `feedback.log` for user feedback
- Monitor console output for errors

## 📚 Key Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `chromadb` | Vector database |
| `ollama` | LLM integration |
| `sentence-transformers` | Cross-encoder models |
| `torch` | Deep learning |
| `redis` | Caching |
| `pymupdf` | PDF processing |
| `cachetools` | In-memory caching |

## 🎯 Best Practices

1. **Error Handling**: Always use fallback mechanisms
2. **Caching**: Cache frequently accessed data
3. **Validation**: Validate all inputs
4. **Logging**: Log important events and errors
5. **Testing**: Test all components thoroughly
6. **Documentation**: Keep docs updated
7. **Security**: Validate and sanitize inputs
8. **Performance**: Monitor and optimize regularly 