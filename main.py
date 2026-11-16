import os
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

# Подключение к Timeweb Cloud
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.timeweb.ai/v1"
)

@app.post("/")
async def main(request: Request):
    body = await request.json()
    
    req_data = body.get("request", {})
    user_text = req_data.get("original_utterance") or req_data.get("command", "Привет")
    
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-v4-flash",  # Идентификатор модели из панели Timeweb
            messages=[{"role": "user", "content": user_text}],
            timeout=4
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Ошибка: {str(e)}"

    return {
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {
            "end_session": False,
            "text": answer
        }
    }
