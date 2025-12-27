# OpenAI File Search

> A Python-based vector store management system for OpenAI's File Search API, providing seamless document indexing and intelligent semantic search capabilities.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://platform.openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

This project implements a comprehensive vector store management system using OpenAI's Responses API and File Search capabilities. It enables users to build, search, and manage vector stores for efficient document retrieval and AI-powered question answering.

### Key Features

- **🔨 Vector Store Builder**: Automated pipeline for uploading files and creating indexed vector stores
- **🔍 Intelligent Search**: Semantic and keyword-based search with AI-generated responses and citations
- **📊 Store Management**: Complete lifecycle management of vector stores with detailed analytics
- **💾 File Support**: CSV, PDF, TXT, JSON, Markdown, and code files
- **🎯 Customizable**: Flexible search parameters, result limits, and metadata filtering
- **📝 Rich Output**: Formatted results with citations, annotations, and relevance scores

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/openai-file-search.git
cd openai-file-search
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API key**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-api-key-here
```

### First Run

**Build a vector store from your CSV data:**
```bash
python build_vector_store.py
```

**Start the interactive chatbot:**
```bash
python chatbot.py
```

The chatbot provides an interactive interface with commands:
- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/model` - Switch between GPT-4o and GPT-4o-mini
- `/exit` - Exit the chatbot

**For programmatic search (returns raw data):**
```bash
python search_vector_store.py
```

## 💻 Usage

### 1. Building Vector Stores

Create and index your documents for searchable vector storage:

```python
from build_vector_store import VectorStoreBuilder

# Initialize builder
builder = VectorStoreBuilder()

# Build vector store from CSV file
vector_store_id = builder.build(
    csv_file_path="data/hoanghamobile.csv",
    vector_store_name="product_catalog",
    max_wait=60
)

# Save the ID for later use
builder.save_vector_store_id("vector_store_id.txt")
```

### 2. Interactive Chatbot (Recommended)

The easiest way to interact with your vector store - a conversational AI interface:

```python
from chatbot import Chatbot

# Initialize chatbot (auto-loads vector store)
bot = Chatbot(model="gpt-4o")

# Interactive mode (default when running chatbot.py)
# Or programmatic usage:
response = bot.chat("Find Samsung phones under $500")
print(response)  # AI-generated answer with context

# Chat without vector context (pure LLM knowledge)
response = bot.chat("Hello, who are you?", use_vector_context=False)
```

### 3. Raw Vector Search (Advanced)

For applications needing raw search results without AI processing:

```python
from search_vector_store import VectorStoreSearcher

# Initialize searcher
searcher = VectorStoreSearcher()

# Get raw search results
results = searcher.search(
    query="Samsung Galaxy S24",
    max_num_results=5
)

# Process raw results
for result in results:
    print(f"Score: {result['score']}")
    print(f"Content: {result['content']}")
```

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────┐
│     VectorStoreBuilder                  │
│     (build_vector_store.py)             │
│                                         │
│  • Upload files to OpenAI               │
│  • Create vector stores                 │
│  • Monitor indexing status              │
│  • Manage store lifecycle               │
└─────────────────────────────────────────┘
                   │
                   ▼
         vector_store_id.txt
                   │
    ┌──────────────┴──────────────┐
    │                             │
    ▼                             ▼
┌─────────────────────┐   ┌─────────────────────┐
│ VectorStoreSearcher │   │      Chatbot        │
│ (search_vector...)  │   │   (chatbot.py)      │
│                     │   │                     │
│ • Pure search layer │   │ • LLM integration   │
│ • Returns raw data  │   │ • Conversation mgmt │
│ • No AI processing  │   │ • User interface    │
│                     │   │ • Uses Searcher     │
└─────────────────────┘   └─────────────────────┘
         │                         │
         │                         │
         ▼                         ▼
   Raw Results            AI-Powered Responses
  (for apps/APIs)       (for end users)
```

### Separation of Concerns (SOLID Principles)

**1. VectorStoreBuilder** - Data Preparation Layer
- Single Responsibility: Build and manage vector stores
- Used once during setup or data updates

**2. VectorStoreSearcher** - Data Access Layer  
- Single Responsibility: Execute searches, return raw results
- No LLM, no formatting, pure search functionality
- Reusable by any application layer

**3. Chatbot** - Application/Presentation Layer
- Single Responsibility: User interaction and AI responses
- Depends on VectorStoreSearcher (Dependency Injection)
- Handles LLM calls, conversation state, formatting

### Project Structure

```
openai-file-search/
├── build_vector_store.py      # Vector store creation and indexing
├── search_vector_store.py     # Pure search functionality (data layer)
├── chatbot.py                 # Interactive AI chatbot (application layer)
├── list_vector_store.py       # Vector store management
│
├── data/                      # Data directory
│   └── hoanghamobile.csv      # Sample dataset (2995 products)
│
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
├── SETUP.md                   # Detailed documentation (Vietnamese)
├── QUICK_REF.md               # Quick reference guide
├── learning.md                # Educational guide about LLM & Vector Search
└── vector_store_id.txt        # Current vector store ID (auto-generated)
```

## 📚 API Reference

### VectorStoreBuilder

| Method | Description | Returns |
|--------|-------------|---------|
| `build(csv_file_path, vector_store_name, max_wait)` | Build complete vector store | `vector_store_id` |
| `upload_file(file_path)` | Upload file to OpenAI | `file_id` |
| `create_vector_store(name)` | Create new vector store | `vector_store_id` |
| `save_vector_store_id(output_file)` | Save store ID to file | `None` |

### VectorStoreSearcher (Data Layer)

| Method | Description | Returns |
|--------|-------------|---------|
| `search(query, max_num_results, filters)` | Execute search, return raw results | `List[Dict]` |
| `get_vector_store_info()` | Get vector store metadata | `Dict` |

**Note:** This class returns raw search results only, without LLM processing.

### Chatbot (Application Layer)

| Method | Description | Returns |
|--------|-------------|---------|
| `chat(message, use_vector_context)` | Get AI response with optional context | `str` |
| `clear_history()` | Clear conversation history | `None` |
| `set_model(model)` | Change LLM model | `None` |
| `get_history()` | Get conversation history | `List[Dict]` |

### VectorStoreManager

| Method | Description | Returns |
|--------|-------------|---------|
| `list_vector_stores(limit)` | List all stores | `List[VectorStore]` |
| `get_vector_store_details(vector_store_id)` | Get store details | `VectorStore` |
| `list_vector_store_files(vector_store_id)` | List files in store | `List[File]` |
| `find_vector_store_by_name(name)` | Find store by name | `VectorStore \| None` |
| `delete_vector_store(vector_store_id, confirm)` | Delete store | `bool` |

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Optional: Custom model settings
# DEFAULT_MODEL=gpt-4o
```

### Supported File Types

- **Documents**: `.pdf`, `.txt`, `.md`, `.doc`, `.docx`
- **Data**: `.csv`, `.json`
- **Code**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rb`, `.php`
- **Presentations**: `.pptx`

## 🎯 Use Cases

### Interactive Customer Support
```python
# Use chatbot for conversational interface
from chatbot import Chatbot

bot = Chatbot()

# Natural language interaction
response = bot.chat("I need a phone with good camera under $400")
print(response)  # AI explains options with specific recommendations
```

### API Integration (E-commerce Search)
```python
# Use raw searcher for API endpoints
from search_vector_store import VectorStoreSearcher
from fastapi import FastAPI

app = FastAPI()
searcher = VectorStoreSearcher()

@app.get("/products/search")
async def search_products(q: str):
    results = searcher.search(q, max_num_results=10)
    return {"results": results}  # Return raw data for frontend processing
```

### Knowledge Base Q&A
```python
# Build knowledge base from documents
builder = VectorStoreBuilder()
builder.build(csv_file_path="data/documentation.csv")

# Interactive Q&A
bot = Chatbot()
while True:
    question = input("Ask a question: ")
    if question.lower() == 'exit':
        break
    answer = bot.chat(question)
    print(f"\nAnswer: {answer}\n")
```

### Data Analytics Assistant
```python
# Combine chatbot with programmatic search
bot = Chatbot()
searcher = VectorStoreSearcher()

# Natural language query
nl_response = bot.chat("What are the trending products in Q4?")

# Get raw data for analysis
raw_results = searcher.search("Q4 trending products", max_num_results=50)
# Process raw_results for charts, reports, etc.
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'dotenv'` | Run `pip install -r requirements.txt` |
| `OPENAI_API_KEY not found` | Check `.env` file exists and contains valid API key |
| `File not found` | Ensure CSV file is in `data/` directory |
| `Timeout waiting for vector store` | Increase `max_wait` parameter or check internet connection |

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

**ProtonX Team**
- GitHub: [@khnguyen0211](https://github.com/khnguyen0211)
- Project: [openai-file-search](https://github.com/khnguyen0211/openai-file-search)

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for providing the powerful AI APIs
- OpenAI Responses API and Vector Stores documentation
- Community contributors and testers

## 📞 Support

For questions and support:
- 📖 Check [SETUP.md](SETUP.md) for detailed documentation
- 🚀 See [QUICK_REF.md](QUICK_REF.md) for quick reference
- 🐛 Report issues on [GitHub Issues](https://github.com/khnguyen0211/openai-file-search/issues)

---

**Built with ❤️ using OpenAI's cutting-edge AI technology**