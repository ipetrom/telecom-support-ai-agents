import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from retriever.retriever import KBRetriever, RetrieverConfig


def test_retriever():
    """Testing the retriever with sample queries"""
    
    print("📁 Loading retriever...")
    cfg = RetrieverConfig(artifacts_dir=Path("artifacts"))
    retriever = KBRetriever(cfg)
    print("✅ Retriever loaded\n")

    # Sample queries
    queries = [
        "How do I enable bridge mode on the ONT and use my own router?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print(f"{'='*60}")

        # Perform retrieval
        result = retriever.retrieve(query)

        # Display results
        if result["no_context"]:
            print("⚠️  NO_CONTEXT - documentation does not cover this topic")
        else:
            print(f"✅ Found {len(result['docs'])} documents\n")

            # Wyświetl każdy dokument, pobierając metadane przez funkcje retriever jeśli dostępne
            for j, doc in enumerate(result["docs"], 1):
                score = result["scores"][j-1] if j-1 < len(result["scores"]) else 0
                
                # Pobierz metadane z dokumentu
                meta = doc.metadata or {}
                
                # Wyodrębnij czytelne dane
                title = meta.get("title", "Unknown")
                section_path = meta.get("section_path", [])
                section = " > ".join(section_path) if section_path else "Unknown"
                file_path = Path(meta.get("path", "unknown")).name
                content = doc.page_content[:150]

                print(f"\n📄 Document {j} (score: {score:.4f}):")
                print(f"   File: {file_path}")
                print(f"   Title: {title}")
                print(f"   Section: {section}")
                print(f"   Content: {content}...")

        print()


if __name__ == "__main__":
    test_retriever()