
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"


def ask_ai(question):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are an IT support engineer. Explain technical problems clearly and provide practical troubleshooting steps."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()
        answer = result["message"]["content"]

        return answer

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure Ollama is running."

    except requests.exceptions.Timeout:
        return "Error: The AI model took too long to respond."

    except requests.exceptions.RequestException as error:
        return f"API Error: {error}"


if __name__ == "__main__":
    print("===== AI IT SUPPORT AGENT =====")

    user_question = input("\nDescribe your IT problem: ")

    print("\nAI is analyzing your problem...\n")

    answer = ask_ai(user_question)

    print("===== AI RESPONSE =====")
    print(answer)
