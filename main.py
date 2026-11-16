import os
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

# Инициализируем клиент OpenAI для работы с Timeweb Cloud
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.timeweb.ai/v1"  # Базовый URL из документации Timeweb
)

@app.post("/")
async def main(request: Request):
    body = await request.json()
    
    # 1. Безопасно извлекаем текст вопроса от Алисы
    req_data = body.get("request", {})
    user_text = req_data.get("original_utterance") or req_data.get("command", "Привет")
    
    # 2. Отправляем запрос через официальную библиотеку
    try:
        # Используем модель, которую вы создали в Timeweb Cloud
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",  # или "deepseek/deepseek-v4-flash"
            messages=[{"role": "user", "content": user_text}],
            timeout=4  # Алиса ждёт 4.5 секунды, ставим 4 для запаса
        )
        answer = response.choices[0].message.content
    except Exception as e:
        # Если произошла ошибка, выводим её текст в ответе для диагностики
        answer = f"Ошибка: {str(e)}"

    # 3. Отдаём ответ Алисе в правильном формате
    return {
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {
            "end_session": False,
            "text": answer
        }
    }
