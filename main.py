import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

# Адрес API Timeweb Cloud (с добавленным /chat/completions)
API_URL = "https://api.timeweb.ai/v1/chat/completions"
# Ключ берется из настроек Render (переменная DEEPSEEK_API_KEY)
API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    
    # 1. Безопасно извлекаем текст вопроса от Алисы
    # Если original_utterance нет, берем command. Если нет и его - пишем "Привет"
    req_data = body.get("request", {})
    user_text = req_data.get("original_utterance") or req_data.get("command", "Привет")
    
    # 2. Готовим запрос к Timeweb
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-v4-flash",  # Точное имя модели из Timeweb
        "messages": [
            {"role": "user", "content": user_text}
        ]
    }

    # 3. Отправляем запрос и обрабатываем ответ
    try:
        # Ставим таймаут 4 секунды (Алиса дает 4.5 сек на ответ)
        response = requests.post(API_URL, headers=headers, json=payload, timeout=4)
        response.raise_for_status() # Проверяем на ошибки сервера
        answer = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        # Если Timeweb не ответил или произошла ошибка - Алиса скажет эту фразу
        answer = "Извините, нейросеть временно недоступна. Попробуйте позже."

    # 4. Отдаем ответ Алисе в правильном формате
    return {
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {
            "end_session": False,
            "text": answer
        }
    }
