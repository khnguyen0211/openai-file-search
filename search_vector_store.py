"""
Search Vector Store for OpenAI File Search
===========================================
This script searches in a vector store using OpenAI Responses API
and displays the results with citations and annotations.

Based on OpenAI File Search documentation.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI


class VectorStoreSearcher:
    """
    A class to search and query OpenAI Vector Stores using file search.
    
    This class handles:
    1. Loading vector store ID from file or direct input
    2. Performing semantic/keyword search using Responses API
    3. Displaying results with citations and annotations
    4. Customizing search parameters (max results, filters, etc.)
    
    Attributes:
        client (OpenAI): OpenAI client instance
        project_root (Path): Root directory of the project
        vector_store_id (str): ID of the vector store to search
        model (str): Model to use for responses
    """
    
    def __init__(
        self, 
        vector_store_id: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize the VectorStoreSearcher.
        
        Args:
            vector_store_id: ID of vector store. If None, will load from file.
            api_key: OpenAI API key. If None, will load from environment.
            model: Model to use (default: gpt-4o)
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # Project configuration
        self.project_root = Path(__file__).parent
        
        # Model configuration
        self.model = model
        
        # Load or set vector store ID
        if vector_store_id:
            self.vector_store_id = vector_store_id
        else:
            self.vector_store_id = self._load_vector_store_id()
        
        print(f"🔍 Searcher initialized with Vector Store: {self.vector_store_id}")
        print(f"🤖 Using model: {self.model}\n")
    
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
        max_num_results: Optional[int] = None,
        include_search_results: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform a search in the vector store.
        
        Args:
            query: Search query text
            max_num_results: Maximum number of results to retrieve
            include_search_results: Whether to include search results in response
            filters: Metadata filters for search
            
        Returns:
            response: The complete response object from OpenAI
        """
        print("=" * 70)
        print(f"🔎 SEARCHING: {query}")
        print("=" * 70)
        print()
        
        # Build file search tool configuration
        file_search_tool = {
            "type": "file_search",
            "vector_store_ids": [self.vector_store_id]
        }
        
        # Add optional parameters
        if max_num_results:
            file_search_tool["max_num_results"] = max_num_results
        
        if filters:
            file_search_tool["filters"] = filters
        
        # Build include array
        include = []
        if include_search_results:
            include.append("file_search_call.results")
        
        # Perform search
        try:
            response = self.client.responses.create(
                model=self.model,
                input=query,
                tools=[file_search_tool],
                include=include if include else None
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            raise
    
    def display_results(self, response: Any) -> None:
        """
        Display search results in a formatted way.
        
        Args:
            response: Response object from search()
        """
        print("📋 SEARCH RESULTS")
        print("=" * 70)
        print()
        
        # Check if we have output
        if not hasattr(response, 'output') or not response.output:
            print("⚠️  No results found.")
            return
        
        # Iterate through output items
        for idx, item in enumerate(response.output):
            
            # Handle file_search_call type
            if item.type == "file_search_call":
                self._display_file_search_call(item, idx + 1)
            
            # Handle message type
            elif item.type == "message":
                self._display_message(item, idx + 1)
        
        print()
        print("=" * 70)
    
    def _display_file_search_call(self, item: Any, index: int) -> None:
        """Display file search call information."""
        print(f"🔍 File Search Call #{index}")
        print(f"   ID: {item.id}")
        print(f"   Status: {item.status}")
        
        if hasattr(item, 'queries') and item.queries:
            print(f"   Queries: {item.queries}")
        
        # Display search results if available
        if hasattr(item, 'search_results') and item.search_results:
            print(f"\n   📊 Search Results Found: {len(item.search_results)}")
            
            for i, result in enumerate(item.search_results, 1):
                print(f"\n   Result {i}:")
                
                # Display file information
                if hasattr(result, 'file_id'):
                    print(f"      File ID: {result.file_id}")
                if hasattr(result, 'filename'):
                    print(f"      Filename: {result.filename}")
                if hasattr(result, 'score'):
                    print(f"      Score: {result.score:.4f}")
                
                # Display content snippet
                if hasattr(result, 'content'):
                    content = result.content[:300] + "..." if len(result.content) > 300 else result.content
                    print(f"      Content:\n         {content}")
        
        print()
    
    def _display_message(self, item: Any, index: int) -> None:
        """Display message content with annotations."""
        print(f"💬 Message #{index}")
        print(f"   ID: {item.id}")
        print(f"   Role: {item.role}")
        print()
        
        # Display content
        if hasattr(item, 'content') and item.content:
            for content_item in item.content:
                
                if content_item.type == "output_text":
                    print("   📝 Response:")
                    print("   " + "-" * 66)
                    
                    # Display text with word wrapping
                    text = content_item.text
                    self._print_wrapped(text, prefix="   ")
                    
                    print("   " + "-" * 66)
                    
                    # Display annotations (citations)
                    if hasattr(content_item, 'annotations') and content_item.annotations:
                        print()
                        print("   📚 Citations:")
                        
                        for i, annotation in enumerate(content_item.annotations, 1):
                            if annotation.type == "file_citation":
                                print(f"      [{i}] File: {annotation.filename}")
                                print(f"          File ID: {annotation.file_id}")
                                print(f"          Position: {annotation.index}")
        
        print()
    
    def _print_wrapped(self, text: str, prefix: str = "", width: int = 66) -> None:
        """Print text with word wrapping."""
        words = text.split()
        line = prefix
        
        for word in words:
            if len(line) - len(prefix) + len(word) + 1 > width:
                print(line)
                line = prefix + word + " "
            else:
                line += word + " "
        
        if line.strip():
            print(line)
    
    def search_and_display(
        self,
        query: str,
        max_num_results: Optional[int] = None,
        include_search_results: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to search and display results in one call.
        
        Args:
            query: Search query text
            max_num_results: Maximum number of results to retrieve
            include_search_results: Whether to include search results
            filters: Metadata filters for search
            
        Returns:
            response: The complete response object from OpenAI
        """
        response = self.search(
            query=query,
            max_num_results=max_num_results,
            include_search_results=include_search_results,
            filters=filters
        )
        
        self.display_results(response)
        
        return response
    
    def get_raw_response(self, response: Any) -> str:
        """
        Get the raw JSON response for debugging.
        
        Args:
            response: Response object from search()
            
        Returns:
            JSON string of the response
        """
        return json.dumps(response.model_dump(), indent=2, ensure_ascii=False)


def main():
    """Main entry point for the script."""
    try:
        # Initialize searcher (auto-loads vector store ID from file)
        searcher = VectorStoreSearcher()
        
        # Example queries
        queries = [
            "Tần số quét màn hình 1-120Hz, Tốc độ lấy mẫu cảm ứng 240Hz",
        ]
        
        # Run first query as example
        print("🎯 Running example search...\n")
        searcher.search_and_display(
            query=queries[0],
            max_num_results=5,
            include_search_results=True
        )
        
        # Uncomment to run all queries
        # for query in queries:
        #     searcher.search_and_display(query, max_num_results=5)
        #     print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
