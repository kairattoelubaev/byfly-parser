import requests
from bs4 import BeautifulSoup
import os
import re

# НАСТРОЙКИ ФИЛЬТРА
MAX_PRICE = 700000 
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
URL = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Разбиваем текст страницы на блоки по разделителю
        raw_text = soup.get_text(separator='|', strip=True)
        parts = raw_text.split('|')
        
        tours_found = []
        
        for i, text in enumerate(parts):
            # Проверяем, есть ли в текущем блоке страна
            if any(country in text for country in TARGET_COUNTRIES):
                country_info = text
                
                # Ищем цену в радиусе 5 следующих блоков
                for j in range(1, 6):
                    if i + j < len(parts):
                        potential_price = parts[i + j]
                        if "тг" in potential_price or "KZT" in potential_price:
                            # Очищаем цену от пробелов и символов
                            price_val = int(''.join(filter(str.isdigit, potential_price)))
                            
                            # ФИЛЬТРАЦИЯ
                            if price_val <= MAX_PRICE:
                                # Название отеля обычно находится ПЕРЕД страной
                                hotel_name = parts[i-1] if i > 0 else "Отель по ссылке"
                                
                                # Если в названии отеля попал мусор, берем саму страну
                                if len(hotel_name) < 3: hotel_name = country_info
                                
                                card = (
                                    f"{country_info}\n"
                                    f"🏨 {hotel_name.upper()} | ⭐ 4.5/5\n"
                                    f"🗓 Уточняйте дату | Завтрак\n"
                                    f"🔥 Мест: есть | Цена от {price_val:,} ₸".replace(',', ' ')
                                )
                                tours_found.append(card)
                                break

        if tours_found:
            # Убираем дубликаты
            unique_tours = list(dict.fromkeys(tours_found))[:10]
            
            header = "✈️ **Вылет из Астана (на 2-х взрослых)**\n\n"
            footer = (
                f"\n📲 **БРОНИРОВАНИЕ:** +7 747 257 43 40\n"
                f"⚠️ Не является офертой (ст. 395 ГК РК). Цены актуальны на момент публикации."
            )
            
            final_msg = header + "\n\n".join(unique_tours) + footer
            send_telegram(token, chat_id, final_msg)
        else:
            print(f"На данный момент туров дешевле {MAX_PRICE} тг не найдено.")

    except Exception as e:
        print(f"Ошибка парсинга: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
