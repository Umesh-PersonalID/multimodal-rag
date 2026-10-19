"""
Test script to verify that the RAG backend setup is working correctly.
Run this after completing the setup steps.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def print_banner():
    """Print a clean header for the setup check."""
    print("=" * 72)
    print(" RAG Backend Setup Verification")
    print("=" * 72)


def print_step(number, title):
    """Print a section title with consistent formatting."""
    print(f"\n[{number}] {title}")


async def test_setup():
    """Run the end-to-end verification steps for the RAG setup."""
    print_banner()

    try:
        print_step(1, "Testing imports")
        from app.core.config import get_settings
        from app.core.database import db
        from app.services.rag import rag_service
        print("  OK  All modules imported successfully")

        print_step(2, "Testing configuration")
        settings = get_settings()

        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ]
        if settings.ai_provider == "gemini":
            required_vars.append("GEMINI_API_KEY")
        elif settings.ai_provider == "openai":
            required_vars.append("OPENAI_API_KEY")

        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or value == f"your_{var.lower()}_here":
                missing_vars.append(var)

        if missing_vars:
            print(f"  ERROR  Missing environment variables: {', '.join(missing_vars)}")
            print("  Please update your .env file with real API keys.")
            return False

        print("  OK  Environment variables configured")

        if settings.ai_provider == "gemini":
            print(f"  Using embedding model: {settings.gemini_embed_model}")
            print(f"  Using chat model: {settings.gemini_chat_model}")
        else:
            print(f"  Using embedding model: {settings.openai_embed_model}")
            print(f"  Using chat model: {settings.openai_chat_model}")

        print(f"  Using AI provider: {settings.ai_provider}")

        print_step(3, "Testing database connection")
        await db.connect()
        health = await db.health_check()

        if not health:
            print("  ERROR  Database connection failed")
            print("  Check your Supabase credentials and ensure the project is active.")
            return False

        print("  OK  Database connection successful")

        print_step(4, "Testing database schema")
        await db.initialize_schema()
        print("  OK  Database schema validated")

        print_step(5, "Testing document seeding")
        inserted_count = await rag_service.seed_documents()

        if inserted_count == 0:
            print("  No new documents inserted (this may be expected if the data already exists)")
        else:
            print(f"  OK  Successfully seeded {inserted_count} document chunks")

        print_step(6, "Testing RAG query")
        test_query = "Can I return shoes after 30 days?"
        result = await rag_service.answer_query(test_query)

        if not result.get("text") or "error" in result["text"].lower():
            print("  ERROR  RAG query failed")
            print(f"  Response: {result.get('text', '')[:100]}...")
            return False

        print("  OK  RAG query successful")
        print(f"  Answer: {result['text'][:100]}...")
        print(f"  Citations: {result['citations']}")
        print(f"  Latency: {result['debug']['latency_ms']}ms")

        await db.disconnect()

        print("\n" + "=" * 72)
        print(" ALL TESTS PASSED")
        print("=" * 72)
        print(" Your RAG backend is fully functional.")
        print(" You can now start the server with: uvicorn main:app --reload --port 8000")
        print(" Visit http://localhost:8000/docs for interactive API documentation.")
        return True

    except ImportError as exc:
        print(f"  ERROR  Import error: {exc}")
        print("  Make sure you've installed dependencies: pip install -r requirements.txt")
        return False

    except Exception as exc:
        print(f"  ERROR  Setup test failed: {exc}")
        print("  Check the error message above and refer to QUICKSTART.md")
        return False


async def main():
    """Run the setup verification script."""
    print("This will test the complete setup without starting the server.\n")

    from dotenv import load_dotenv

    load_dotenv()

    success = await test_setup()

    if success:
        print("\nNext steps:")
        print("  1. Start the server: uvicorn main:app --reload --port 8000")
        print("  2. Test the health endpoint: curl http://localhost:8000/healthz")
        print(
            "  3. Ask a question: curl -X POST http://localhost:8000/answer -H "
            "'Content-Type: application/json' -d '{\"query\":\"What is your return policy?\"}'"
        )
        print("  4. Visit the interactive docs: http://localhost:8000/docs")
        sys.exit(0)

    print("\nSetup incomplete. Please fix the issues above and try again.")
    print("Refer to QUICKSTART.md for detailed setup instructions.")
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
