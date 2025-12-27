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

**Search your indexed data:**
```bash
python search_vector_store.py
```

**View and manage vector stores:**
```bash
python list_vector_store.py
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

### 2. Searching Vector Stores

Perform semantic searches and get AI-powered responses:

```python
from search_vector_store import VectorStoreSearcher

# Initialize searcher (auto-loads vector store ID)
searcher = VectorStoreSearcher()

# Search and display results
searcher.search_and_display(
    query="Find Samsung phones under $500",
    max_num_results=5,
    include_search_results=True
)
```

**Advanced Search:**
```python
# Custom search with specific parameters
response = searcher.search(
    query="Compare iPhone 15 Pro and Galaxy S24",
    max_num_results=3,
    include_search_results=True
)

# Display formatted results
searcher.display_results(response)

# Access raw JSON for custom processing
raw_data = searcher.get_raw_response(response)
```

### 3. Managing Vector Stores

List, inspect, and manage your vector stores:

```python
from list_vector_store import VectorStoreManager

# Initialize manager
manager = VectorStoreManager()

# List all vector stores
vector_stores = manager.list_vector_stores(limit=20)
manager.display_vector_stores(vector_stores)

# Get details of specific store
manager.display_vector_store_details("vs_abc123...")

# Find by name
vs = manager.find_vector_store_by_name("product_catalog")
if vs:
    files = manager.list_vector_store_files(vs.id)
    print(f"Store contains {len(files)} files")
```

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────┐
│     VectorStoreBuilder                  │
│                                         │
│  • Upload files to OpenAI               │
│  • Create vector stores                 │
│  • Monitor indexing status              │
│  • Manage store lifecycle               │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     VectorStoreSearcher                 │
│                                         │
│  • Semantic search queries              │
│  • AI-powered responses                 │
│  • Citation extraction                  │
│  • Result formatting                    │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     VectorStoreManager                  │
│                                         │
│  • List all stores                      │
│  • View store details                   │
│  • Manage files                         │
│  • Delete operations                    │
└─────────────────────────────────────────┘
```

### Project Structure

```
openai-file-search/
├── build_vector_store.py      # Vector store creation and indexing
├── search_vector_store.py     # Search functionality and AI responses
├── list_vector_store.py       # Vector store management
│
├── data/                      # Data directory
│   └── hoanghamobile.csv      # Sample dataset (2995 products)
│
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
├── SETUP.md                   # Detailed documentation (Vietnamese)
├── QUICK_REF.md               # Quick reference guide
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

### VectorStoreSearcher

| Method | Description | Returns |
|--------|-------------|---------|
| `search_and_display(query, max_num_results, ...)` | Search and display results | `response` |
| `search(query, max_num_results, filters)` | Execute search query | `response` |
| `display_results(response)` | Format and print results | `None` |
| `get_raw_response(response)` | Get JSON response | `str` |

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

### Product Catalog Search
```python
# Index product database
builder = VectorStoreBuilder()
builder.build(csv_file_path="data/products.csv")

# Intelligent product search
searcher = VectorStoreSearcher()
searcher.search_and_display("phones with 5000mAh battery under $400")
```

### Knowledge Base Q&A
```python
# Build knowledge base from documents
builder.build(csv_file_path="data/documentation.csv")

# Ask questions
searcher.search_and_display("How to configure authentication?")
```

### Data Analytics Assistant
```python
# Search with filters and custom parameters
response = searcher.search(
    query="Analyze sales trends for Q4",
    max_num_results=10,
    include_search_results=True
)
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