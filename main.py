import requests
import os

# Настройки поиска (можете менять под себя)
MAX_PRICE = 200000  # Максимальная цена в тенге
TARGET_COUNTRY = "Турция"
URL = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62" # Ваша ссылка

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Имитируем запрос браузера
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    
    # Здесь логика поиска по тексту страницы (упрощенная)
    # Если на странице находим цену ниже лимита:
    found_tours = [] 
    
    # Для примера: если в тексте страницы есть цена и страна
    if TARGET_COUNTRY.lower() in response.text.lower():
        # Тут должна быть логика извлечения цены (зависит от верстки)
        # Если нашли подходящий тур:
        msg = f"🚀 Нашел выгодный тур в {TARGET_COUNTRY} до {MAX_PRICE} тг!\nПроверь тут: {URL}"
        send_telegram(token, chat_id, msg)

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
