
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# Locate the knowledge base
PROJECT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_FILE = PROJECT_DIR / "data" / "knowledge_base.txt"


def load_documents():
    """Load troubleshooting documents."""

    with KNOWLEDGE_FILE.open("r", encoding="utf-8") as file:
        content = file.read()

    documents = [
        doc.strip()
        for doc in content.split("\n\n")
        if doc.strip()
    ]

    return documents


def semantic_search(query):
    """Find the most relevant troubleshooting document."""

    documents = load_documents()

    if not documents:
        print("No documents found.")
        return

    print("Loading sentence transformer model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    document_embeddings = model.encode(
        documents,
        convert_to_tensor=True
    )

    query_embedding = model.encode(
        query,
        convert_to_tensor=True
    )

    similarity_scores = util.cos_sim(
        query_embedding,
        document_embeddings
    )[0]

    best_index = similarity_scores.argmax().item()

    print("\n===== SEMANTIC SEARCH RESULTS =====")
    print(f"Your question: {query}")
    print(
        f"Similarity score: "
        f"{similarity_scores[best_index].item():.2f}"
    )

    print("\nMost relevant document:")
    print(documents[best_index])


if __name__ == "__main__":

    user_query = input("Enter your IT problem: ")

    semantic_search(user_query)


