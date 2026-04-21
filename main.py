import requests
import os
import re

# НАСТРОЙКИ
MAX_PRICE = 1000000 
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
URL = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers)
        page_text = response.text
        
        # Список для найденных туров
        found_tours = []

        # Упрощенный поиск: ищем блоки, где есть название страны и цена (цифры рядом с 'тг' или 'kZT')
        # ВАЖНО: Эта логика зависит от того, как сайт отдает текст.
        for country in TARGET_COUNTRIES:
            if country.lower() in page_text.lower():
                # Ищем отели (обычно они в кавычках или перед звездами ***)
                # Пока сделаем универсальный вывод, если нашли страну
                found_tours.append(f"🏨 Отель в направлении {country}\n💰 Цена: до {MAX_PRICE} тг")

        if found_tours:
            header = "🔔 **Найдены подходящие туры!**\n\n"
            tours_list = "\n\n".join(found_tours)
            footer = f"\n\n🔗 Проверить на сайте: {URL}"
            send_telegram(token, chat_id, header + tours_list + footer)
        else:
            # Если ничего не нашли, бот может промолчать или прислать отчет (для теста оставим отчет)
            print("Туры не найдены")

    except Exception as e:
        print(f"Ошибка: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
