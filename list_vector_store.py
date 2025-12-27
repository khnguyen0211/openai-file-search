"""
List and Manage Vector Stores
==============================
This script lists all vector stores and their details including
files, metadata, and status information.

Based on OpenAI Vector Stores API.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI


class VectorStoreManager:
    """
    A class to list and manage OpenAI Vector Stores.
    
    This class provides functionality to:
    1. List all vector stores in the account
    2. Get detailed information about specific vector stores
    3. List files within vector stores
    4. Display formatted information
    5. Delete vector stores (optional)
    
    Attributes:
        client (OpenAI): OpenAI client instance
        project_root (Path): Root directory of the project
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the VectorStoreManager.
        
        Args:
            api_key: OpenAI API key. If None, will load from environment.
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # Project configuration
        self.project_root = Path(__file__).parent
        
        print("📋 Vector Store Manager initialized\n")
    
    def list_vector_stores(self, limit: int = 20) -> List[Any]:
        """
        List all vector stores in the account.
        
        Args:
            limit: Maximum number of vector stores to retrieve (default: 20)
            
        Returns:
            List of vector store objects
        """
        print(f"🔍 Fetching vector stores (limit: {limit})...")
        
        try:
            response = self.client.vector_stores.list(limit=limit)
            vector_stores = list(response.data)
            
            print(f"✅ Found {len(vector_stores)} vector store(s)\n")
            return vector_stores
            
        except Exception as e:
            print(f"❌ Error listing vector stores: {e}")
            raise
    
    def get_vector_store_details(self, vector_store_id: str) -> Any:
        """
        Get detailed information about a specific vector store.
        
        Args:
            vector_store_id: ID of the vector store
            
        Returns:
            Vector store object with full details
        """
        try:
            vector_store = self.client.vector_stores.retrieve(vector_store_id)
            return vector_store
            
        except Exception as e:
            print(f"❌ Error retrieving vector store {vector_store_id}: {e}")
            raise
    
    def list_vector_store_files(self, vector_store_id: str, limit: int = 20) -> List[Any]:
        """
        List all files in a specific vector store.
        
        Args:
            vector_store_id: ID of the vector store
            limit: Maximum number of files to retrieve (default: 20)
            
        Returns:
            List of file objects in the vector store
        """
        try:
            response = self.client.vector_stores.files.list(
                vector_store_id=vector_store_id,
                limit=limit
            )
            files = list(response.data)
            return files
            
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            raise
    
    def get_file_details(self, file_id: str) -> Any:
        """
        Get detailed information about a specific file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            File object with full details
        """
        try:
            file = self.client.files.retrieve(file_id)
            return file
            
        except Exception as e:
            print(f"❌ Error retrieving file {file_id}: {e}")
            raise
    
    def display_vector_stores(self, vector_stores: List[Any]) -> None:
        """
        Display vector stores in a formatted table.
        
        Args:
            vector_stores: List of vector store objects
        """
        if not vector_stores:
            print("📭 No vector stores found.")
            return
        
        print("=" * 100)
        print("📊 VECTOR STORES")
        print("=" * 100)
        print()
        
        for idx, vs in enumerate(vector_stores, 1):
            self._display_vector_store_summary(vs, idx)
            print()
    
    def _display_vector_store_summary(self, vs: Any, index: int) -> None:
        """Display summary information for a vector store."""
        print(f"#{index} Vector Store")
        print("-" * 100)
        
        # Basic info
        print(f"   📌 ID:           {vs.id}")
        print(f"   📝 Name:         {vs.name or '(No name)'}")
        print(f"   📊 Status:       {vs.status}")
        
        # Timestamps
        created_at = self._format_timestamp(vs.created_at)
        print(f"   📅 Created:      {created_at}")
        
        if hasattr(vs, 'last_active_at') and vs.last_active_at:
            last_active = self._format_timestamp(vs.last_active_at)
            print(f"   🕐 Last Active:  {last_active}")
        
        # File counts
        if hasattr(vs, 'file_counts') and vs.file_counts:
            print(f"   📁 Files:")
            print(f"      - Total:        {vs.file_counts.total}")
            print(f"      - In Progress:  {vs.file_counts.in_progress}")
            print(f"      - Completed:    {vs.file_counts.completed}")
            print(f"      - Failed:       {vs.file_counts.failed}")
            print(f"      - Cancelled:    {vs.file_counts.cancelled}")
        
        # Usage bytes
        if hasattr(vs, 'usage_bytes'):
            size_mb = vs.usage_bytes / (1024 * 1024)
            print(f"   💾 Storage:      {vs.usage_bytes:,} bytes ({size_mb:.2f} MB)")
        
        # Metadata
        if hasattr(vs, 'metadata') and vs.metadata:
            print(f"   🏷️  Metadata:     {vs.metadata}")
    
    def display_vector_store_details(self, vector_store_id: str) -> None:
        """
        Display detailed information about a vector store including files.
        
        Args:
            vector_store_id: ID of the vector store
        """
        print("=" * 100)
        print(f"🔍 VECTOR STORE DETAILS: {vector_store_id}")
        print("=" * 100)
        print()
        
        # Get vector store details
        vs = self.get_vector_store_details(vector_store_id)
        self._display_vector_store_summary(vs, 1)
        
        print()
        print("-" * 100)
        print("📂 FILES IN VECTOR STORE")
        print("-" * 100)
        
        # Get files in vector store
        vs_files = self.list_vector_store_files(vector_store_id)
        
        if not vs_files:
            print("   📭 No files in this vector store.")
        else:
            print(f"   Found {len(vs_files)} file(s)\n")
            
            for idx, vs_file in enumerate(vs_files, 1):
                self._display_file_summary(vs_file, idx)
                print()
    
    def _display_file_summary(self, vs_file: Any, index: int) -> None:
        """Display summary information for a file in vector store."""
        print(f"   File #{index}")
        print(f"   {'─' * 90}")
        
        print(f"      📌 File ID:       {vs_file.id}")
        print(f"      📊 Status:        {vs_file.status}")
        
        # Get full file details
        try:
            file_details = self.get_file_details(vs_file.id)
            
            print(f"      📝 Filename:      {file_details.filename}")
            print(f"      📁 Purpose:       {file_details.purpose}")
            
            # File size
            if hasattr(file_details, 'bytes'):
                size_kb = file_details.bytes / 1024
                size_mb = size_kb / 1024
                if size_mb >= 1:
                    print(f"      💾 Size:          {file_details.bytes:,} bytes ({size_mb:.2f} MB)")
                else:
                    print(f"      💾 Size:          {file_details.bytes:,} bytes ({size_kb:.2f} KB)")
            
            # Created timestamp
            if hasattr(file_details, 'created_at'):
                created = self._format_timestamp(file_details.created_at)
                print(f"      📅 Created:       {created}")
        
        except Exception as e:
            print(f"      ⚠️  Could not retrieve file details: {e}")
        
        # Vector store file specific info
        if hasattr(vs_file, 'created_at'):
            added = self._format_timestamp(vs_file.created_at)
            print(f"      ➕ Added to VS:   {added}")
        
        if hasattr(vs_file, 'last_error') and vs_file.last_error:
            print(f"      ❌ Last Error:    {vs_file.last_error}")
    
    def _format_timestamp(self, timestamp: int) -> str:
        """
        Format Unix timestamp to readable string.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted datetime string
        """
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def delete_vector_store(self, vector_store_id: str, confirm: bool = False) -> bool:
        """
        Delete a vector store.
        
        Args:
            vector_store_id: ID of the vector store to delete
            confirm: Confirmation flag (safety check)
            
        Returns:
            True if deleted successfully
            
        Note:
            This is a destructive operation. Use with caution!
        """
        if not confirm:
            print("⚠️  Delete operation requires confirmation.")
            print("   Set confirm=True to proceed.")
            return False
        
        print(f"🗑️  Deleting vector store: {vector_store_id}")
        
        try:
            self.client.vector_stores.delete(vector_store_id)
            print("✅ Vector store deleted successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting vector store: {e}")
            raise
    
    def find_vector_store_by_name(self, name: str) -> Optional[Any]:
        """
        Find a vector store by name.
        
        Args:
            name: Name of the vector store
            
        Returns:
            Vector store object if found, None otherwise
        """
        vector_stores = self.list_vector_stores(limit=100)
        
        for vs in vector_stores:
            if vs.name == name:
                return vs
        
        return None
    
    def get_current_vector_store_id(self) -> Optional[str]:
        """
        Get the vector store ID from the saved file.
        
        Returns:
            Vector store ID if file exists, None otherwise
        """
        file_path = self.project_root / "vector_store_id.txt"
        
        if not file_path.exists():
            return None
        
        with open(file_path, "r") as f:
            return f.read().strip()


def main():
    """Main entry point for the script."""
    try:
        # Initialize manager
        manager = VectorStoreManager()
        
        # List all vector stores
        vector_stores = manager.list_vector_stores(limit=20)
        manager.display_vector_stores(vector_stores)
        
        # If there's a current vector store, show details
        current_id = manager.get_current_vector_store_id()
        
        if current_id:
            print("\n" + "=" * 100)
            print(f"📍 CURRENT VECTOR STORE (from vector_store_id.txt)")
            print("=" * 100)
            print()
            manager.display_vector_store_details(current_id)
        
        # Show summary
        print("\n" + "=" * 100)
        print("📈 SUMMARY")
        print("=" * 100)
        print(f"   Total vector stores: {len(vector_stores)}")
        
        if current_id:
            print(f"   Current vector store: {current_id}")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
