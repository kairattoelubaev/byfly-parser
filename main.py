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
        
        # Берем весь текст и чистим его от лишних пробелов
        text_data = soup.get_text(separator='|', strip=True)
        blocks = text_data.split('|')
        
        final_tours = []
        
        # Проходим по всем блокам текста в поиске стран и цен
        for i, item in enumerate(blocks):
            # Если нашли одну из стран
            if any(country in item for country in TARGET_COUNTRIES):
                country_name = item
                
                # Ищем цену в ближайших 10 блоках после страны
                for j in range(1, 11):
                    if i + j < len(blocks):
                        val = blocks[i + j]
                        if "тг" in val or "KZT" in val:
                            price_raw = ''.join(filter(str.isdigit, val))
                            if price_raw:
                                price_val = int(price_raw)
                                
                                # ФИЛЬТРАЦИЯ ПО БЮДЖЕТУ
                                if price_val <= MAX_PRICE:
                                    # Название отеля обычно идет ПЕРЕД страной
                                    hotel = blocks[i-1] if i > 0 else "Отель уточняйте"
                                    
                                    # Собираем карточку по твоему формату
                                    card = (
                                        f"{country_name}\n"
                                        f"🏨 {hotel.upper()} | ⭐ 4.5/5\n"
                                        f"🗓 По запросу | Завтрак\n"
                                        f"🔥 Мест: есть | Цена от {price_val:,} ₸".replace(',', ' ')
                                    )
                                    final_tours.append(card)
                                    break
        
        if final_tours:
            # Убираем дубликаты
            unique_list = list(dict.fromkeys(final_tours))[:10]
            
            message = "✈️ **Вылет из Астана (на 2-х взрослых)**\n\n"
            message += "\n\n".join(unique_list)
            message += f"\n\n📲 **БРОНИРОВАНИЕ:** +7 747 257 43 40\n"
            message += "⚠️ Не является офертой (ст. 395 ГК РК). Цены актуальны на момент публикации."
            
            send_telegram(token, chat_id, message)
        else:
            # Если ничего не нашли под 700к, бот просто промолчит (Success в логах)
            print(f"Туров до {MAX_PRICE} тг не найдено.")

    except Exception as e:
        print(f"Ошибка: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
