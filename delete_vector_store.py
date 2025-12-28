"""
Vector Store Deleter - Clean Up Resources
==========================================
This module provides functionality to delete vector stores and files
from OpenAI to clean up resources and free up quota.

Follows SOLID principles: Single Responsibility - Delete Only
"""

import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from openai import OpenAI


class VectorStoreDeleter:
    """Delete vector stores and files from OpenAI.

    This class handles ONLY deletion operations for:
    1. Vector stores
    2. Files uploaded to OpenAI
    3. Cleanup of local ID files

    Responsibilities:
    - List all vector stores and files
    - Delete specific vector store
    - Delete all files in a vector store
    - Delete uploaded files
    - Clean up local storage

    Note: This class does NOT create or search - only deletes.
    """

    def __init__(
        self,
        vector_store_id: Optional[str] = None,
        api_key: Optional[str] = None,
        verbose: bool = True,
    ):
        """
        Initialize the VectorStoreDeleter.

        Args:
            vector_store_id: ID of vector store. If None, will load from file.
            api_key: OpenAI API key. If None, will load from environment.
            verbose: Show deletion messages (default: True)
        """
        load_dotenv()

        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.verbose = verbose

        # Load vector store ID if not provided
        if vector_store_id:
            self.vector_store_id = vector_store_id
        else:
            try:
                self.vector_store_id = self._load_vector_store_id()
                if self.verbose:
                    print(f"✅ Loaded vector store ID: {self.vector_store_id}")
            except FileNotFoundError:
                self.vector_store_id = None
                if self.verbose:
                    print("⚠️  No vector store ID file found")

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
        file_path = Path(filename)

        if not file_path.exists():
            raise FileNotFoundError(f"Vector store ID file not found: {filename}")

        with open(file_path, "r") as f:
            vector_store_id = f.read().strip()

        return vector_store_id

    def list_vector_store_files(self, vector_store_id: Optional[str] = None) -> List:
        """
        List all files in a vector store.

        Args:
            vector_store_id: ID of vector store (uses default if None)

        Returns:
            List of file objects in the vector store
        """
        vs_id = vector_store_id or self.vector_store_id

        if not vs_id:
            if self.verbose:
                print("❌ No vector store ID provided")
            return []

        try:
            files = self.client.vector_stores.files.list(vector_store_id=vs_id)
            return list(files.data)
        except Exception as e:
            if self.verbose:
                print(f"❌ Error listing files: {e}")
            return []

    def delete_vector_store(self, vector_store_id: Optional[str] = None) -> bool:
        """
        Delete a vector store.

        Args:
            vector_store_id: ID of vector store to delete (uses default if None)

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        vs_id = vector_store_id or self.vector_store_id

        if not vs_id:
            if self.verbose:
                print("❌ No vector store ID provided")
            return False

        try:
            if self.verbose:
                print(f"🗑️  Deleting vector store: {vs_id}")

            self.client.vector_stores.delete(vector_store_id=vs_id)

            if self.verbose:
                print("✅ Vector store deleted successfully")

            return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Error deleting vector store: {e}")
            return False

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a single file from OpenAI.

        Args:
            file_id: ID of the file to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            if self.verbose:
                print(f"🗑️  Deleting file: {file_id}")

            self.client.files.delete(file_id=file_id)

            if self.verbose:
                print("✅ File deleted successfully")

            return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Error deleting file: {e}")
            return False

    def delete_all_files_in_vector_store(
        self, vector_store_id: Optional[str] = None
    ) -> int:
        """
        Delete all files in a vector store.

        Note: This deletes files from OpenAI storage, not just from the vector store.

        Args:
            vector_store_id: ID of vector store (uses default if None)

        Returns:
            int: Number of files deleted
        """
        files = self.list_vector_store_files(vector_store_id)

        if not files:
            if self.verbose:
                print("ℹ️  No files found in vector store")
            return 0

        deleted_count = 0

        if self.verbose:
            print(f"📋 Found {len(files)} file(s) to delete")

        for file in files:
            if self.delete_file(file.id):
                deleted_count += 1

        if self.verbose:
            print(f"✅ Deleted {deleted_count}/{len(files)} file(s)")

        return deleted_count

    def cleanup_local_files(self, id_filename: str = "vector_store_id.txt") -> bool:
        """
        Delete local vector store ID file.

        Args:
            id_filename: Name of the local ID file

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        file_path = Path(id_filename)

        if not file_path.exists():
            if self.verbose:
                print(f"ℹ️  Local file not found: {id_filename}")
            return False

        try:
            file_path.unlink()
            if self.verbose:
                print(f"✅ Deleted local file: {id_filename}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"❌ Error deleting local file: {e}")
            return False

    def delete_all(
        self, vector_store_id: Optional[str] = None, cleanup_local: bool = True
    ) -> bool:
        """
        Complete cleanup: Delete vector store, all its files, and local ID file.

        This is the main method that orchestrates the complete cleanup workflow:
        1. List all files in vector store
        2. Delete all files from OpenAI
        3. Delete the vector store itself
        4. Clean up local ID file (optional)

        Args:
            vector_store_id: ID of vector store (uses default if None)
            cleanup_local: Whether to delete local ID file (default: True)

        Returns:
            bool: True if all operations succeeded, False otherwise
        """
        vs_id = vector_store_id or self.vector_store_id

        if not vs_id:
            if self.verbose:
                print("❌ No vector store ID provided")
            return False

        if self.verbose:
            print("\n" + "=" * 60)
            print("🧹 CLEANUP: Deleting all resources")
            print("=" * 60 + "\n")

        success = True

        # Step 1: Delete all files in vector store
        if self.verbose:
            print("Step 1: Deleting files...")
        _ = self.delete_all_files_in_vector_store(
            vs_id
        )  # Return value logged by method itself

        # Step 2: Delete vector store
        if self.verbose:
            print("\nStep 2: Deleting vector store...")
        if not self.delete_vector_store(vs_id):
            success = False

        # Step 3: Clean up local files
        if cleanup_local:
            if self.verbose:
                print("\nStep 3: Cleaning up local files...")
            if not self.cleanup_local_files():
                success = False

        if self.verbose:
            print("\n" + "=" * 60)
            if success:
                print("✅ CLEANUP COMPLETED SUCCESSFULLY")
            else:
                print("⚠️  CLEANUP COMPLETED WITH SOME ERRORS")
            print("=" * 60 + "\n")

        return success

    def list_all_vector_stores(self) -> List:
        """
        List all vector stores in the account.

        Returns:
            List of vector store objects
        """
        try:
            stores = self.client.vector_stores.list()
            return list(stores.data)
        except Exception as e:
            if self.verbose:
                print(f"❌ Error listing vector stores: {e}")
            return []

    def list_all_files(self, purpose: str = "assistants") -> List:
        """
        List all files uploaded to OpenAI.

        Args:
            purpose: Filter by purpose (default: "assistants")

        Returns:
            List of file objects
        """
        try:
            files = self.client.files.list(purpose=purpose)
            return list(files.data)
        except Exception as e:
            if self.verbose:
                print(f"❌ Error listing files: {e}")
            return []


def main():
    """Main entry point - demonstration of deletion."""
    print("\n" + "=" * 60)
    print("Vector Store Deleter - Cleanup Tool")
    print("=" * 60 + "\n")

    # Initialize deleter
    deleter = VectorStoreDeleter(verbose=True)

    if not deleter.vector_store_id:
        print("❌ No vector store found to delete")
        print("   Please build a vector store first using build_vector_store.py")
        return

    # Ask for confirmation
    print(f"⚠️  WARNING: This will delete vector store: {deleter.vector_store_id}")
    print("   This action CANNOT be undone!\n")

    confirmation = input("Type 'DELETE' to confirm: ").strip()

    if confirmation != "DELETE":
        print("\n❌ Deletion cancelled")
        return

    # Perform deletion
    print()
    success = deleter.delete_all()

    if success:
        print("🎉 All resources cleaned up successfully!")
    else:
        print("⚠️  Some errors occurred during cleanup")


if __name__ == "__main__":
    main()
