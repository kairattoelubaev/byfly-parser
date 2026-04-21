import requests
from bs4 import BeautifulSoup
import os
import re

# НОВЫЕ НАСТРОЙКИ
MAX_PRICE = 700000  # Бюджет изменен на 700к
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
URL = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        found_tours = []
        # Ищем все блоки текста
        all_text = soup.get_text(separator='|', strip=True).split('|')
        
        current_hotel = ""
        for i, text in enumerate(all_text):
            # Проверяем страны
            if any(country in text for country in TARGET_COUNTRIES):
                current_hotel = text
            
            # Ищем цену рядом с отелем
            if ("тг" in text or "KZT" in text) and current_hotel:
                price_digits = ''.join(filter(str.isdigit, text))
                if price_digits:
                    price_val = int(price_digits)
                    if price_val <= MAX_PRICE:
                        found_tours.append(f"🏨 {current_hotel}\n💰 Цена: {text}")
                        current_hotel = "" # Сброс для следующего поиска

        if found_tours:
            unique_tours = list(set(found_tours))[:10]
            msg = f"🔥 **Горящие туры до {MAX_PRICE} тг!**\n\n" + "\n\n".join(unique_tours)
            msg += f"\n\n🔗 [Открыть подборку]({URL})"
            send_telegram(token, chat_id, msg)
        else:
            print("Туров по такой цене пока нет.")

    except Exception as e:
        print(f"Ошибка: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
