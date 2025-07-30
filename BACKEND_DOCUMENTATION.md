# PMAY Chatbot Backend - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Layer](#api-layer)
5. [Data Flow](#data-flow)
6. [Configuration](#configuration)
7. [Caching Strategy](#caching-strategy)
8. [Error Handling](#error-handling)
9. [Text-to-Speech](#text-to-speech)
10. [Testing](#testing)
11. [Deployment](#deployment)

## Overview

The PMAY (Pradhan Mantri Awas Yojana) Chatbot Backend is a sophisticated AI-powered system designed to assist users with housing scheme information. It combines Retrieval-Augmented Generation (RAG), advanced caching mechanisms, and robust error handling to provide accurate and helpful responses about the PMAY-U scheme.

### Key Features
- **RAG-based Q&A**: Retrieves relevant documents and generates contextual responses
- **Multi-level Caching**: Reduces latency for common queries and greetings
- **Self-consistency**: Ensures response quality through multiple candidate generation
- **Fallback Mechanisms**: Graceful handling of edge cases and errors
- **Text-to-Speech**: Audio output support for accessibility
- **Document Upload**: Dynamic knowledge base expansion
- **Multi-language Support**: English and Hindi capabilities

## Architecture

```
backend/
├── api/                    # FastAPI application layer
│   ├── main.py            # Main API endpoints
│   └── tts.py             # Text-to-speech endpoints
├── core/                   # Core business logic
│   ├── config.py          # Configuration management
│   ├── constants.py       # System prompts and constants
│   ├── document_processor.py # Document processing and chunking
│   ├── fallback_handler.py # Error handling and fallback responses
│   ├── greeting_cache.py  # Greeting response caching
│   ├── llm.py            # LLM integration and self-consistency
│   ├── redis_cache.py    # FAQ caching with Redis
│   └── vector_store.py   # Vector database operations
├── docs/                  # PMAY documents (knowledge base)
├── models/               # AI models (TTS, embeddings)
├── scripts/              # Utility scripts
├── utils/                # Helper utilities
└── requirements.txt      # Python dependencies
```

## Core Components

### 1. Configuration Management (`core/config.py`)

**Purpose**: Centralized configuration for all system parameters.

**Key Configurations**:
- **Self-consistency**: Controls response quality through multiple candidate generation
- **LLM Settings**: Model selection, temperature, token limits
- **Text Processing**: Response length limits, chunk sizes
- **Logging**: Debug and monitoring settings

**Example Configuration**:
```python
SELF_CONSISTENCY_CONFIG = {
    "enable_self_consistency": False,
    "num_candidates": 3,
    "similarity_threshold": 0.8,
    "min_cluster_size": 2,
    "temperature_variation": True,
    "prompt_variations": True,
    "max_response_time": 30,
}
```

### 2. System Constants (`core/constants.py`)

**Purpose**: Defines the chatbot's personality and behavior guidelines.

**Key Features**:
- Official MoHUA chatbot identity
- Response formatting guidelines
- Tone and style specifications
- Follow-up question generation

### 3. Document Processing (`core/document_processor.py`)

**Purpose**: Processes uploaded PDF documents into searchable chunks.

**Features**:
- **PDF Processing**: Uses PyMuPDF for text extraction
- **Semantic Chunking**: Intelligent document splitting based on meaning
- **Character-based Fallback**: Traditional chunking when semantic fails
- **Metadata Preservation**: Maintains document source information

**Chunking Methods**:
1. **Semantic Chunking**: Uses embeddings to split by meaning
2. **Character-based**: Fixed-size chunks with overlap

### 4. Vector Store (`core/vector_store.py`)

**Purpose**: Manages document storage and retrieval using ChromaDB.

**Features**:
- **Persistent Storage**: ChromaDB with cosine similarity
- **Embedding Integration**: Ollama-based embeddings
- **Query Caching**: LRU cache for frequent queries
- **Metadata Filtering**: Document source tracking

**Key Functions**:
- `query_collection()`: Retrieves relevant documents
- `add_to_vector_collection()`: Adds new documents
- `list_uploaded_documents()`: Lists available documents

### 5. LLM Integration (`core/llm.py`)

**Purpose**: Handles language model interactions and response generation.

**Features**:
- **Multiple Models**: Support for different LLM providers
- **Cross-encoder Reranking**: Improves document relevance
- **Self-consistency**: Multiple candidate generation and clustering
- **Response Post-processing**: Markdown formatting and length limits

**Key Functions**:
- `call_llm()`: Standard LLM interaction
- `call_llm_with_self_consistency()`: Enhanced response generation
- `re_rank_cross_encoders()`: Document relevance improvement
- `cluster_similar_responses()`: Response clustering for consistency

### 6. Greeting Cache (`core/greeting_cache.py`)

**Purpose**: Optimizes response time for common conversational inputs.

**Features**:
- **TTL Cache**: 24-hour expiration for freshness
- **Pattern Matching**: Regex-based greeting detection
- **Smart Normalization**: Consistent input processing
- **Time-aware Responses**: Personalized greetings based on time

**Supported Patterns**:
- Simple greetings: "hi", "hello", "hey"
- Time-based: "good morning", "good afternoon"
- Indian greetings: "namaste", "namaskar"
- Capability questions: "what can you do"
- Identity questions: "who are you"

### 7. Redis Cache (`core/redis_cache.py`)

**Purpose**: Provides fast access to frequently asked questions.

**Features**:
- **FAQ Storage**: Pre-populated common questions
- **Fast Retrieval**: Redis-based caching
- **Scalable**: Easy to add new FAQs

### 8. Fallback Handler (`core/fallback_handler.py`)

**Purpose**: Ensures helpful responses when the main system fails.

**Fallback Types**:
- `NO_DOCUMENTS`: No relevant documents found
- `NO_RELEVANT_TEXT`: Documents found but not relevant
- `RERANKING_FAILED`: Document reranking failed
- `LLM_ERROR`: Language model errors
- `GENERAL_ERROR`: Unexpected errors
- `AMBIGUOUS_QUESTION`: Unclear user input

**Features**:
- **Contextual Responses**: Tailored to error type
- **Helpful Suggestions**: Guides users to better questions
- **Graceful Degradation**: Maintains user experience

## API Layer

### Main API (`api/main.py`)

**Purpose**: FastAPI application with all chat endpoints.

**Key Endpoints**:

#### 1. Chat Endpoint (`POST /chat`)
- **Purpose**: Main conversation interface
- **Features**: Streaming responses, model selection, caching
- **Flow**: Input → Cache Check → RAG → LLM → Response

#### 2. Document Upload (`POST /upload`)
- **Purpose**: Add new documents to knowledge base
- **Features**: PDF processing, chunking, vector storage
- **Response**: Number of chunks added

#### 3. Document List (`GET /upload`)
- **Purpose**: List available documents
- **Response**: Array of document sources

#### 4. Feedback (`POST /feedback`)
- **Purpose**: Collect user feedback
- **Features**: Message tracking, feedback storage

#### 5. Configuration Management
- `GET /config/self-consistency`: Get current settings
- `POST /config/self-consistency`: Update settings

#### 6. Cache Management
- `GET /cache/stats`: Cache statistics
- `DELETE /cache/clear`: Clear caches

#### 7. Health Check (`GET /health`)
- **Purpose**: System health monitoring
- **Response**: Status and component health

### Text-to-Speech API (`api/tts.py`)

**Purpose**: Converts text responses to audio.

**Features**:
- **Multi-language**: English and Hindi support
- **Caching**: TTL-based audio file caching
- **Cleanup**: Automatic file deletion
- **Thread Safety**: Lock-based cache management

**Endpoints**:
- `POST /tts/english`: English TTS
- `POST /tts/hindi`: Hindi TTS

## Data Flow

### 1. Chat Request Processing

```
User Input → API → Cache Check → RAG → LLM → Response
    ↓
1. Check greeting cache
2. Check FAQ cache
3. Query vector store
4. Rerank documents
5. Generate response
6. Apply self-consistency (if enabled)
7. Post-process and return
```

### 2. Document Upload Flow

```
PDF Upload → Processing → Chunking → Vector Storage → Success
    ↓
1. Extract text from PDF
2. Apply semantic/character chunking
3. Generate embeddings
4. Store in ChromaDB
5. Return chunk count
```

### 3. Error Handling Flow

```
Error Detection → Fallback Selection → Response Generation → User Feedback
    ↓
1. Identify error type
2. Select appropriate fallback
3. Generate helpful response
4. Suggest alternative topics
```

## Configuration

### Environment Setup

**Required Services**:
- **Ollama**: Local LLM server (port 11434)
- **Redis**: Caching server (port 6379)
- **ChromaDB**: Vector database (local)

**Python Dependencies**:
```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `fastapi`: Web framework
- `chromadb`: Vector database
- `ollama`: LLM integration
- `sentence-transformers`: Cross-encoder models
- `torch`: Deep learning framework
- `redis`: Caching
- `pymupdf`: PDF processing

### Configuration Files

1. **`core/config.py`**: System-wide settings
2. **`core/constants.py`**: System prompts
3. **Model Paths**: TTS and embedding models

## Caching Strategy

### Multi-Level Caching

1. **Greeting Cache** (TTLCache)
   - Purpose: Common conversational inputs
   - TTL: 24 hours
   - Size: 100 entries

2. **Query Cache** (LRUCache)
   - Purpose: Vector store queries
   - Size: 128 entries
   - Key: Query + parameters

3. **TTS Cache** (TTLCache)
   - Purpose: Audio file caching
   - TTL: 5 minutes
   - Automatic cleanup

4. **Redis Cache**
   - Purpose: FAQ responses
   - Persistent storage
   - Fast retrieval

### Cache Management

- **Automatic Cleanup**: TTL-based expiration
- **Manual Clear**: API endpoints for cache management
- **Statistics**: Cache hit rates and sizes
- **Thread Safety**: Lock-based operations

## Error Handling

### Fallback Mechanisms

1. **Document-Level**: When no relevant documents found
2. **Reranking-Level**: When cross-encoder fails
3. **LLM-Level**: When language model errors occur
4. **System-Level**: When unexpected errors happen

### Error Types and Responses

- **No Documents**: Suggest PMAY topics
- **No Relevant Text**: Guide to rephrase
- **Reranking Failed**: Technical difficulty message
- **LLM Error**: Processing error message
- **General Error**: Generic error handling
- **Ambiguous Question**: Request clarification

### Monitoring and Logging

- **Debug Logs**: Detailed processing information
- **Error Tracking**: Exception handling and reporting
- **Performance Metrics**: Response times and cache hits
- **User Feedback**: Quality assessment collection

## Text-to-Speech

### Architecture

- **Model Storage**: Local VITS models
- **Language Support**: English and Hindi
- **Caching**: TTL-based audio file caching
- **Cleanup**: Automatic file deletion

### Features

- **High Quality**: VITS-based synthesis
- **Fast Generation**: Optimized model loading
- **Cache Management**: Prevents redundant generation
- **Thread Safety**: Concurrent request handling

### Model Configuration

```python
EN_MODEL_PATH = "models/vits_English_Female/best_model.pth"
EN_CONFIG_PATH = "models/vits_English_Female/config.json"
HI_MODEL_PATH = "models/vits_Hindi_Female/best_model.pth"
HI_CONFIG_PATH = "models/vits_Hindi_Female/config.json"
```

## Testing

### Test Files

1. **`test_enhanced_chatbot.py`**: Comprehensive system tests
2. **`test_self_consistency.py`**: Self-consistency validation
3. **`demo_self_consistency.py`**: Self-consistency demonstration

### Test Coverage

- **API Endpoints**: All chat and utility endpoints
- **Caching**: Greeting and query cache functionality
- **Error Handling**: Fallback mechanism validation
- **Document Processing**: Upload and retrieval testing
- **TTS**: Audio generation and caching

### Running Tests

```bash
python test_enhanced_chatbot.py
python test_self_consistency.py
```

## Deployment

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Services**:
   ```bash
   # Start Ollama
   ollama serve
   
   # Start Redis
   redis-server
   ```

3. **Run Application**:
   ```bash
   uvicorn api.main:app --reload
   ```

### Production Considerations

1. **Environment Variables**: Secure configuration
2. **Service Management**: Process supervision
3. **Monitoring**: Health checks and metrics
4. **Scaling**: Load balancing and caching
5. **Security**: Input validation and sanitization

### Performance Optimization

1. **Caching**: Multi-level cache strategy
2. **Async Processing**: Non-blocking operations
3. **Model Optimization**: Efficient model loading
4. **Resource Management**: Memory and CPU optimization

## Monitoring and Maintenance

### Health Checks

- **Service Status**: Ollama, Redis, ChromaDB
- **Model Availability**: TTS and embedding models
- **Cache Performance**: Hit rates and sizes
- **Response Times**: API endpoint performance

### Logging

- **Debug Information**: Detailed processing logs
- **Error Tracking**: Exception handling
- **Performance Metrics**: Response times
- **User Analytics**: Query patterns and feedback

### Maintenance Tasks

1. **Cache Cleanup**: Regular cache maintenance
2. **Model Updates**: TTS and embedding model updates
3. **Document Management**: Knowledge base maintenance
4. **Performance Monitoring**: System optimization

## Conclusion

The PMAY Chatbot Backend is a sophisticated AI system that combines multiple technologies to provide accurate, helpful, and responsive assistance for PMAY-U scheme information. Its modular architecture, robust error handling, and comprehensive caching strategy ensure reliable performance and excellent user experience.

The system's ability to handle various edge cases, provide graceful fallbacks, and maintain high response quality makes it suitable for production deployment in government services where accuracy and reliability are paramount. 