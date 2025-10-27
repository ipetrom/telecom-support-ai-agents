import sys
from pathlib import Path

# Dodaj parent directory do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from retriever.build_vectorstore import build_embedder

embedded = build_embedder()
text = "How to reset the router to factory settings?"
embedding = embedded.embed_query(text)

print(f'"{text}" → embedding with {len(embedding)} dimensions: {embedding[:5]}')  # Show first 5 dimensions