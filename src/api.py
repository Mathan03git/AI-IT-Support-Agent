
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
import requests

from src.rag_assistant import (
    retrieve_context,
    generate_answer,
    analyze_log_file
)

from src.database import (
    init_db,
    save_conversation,
    get_conversations,
    save_log_analysis,
    get_log_analyses
)


# ==========================================
# FASTAPI CONFIGURATION
# ==========================================

app = FastAPI(
    title="AI IT Support Agent API",
    description="AI-powered IT troubleshooting and log monitoring system.",
    version="1.2.0"
)

init_db()


# ==========================================
# REQUEST MODEL
# ==========================================

class QuestionRequest(BaseModel):

    question: str = Field(
        min_length=3,
        max_length=1000
    )


# ==========================================
# HOME ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {
        "message": "AI IT Support Agent API is running!",
        "status": "active"
    }


# ==========================================
# ASK IT SUPPORT QUESTION
# ==========================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    try:

        question = request.question

        results = retrieve_context(
            question,
            top_k=3
        )

        if not results or results[0]["score"] < 0.30:

            return {
                "question": question,
                "answer": "Sorry, I couldn't find sufficiently relevant information in the knowledge base.",
                "retrieved_documents": [],
                "message": "No relevant knowledge found."
            }

        context = "\n\n".join(
            result["document"]
            for result in results
        )

        answer = generate_answer(
            question,
            context
        )

        save_conversation(
            question,
            answer
        )

        return {
            "question": question,
            "answer": answer,
            "retrieved_documents": [
                {
                    "document": result["document"],
                    "similarity_score": round(
                        result["score"],
                        2
                    )
                }
                for result in results
            ],
            "message": "Conversation saved successfully."
        }

    except requests.exceptions.RequestException as error:

        raise HTTPException(
            status_code=502,
            detail=f"Ollama API error: {error}"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to process question: {error}"
        )


# ==========================================
# AI LOG FILE ANALYZER
# ==========================================

@app.post("/analyze-log")
async def analyze_log(
    uploaded_file: UploadFile = File(...)
):

    try:

        filename = uploaded_file.filename or ""

        if not filename.lower().endswith((".log", ".txt")):

            raise HTTPException(
                status_code=400,
                detail="Only .log and .txt files are supported."
            )

        content = await uploaded_file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        if len(content) > 2 * 1024 * 1024:

            raise HTTPException(
                status_code=413,
                detail="File must be 2 MB or smaller."
            )

        log_content = content.decode(
            "utf-8",
            errors="replace"
        )

        # Count log severity levels
        lines = log_content.splitlines()

        error_count = sum(
            "ERROR" in line.upper()
            for line in lines
        )

        warning_count = sum(
            "WARNING" in line.upper()
            for line in lines
        )

        info_count = sum(
            "INFO" in line.upper()
            for line in lines
        )

        # Generate AI analysis
        analysis = analyze_log_file(log_content)

        # Save successful analysis in SQLite
        save_log_analysis(
            filename,
            analysis,
            error_count,
            warning_count,
            info_count
        )

        return {
            "filename": filename,
            "analysis": analysis,
            "statistics": {
                "errors": error_count,
                "warnings": warning_count,
                "info": info_count
            },
            "message": "Log file analyzed and saved successfully."
        }

    except HTTPException:
        raise

    except requests.exceptions.RequestException as error:

        raise HTTPException(
            status_code=502,
            detail=f"Ollama API error: {error}"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to analyze log file: {error}"
        )

    finally:

        await uploaded_file.close()


# ==========================================
# LOG ANALYSIS HISTORY
# ==========================================

@app.get("/log-history")
def log_analysis_history():

    try:

        analyses = get_log_analyses()

        return {
            "total_analyses": len(analyses),
            "history": analyses
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve log history: {error}"
        )


# ==========================================
# CONVERSATION HISTORY
# ==========================================

@app.get("/history")
def conversation_history():

    try:

        conversations = get_conversations()

        return {
            "total_conversations": len(conversations),
            "history": conversations
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve history: {error}"
        )



