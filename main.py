import os
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

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
        # Пытаемся использовать самое вероятное имя из документации
        response = client.chat.completions.create(
            model="deepseek/deepseek-v4.1-flash", 
            messages=[{"role": "user", "content": user_text}],
            timeout=4
        )
        answer = response.choices[0].message.content
    except Exception as e:
        # Если модель не найдена — показываем список доступных
        try:
            models = client.models.list()
            model_ids = [m.id for m in models.data]
            # Ищем все модели, в названии которых есть deepseek
            deepseek_models = [mid for mid in model_ids if "deepseek" in mid.lower()]
            answer = f"Ошибка: {str(e)}. Доступные модели DeepSeek: {deepseek_models}"
        except Exception as list_err:
            answer = f"Ошибка: {str(e)}. Не удалось получить список моделей: {list_err}"

    return {
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {"end_session": False, "text": answer}
    }
