import requests
from bs4 import BeautifulSoup
import os
import re

# НАСТРОЙКИ
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
        
        # Получаем весь текст страницы, разделенный символом |
        all_text = soup.get_text(separator='|', strip=True).split('|')
        
        tours_list = []
        
        # Перебираем блоки текста в поиске стран
        for i, text in enumerate(all_text):
            if any(country in text for country in TARGET_COUNTRIES):
                country_info = text
                
                # Ищем цену в следующих 8 блоках после упоминания страны
                for j in range(1, 9):
                    if i + j < len(all_text):
                        potential_price = all_text[i + j]
                        if "тг" in potential_price or "₸" in potential_price:
                            # Очищаем цену от мусора
                            price_digits = ''.join(filter(str.isdigit, potential_price))
                            if price_digits:
                                price_val = int(price_digits)
                                
                                # ФИЛЬТРАЦИЯ: только до 700 000 тг
                                if price_val <= MAX_PRICE:
                                    # Пытаемся взять название отеля (обычно оно ПЕРЕД страной)
                                    hotel = all_text[i-1] if i > 0 else "Отель по ссылке"
                                    
                                    # Создаем карточку в твоем стиле
                                    card = (
                                        f"{country_info}\n"
                                        f"🏨 {hotel.upper()} | ⭐ 4.5/5\n"
                                        f"🗓 Уточняйте дату | Завтрак\n"
                                        f"🔥 Мест: есть | Цена от {price_val:,} ₸".replace(',', ' ')
                                    )
                                    tours_list.append(card)
                                    break
        
        if tours_list:
            # Убираем дубликаты и берем топ-8
            unique_tours = list(dict.fromkeys(tours_list))[:8]
            
            final_msg = "✈️ **Вылет из Астана (на 2-х взрослых)**\n\n"
            final_msg += "\n\n".join(unique_tours)
            final_msg += f"\n\n📲 **БРОНИРОВАНИЕ:** +7 747 257 43 40\n"
            final_msg += "⚠️ Не является офертой (ст. 395 ГК РК). Цены актуальны на момент публикации."
            
            send_telegram(token, chat_id, final_msg)
        else:
            print(f"Туров дешевле {MAX_PRICE} тг не обнаружено.")

    except Exception as e:
        print(f"Ошибка парсинга: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
