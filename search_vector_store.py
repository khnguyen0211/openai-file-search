"""
Vector Store Searcher - Pure Search Layer
==========================================
This module provides pure vector store search functionality
without LLM integration. Focuses solely on retrieving relevant
documents from vector stores.

Follows SOLID principles: Single Responsibility - Search Only
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI


class VectorStoreSearcher:
    """
    Pure vector store search functionality.
    
    This class handles ONLY vector store search operations,
    returning raw search results without LLM processing.
    
    Responsibilities:
    1. Connect to vector stores
    2. Execute search queries
    3. Return raw search results
    
    Does NOT:
    - Generate AI responses (handled by Chatbot)
    - Format output for display (handled by Chatbot)
    - Manage conversation state (handled by Chatbot)
    
    Attributes:
        client (OpenAI): OpenAI client instance
        project_root (Path): Root directory of the project
        vector_store_id (str): ID of the vector store to search
        verbose (bool): Show initialization messages
    """
    
    def __init__(
        self, 
        vector_store_id: Optional[str] = None,
        api_key: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize the VectorStoreSearcher.
        
        Args:
            vector_store_id: ID of vector store. If None, will load from file.
            api_key: OpenAI API key. If None, will load from environment.
            verbose: Show initialization messages (default: True)
        """
        load_dotenv()
        
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.project_root = Path(__file__).parent
        
        if vector_store_id:
            self.vector_store_id = vector_store_id
        else:
            self.vector_store_id = self._load_vector_store_id()
        
        self.verbose = verbose
        
        if verbose:
            print(f"[*] VectorStoreSearcher initialized")
            print(f"[*] Vector Store: {self.vector_store_id}\n")
    
    def _load_vector_store_id(self, filename: str = "vector_store_id.txt") -> str:
        """
        Load vector store ID from file.
        
        Args:
            filename: Name of the file containing vector store ID
            
        Returns:
            vector_store_id: The loaded vector store ID
            
        Raises:
            FileNotFoundError: If the ID file doesn't exist
        """
        file_path = self.project_root / filename
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Vector store ID file not found: {file_path}\n"
                "Please run build_vector_store.py first."
            )
        
        with open(file_path, "r") as f:
            vector_store_id = f.read().strip()
        
        return vector_store_id
    
    def search(
        self,
        query: str,
        max_num_results: Optional[int] = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a pure vector search in the vector store.
        
        This method ONLY searches and returns raw results.
        It does NOT generate AI responses.
        
        Args:
            query: Search query text
            max_num_results: Maximum number of results to retrieve
            filters: Metadata filters for search
            
        Returns:
            List of search results with content and scores
            
        Example:
            >>> searcher = VectorStoreSearcher()
            >>> results = searcher.search("Samsung phone")
            >>> for result in results:
            ...     print(f"Score: {result['score']}, Content: {result['content']}")
        """
        print(f"[*] Searching: {query}")
        print(f"[*] Vector Store: {self.vector_store_id}")
        print(f"[*] Max results: {max_num_results}\n")
        
        # Build search parameters
        search_params = {
            "vector_store_id": self.vector_store_id,
            "query": query,
        }
        
        if max_num_results:
            search_params["limit"] = max_num_results
        
        if filters:
            search_params["filter"] = filters
        
        try:
            # Execute vector store search
            # Note: Using vector_stores.search (hypothetical direct API)
            # In practice, we use Responses API but extract only search results
            response = self._execute_search(query, max_num_results, filters)
            
            print(f"[OK] Found {len(response)} results\n")
            return response
            
        except Exception as e:
            print(f"[ERROR] Error during search: {e}")
            raise
    
    def _execute_search(
        self,
        query: str,
        max_num_results: Optional[int],
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute the actual search using OpenAI API.
        
        Note: OpenAI doesn't have a direct vector_stores.search API yet.
        We use Responses API and extract search_results.
        
        Args:
            query: Search query
            max_num_results: Limit results
            filters: Search filters
            
        Returns:
            List of search result dictionaries
        """
        # Build file search tool configuration
        file_search_tool = {
            "type": "file_search",
            "vector_store_ids": [self.vector_store_id]
        }
        
        if max_num_results:
            file_search_tool["max_num_results"] = max_num_results
        
        if filters:
            file_search_tool["filters"] = filters
        
        # Use a simple model just to get search results
        # We don't care about the response text here
        response = self.client.responses.create(
            model="gpt-4o-mini",  # Cheapest model, we only need search results
            input=query,
            tools=[file_search_tool],
            include=["file_search_call.results"]
        )
        
        # Extract search results from response
        search_results = []
        
        for item in response.output:
            if item.type == "file_search_call" and hasattr(item, "results"):
                if item.results:
                    for result in item.results:
                        search_results.append(
                            {
                                "content": result.text if hasattr(result, "text") else "",
                                "score": result.score if hasattr(result, "score") else 0.0,
                                "file_id": result.file_id if hasattr(result, "file_id") else "",
                                "filename": result.filename
                                if hasattr(result, "filename")
                                else "",
                            }
                        )
        
        return search_results
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """
        Get information about the current vector store.
        
        Returns:
            Dictionary with vector store metadata
        """
        try:
            vs = self.client.vector_stores.retrieve(self.vector_store_id)
            
            return {
                'id': vs.id,
                'name': vs.name,
                'status': vs.status,
                'file_counts': {
                    'total': vs.file_counts.total,
                    'completed': vs.file_counts.completed,
                    'in_progress': vs.file_counts.in_progress,
                    'failed': vs.file_counts.failed
                },
                'usage_bytes': vs.usage_bytes,
                'created_at': vs.created_at
            }
        except Exception as e:
            print(f"❌ Error getting vector store info: {e}")
            raise


def main():
    """Main entry point - demonstration of pure search."""
    try:
        # Initialize searcher
        searcher = VectorStoreSearcher()
        
        # Get vector store info
        print("=" * 70)
        print("📊 VECTOR STORE INFO")
        print("=" * 70)
        info = searcher.get_vector_store_info()
        print(f"Name: {info['name']}")
        print(f"Status: {info['status']}")
        print(f"Files: {info['file_counts']['total']} total, {info['file_counts']['completed']} completed")
        print()
        
        # Example search
        print("=" * 70)
        print("🔍 EXAMPLE SEARCH")
        print("=" * 70)
        
        query = "Samsung Galaxy S24"
        results = searcher.search(query, max_num_results=3)
        
        print("📋 SEARCH RESULTS (Raw)")
        print("=" * 70)
        
        for idx, result in enumerate(results, 1):
            print(f"\nResult #{idx}")
            print(f"  Score: {result['score']:.4f}")
            print(f"  File: {result['filename']}")
            content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            print(f"  Content: {content_preview}")
        
        print("\n" + "=" * 70)
        print("ℹ️  Note: This is RAW search results only.")
        print("   For AI-powered responses, use chatbot.py")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
