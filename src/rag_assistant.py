
from pathlib import Path
from functools import lru_cache

import requests
from sentence_transformers import SentenceTransformer, util


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_FILE = PROJECT_DIR / "data" / "knowledge_base.txt"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"


# ==========================================
# LOAD KNOWLEDGE BASE AND EMBEDDING MODEL
# ==========================================

@lru_cache(maxsize=1)
def load_resources():

    print("Loading knowledge base...")

    with KNOWLEDGE_FILE.open("r", encoding="utf-8") as file:
        content = file.read()

    documents = [
        doc.strip()
        for doc in content.split("\n\n")
        if doc.strip()
    ]

    if not documents:
        raise ValueError("Knowledge base is empty.")

    print("Loading embedding model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    embeddings = model.encode(
        documents,
        convert_to_tensor=True
    )

    return documents, model, embeddings


# ==========================================
# RETRIEVE RELEVANT KNOWLEDGE
# ==========================================

def retrieve_context(question, top_k=3):

    documents, model, embeddings = load_resources()

    question_embedding = model.encode(
        question,
        convert_to_tensor=True
    )

    scores = util.cos_sim(
        question_embedding,
        embeddings
    )[0]

    top_k = min(top_k, len(documents))

    top_results = scores.topk(top_k)

    retrieved_documents = []

    for score, index in zip(
        top_results.values,
        top_results.indices
    ):

        retrieved_documents.append({
            "document": documents[index.item()],
            "score": score.item()
        })

    return retrieved_documents


# ==========================================
# GENERATE RAG ANSWER USING LLAMA
# ==========================================

def generate_answer(question, context):

    prompt = f"""
You are an experienced IT support engineer.

Use the following knowledge base information
to answer the user's question.

KNOWLEDGE BASE:
{context}

USER QUESTION:
{question}

Instructions:
1. Use the supplied knowledge as your primary source.
2. Give clear, practical troubleshooting steps.
3. Do not invent commands, tools, or technical facts.
4. If the knowledge is insufficient, say so clearly.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    result = response.json()

    return result["message"]["content"]


# ==========================================
# AI-POWERED LOG FILE ANALYSIS
# ==========================================

def analyze_log_file(log_content):

    if not log_content.strip():
        raise ValueError("Uploaded log file is empty.")

    prompt = f"""
You are an experienced IT support engineer.

Analyze the following application log file.

LOG CONTENT:
{log_content}

Provide your analysis using these sections:

1. Overall Summary
2. Errors Found
3. Warnings Found
4. Possible Root Causes
5. Recommended Troubleshooting Steps
6. Prevention Suggestions

Instructions:
- Focus on actual errors and warnings in the log.
- Do not invent error messages.
- Distinguish confirmed findings from possible causes.
- If there are no errors, clearly mention that.
- Give practical troubleshooting suggestions.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=240
    )

    response.raise_for_status()

    result = response.json()

    return result["message"]["content"]


# ==========================================
# MAIN APPLICATION
# ==========================================

if __name__ == "__main__":

    print("===== AI IT SUPPORT AGENT =====")

    question = input("\nDescribe your IT problem: ")

    try:

        print("\nSearching knowledge base...")

        results = retrieve_context(question, top_k=3)

        if not results:
            print("\nNo knowledge documents found.")

        else:

            best_score = results[0]["score"]

            print("\n===== RETRIEVED DOCUMENTS =====")

            for number, result in enumerate(results, start=1):

                print(f"\nDocument {number}")
                print(f"Similarity score: {result['score']:.2f}")
                print(result["document"])

            if best_score < 0.30:

                print("\nNo sufficiently relevant information found.")

            else:

                context = "\n\n".join(
                    result["document"] for result in results
                )

                print("\nGenerating AI response...")

                answer = generate_answer(question, context)

                print("\n===== RAG AI RESPONSE =====")
                print(answer)

    except FileNotFoundError:
        print("Error: Knowledge base file not found.")

    except requests.exceptions.RequestException as error:
        print(f"Ollama API error: {error}")

    except Exception as error:
        print(f"Application error: {error}")





   





