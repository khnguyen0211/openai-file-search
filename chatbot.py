"""
AI Chatbot with Vector Store Integration
==========================================
Interactive chatbot with clean UX and vector store context.
Type /help for commands, /exit to quit.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from search_vector_store import VectorStoreSearcher
from delete_vector_store import VectorStoreDeleter

# Fix encoding for Windows terminal to support Vietnamese
if sys.platform == "win32":
    try:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "str ict")
    except:
        pass


def safe_print(*args, **kwargs):
    """Safe print that handles encoding errors gracefully."""
    try:
        print(*args, **kwargs)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback: encode to ASCII with replacement
        text = " ".join(str(arg) for arg in args)
        try:
            print(text.encode("ascii", "replace").decode("ascii"), **kwargs)
        except:
            print(
                "[Output contains special characters that cannot be displayed]",
                **kwargs,
            )


class Chatbot:
    """AI-powered chatbot with vector store context."""

    def __init__(
        self,
        vector_store_id: Optional[str] = None,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        max_context_results: int = 5,
        verbose: bool = False,
    ):
        """Initialize the Chatbot."""
        load_dotenv()

        self.searcher = VectorStoreSearcher(
            vector_store_id=vector_store_id, api_key=api_key, verbose=verbose
        )

        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.max_context_results = max_context_results
        self.conversation_history = []
        self.verbose = verbose

    def chat(self, user_message: str, use_vector_context: bool = True) -> str:
        """Send a message and get AI response."""
        context_docs = []

        if use_vector_context:
            if self.verbose:
                print("[*] Searching vector store...")

            old_stdout = sys.stdout
            if not self.verbose:
                sys.stdout = open(os.devnull, "w")

            try:
                context_docs = self.searcher.search(
                    query=user_message, max_num_results=self.max_context_results
                )
            finally:
                if not self.verbose:
                    sys.stdout = old_stdout

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_message, context_docs)

        if self.verbose:
            print(f"[*] Calling {self.model}...")

        ai_response = self._call_llm(system_prompt, user_prompt)

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        return ai_response

    def _build_system_prompt(self) -> str:
        """Build system prompt for the LLM."""
        return """You are a helpful AI assistant with access to a product database.

Your responsibilities:
1. Answer user questions based on the provided context
2. Be accurate and cite sources when possible
3. If information is not in the context, say so clearly
4. Be concise but informative
5. Use Vietnamese for Vietnamese queries, English for English queries

Guidelines:
- Always prioritize information from the context documents  
- Mention product names, prices, and specifications accurately
- If comparing products, be objective
- Use bullet points for clarity when listing multiple items
"""

    def _build_user_prompt(
        self, user_message: str, context_docs: List[Dict[str, Any]]
    ) -> str:
        """Build user prompt with context."""
        if not context_docs:
            return user_message

        context_text = "CONTEXT DOCUMENTS:\n\n"

        for idx, doc in enumerate(context_docs, 1):
            context_text += f"[Document {idx}] (Relevance: {doc['score']:.2f})\n"
            context_text += f"Source: {doc['filename']}\n"
            context_text += f"Content: {doc['content']}\n\n"

        full_prompt = f"""{context_text}

USER QUESTION:
{user_message}

Please answer based on the context documents provided above. If the context doesn't contain relevant information, let the user know."""

        return full_prompt

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM to generate response."""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            if len(self.conversation_history) > 0:
                recent_history = self.conversation_history[-6:]
                messages = (
                    [{"role": "system", "content": system_prompt}]
                    + recent_history
                    + [{"role": "user", "content": user_prompt}]
                )

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"[ERROR] {str(e)}"

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history

    def set_model(self, model: str) -> None:
        """Change LLM model."""
        self.model = model


def print_welcome():
    """Print welcome message."""
    print("\n" + "=" * 70)
    print("AI Chatbot - Vector Store Powered")
    print("=" * 70)
    print("\nCommands:")
    print("  /help     - Show this help message")
    print("  /clear    - Clear conversation history")
    print("  /model    - Change AI model")
    print("  /delete   - Delete vector store and files")
    print("  /exit     - Exit chatbot")
    print("\n" + "=" * 70 + "\n")


def print_help():
    """Print help message."""
    print("\n[HELP] Available Commands:")
    print("  /help     - Show this help message")
    print("  /clear    - Clear conversation history")
    print("  /model    - Change AI model (gpt-4o, gpt-4o-mini)")
    print(
        "  /delete   - Delete all vector stores and files (WARNING: Cannot be undone)"
    )
    print("  /exit     - Exit the chatbot")
    print("\n[TIP] Usage Tips:")
    print("  * Ask questions in natural language")
    print("  * The chatbot searches the product database automatically")
    print("  * Conversation history is maintained for context\n")


def main():
    """Interactive chatbot loop with clean UX."""
    print_welcome()

    try:
        print("[*] Initializing chatbot...")
        chatbot = Chatbot(model="gpt-4o", verbose=False)
        print("[OK] Ready! Start chatting...\n")

        while True:
            try:
                user_input = input("User: ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    command = user_input.lower()

                    if command in ["/exit", "/quit", "/q"]:
                        print("\nGoodbye! Thanks for chatting.\n")
                        break

                    elif command == "/help":
                        print_help()
                        continue

                    elif command == "/clear":
                        chatbot.clear_history()
                        print("[OK] Conversation history cleared\n")
                        continue

                    elif command == "/model":
                        print("\n[MODELS] Available models:")
                        print("  1. gpt-4o       (Best quality, slower)")
                        print("  2. gpt-4o-mini  (Fast, cheaper)")
                        choice = input("\nSelect (1 or 2): ").strip()

                        if choice == "1":
                            chatbot.set_model("gpt-4o")
                            print("[OK] Model changed to: gpt-4o\n")
                        elif choice == "2":
                            chatbot.set_model("gpt-4o-mini")
                            print("[OK] Model changed to: gpt-4o-mini\n")
                        else:
                            print("[ERROR] Invalid choice\n")
                        continue

                    elif command == "/delete":
                        print("\n" + "=" * 60)
                        print("⚠️  WARNING: DELETE ALL RESOURCES")
                        print("=" * 60)
                        print("This will permanently delete:")
                        print("  • Vector store")
                        print("  • All uploaded files")
                        print("  • Local ID file")
                        print("\n⚠️  This action CANNOT be undone!\n")

                        confirmation = input("Type 'DELETE' to confirm: ").strip()

                        if confirmation != "DELETE":
                            print("\n[OK] Deletion cancelled\n")
                            continue

                        try:
                            print()
                            deleter = VectorStoreDeleter(verbose=True)
                            success = deleter.delete_all()

                            if success:
                                print("\n✅ All resources deleted successfully")
                                print(
                                    "[INFO] You'll need to rebuild the vector store to continue chatting\n"
                                )
                            else:
                                print("\n⚠️  Some errors occurred during deletion\n")
                        except Exception as e:
                            print(f"\n[ERROR] Failed to delete: {e}\n")

                        continue

                    else:
                        print(f"[ERROR] Unknown command: {command}")
                        print("        Type /help for available commands\n")
                        continue

                response = chatbot.chat(user_input)
                safe_print(f"\nChatbot: {response}\n")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type /exit to quit properly.\n")
                continue

            except Exception as e:
                print(f"\n[ERROR] {str(e)}\n")
                continue

    except Exception as e:
        print(f"\n[FATAL] {str(e)}")
        print("Please check your API key and try again.\n")


if __name__ == "__main__":
    main()
