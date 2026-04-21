import requests
import os

def test_bot():
    # Получаем данные из секретов GitHub
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    message = "🚀 Проверка связи! Если ты видишь это сообщение, значит:\n1. Токен бота верный.\n2. Chat ID верный.\n3. GitHub Actions работает!"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Успех! Сообщение отправлено.")
        else:
            print(f"Ошибка! Ответ сервера: {response.text}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    test_bot()
