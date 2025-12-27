"""
Build Vector Store for OpenAI File Search
==========================================
This script loads a CSV file from the data folder, uploads it to OpenAI,
creates a vector store, and returns the vector store ID.

Based on OpenAI File Search documentation.
"""

import os
import time
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI


class VectorStoreBuilder:
    """
    A class to build and manage OpenAI Vector Stores for file search.
    
    This class handles the complete workflow of:
    1. Uploading files to OpenAI File API
    2. Creating vector stores
    3. Adding files to vector stores
    4. Monitoring processing status
    
    Attributes:
        client (OpenAI): OpenAI client instance
        project_root (Path): Root directory of the project
        vector_store_id (str): ID of the created vector store
        file_id (str): ID of the uploaded file
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the VectorStoreBuilder.
        
        Args:
            api_key: OpenAI API key. If None, will load from environment variables.
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # Project configuration
        self.project_root = Path(__file__).parent
        
        # Store IDs for later reference
        self.vector_store_id: Optional[str] = None
        self.file_id: Optional[str] = None
    
    def upload_file(self, file_path: str) -> str:
        """
        Upload a file to OpenAI File API.
        
        Args:
            file_path: Path to the file to upload (absolute path)
            
        Returns:
            file_id: ID of the uploaded file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"📤 Uploading file: {file_path}")
        
        with open(file_path, "rb") as file_content:
            result = self.client.files.create(
                file=file_content,
                purpose="assistants"
            )
        
        self.file_id = result.id
        print(f"✅ File uploaded successfully! File ID: {result.id}")
        return result.id
    
    def create_vector_store(self, name: str = "hoanghamobile_products") -> str:
        """
        Create a vector store.
        
        Args:
            name: Name for the vector store
            
        Returns:
            vector_store_id: ID of the created vector store
        """
        print(f"🏗️  Creating vector store: {name}")
        
        vector_store = self.client.vector_stores.create(name=name)
        
        self.vector_store_id = vector_store.id
        print(f"✅ Vector store created! ID: {vector_store.id}")
        return vector_store.id
    
    def add_file_to_vector_store(self, vector_store_id: str, file_id: str) -> dict:
        """
        Add a file to a vector store.
        
        Args:
            vector_store_id: ID of the vector store
            file_id: ID of the file to add
            
        Returns:
            result: Vector store file object
        """
        print(f"📎 Adding file to vector store...")
        
        result = self.client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        
        print(f"✅ File added to vector store!")
        return result
    
    def check_vector_store_status(
        self, 
        vector_store_id: str, 
        max_wait: int = 60,
        check_interval: int = 2
    ) -> bool:
        """
        Check if files in vector store are ready (status = completed).
        
        Args:
            vector_store_id: ID of the vector store
            max_wait: Maximum time to wait in seconds (default: 60)
            check_interval: Interval between status checks in seconds (default: 2)
            
        Returns:
            bool: True if ready, False if timeout
        """
        print(f"⏳ Checking vector store status...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            result = self.client.vector_stores.files.list(
                vector_store_id=vector_store_id
            )
            
            # Check if all files are completed
            all_completed = all(file.status == "completed" for file in result.data)
            
            if all_completed:
                print(f"✅ Vector store is ready! All files processed.")
                return True
            
            # Show current status
            statuses = [f.status for f in result.data]
            print(f"   Status: {statuses}")
            
            time.sleep(check_interval)
        
        print(f"⚠️  Timeout waiting for vector store to be ready")
        return False
    
    def build(
        self, 
        csv_file_path: str = "data/hoanghamobile.csv",
        vector_store_name: str = "hoanghamobile_products",
        max_wait: int = 60
    ) -> str:
        """
        Main method to build vector store from CSV file.
        
        This method orchestrates the entire workflow:
        1. Upload the CSV file
        2. Create a vector store
        3. Add the file to the vector store
        4. Wait for processing to complete
        
        Args:
            csv_file_path: Path to the CSV file (relative to project root)
            vector_store_name: Name for the vector store
            max_wait: Maximum time to wait for processing (seconds)
            
        Returns:
            vector_store_id: ID of the created and ready vector store
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            RuntimeError: If vector store processing times out
        """
        print("=" * 60)
        print("🚀 Building Vector Store for OpenAI File Search")
        print("=" * 60)
        
        # Get absolute path
        file_path = self.project_root / csv_file_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        print(f"📁 File location: {file_path}")
        print()
        
        # Step 1: Upload file
        file_id = self.upload_file(str(file_path))
        print()
        
        # Step 2: Create vector store
        vector_store_id = self.create_vector_store(vector_store_name)
        print()
        
        # Step 3: Add file to vector store
        self.add_file_to_vector_store(vector_store_id, file_id)
        print()
        
        # Step 4: Wait for processing to complete
        is_ready = self.check_vector_store_status(vector_store_id, max_wait)
        print()
        
        if is_ready:
            print("=" * 60)
            print("🎉 SUCCESS!")
            print(f"📊 Vector Store ID: {vector_store_id}")
            print(f"📄 File ID: {file_id}")
            print("=" * 60)
            return vector_store_id
        else:
            raise RuntimeError("Vector store processing did not complete in time")
    
    def save_vector_store_id(self, output_file: str = "vector_store_id.txt") -> None:
        """
        Save the vector store ID to a file for later use.
        
        Args:
            output_file: Name of the output file (default: vector_store_id.txt)
        """
        if not self.vector_store_id:
            raise ValueError("No vector store ID to save. Run build() first.")
        
        output_path = self.project_root / output_file
        with open(output_path, "w") as f:
            f.write(self.vector_store_id)
        
        print(f"💾 Vector Store ID saved to: {output_path}")


def main():
    """Main entry point for the script."""
    try:
        # Initialize builder
        builder = VectorStoreBuilder()
        
        # Build vector store
        vector_store_id = builder.build(
            csv_file_path="data/hoanghamobile.csv",
            vector_store_name="hoanghamobile_products",
            max_wait=60
        )
        
        # Save vector store ID to file
        builder.save_vector_store_id("vector_store_id.txt")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
