import requests
import os

# НАСТРОЙКИ
MAX_PRICE = 1000000 
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
URL = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(URL, headers=headers)
        page_text = response.text.lower()
        
        # Ищем совпадения по странам
        found = [c for c in TARGET_COUNTRIES if c.lower() in page_text]
        
        if found:
            msg = f"🌟 **Найдены варианты!**\n\n🌍 Страны: {', '.join(found)}\n💰 Бюджет: до {MAX_PRICE} тг\n📍 Вылет: Астана/Алматы\n🔗 Ссылка: {URL}"
            send_telegram(token, chat_id, msg)
    except Exception as e:
        print(f"Ошибка: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
