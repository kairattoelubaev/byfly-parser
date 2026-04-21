import requests
import os

# НАСТРОЙКИ
MAX_PRICE = 700000 
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
# Прямая ссылка на API, которую ты нашел
API_URL = "https://byfly-shop.com/api/list_start.php"
ORIGINAL_PAGE = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': ORIGINAL_PAGE
    }
    
    try:
        # Запрашиваем данные напрямую у API
        response = requests.get(API_URL, headers=headers)
        data = response.json() # API обычно возвращает JSON
        
        found_tours = []
        
        # Перебираем туры из полученных данных
        # Структура API ByFly обычно содержит список в ключе 'tours' или 'items'
        tours = data.get('tours', data.get('items', []))
        
        # Если API отдал данные не списком, а строкой или иначе, 
        # мы все равно попробуем найти в них туры
        if not tours and isinstance(data, list):
            tours = data

        for tour in tours:
            country = tour.get('country', '')
            price = int(str(tour.get('price', '0')).replace(' ', ''))
            hotel = tour.get('hotel_name', tour.get('name', 'Отель по ссылке'))
            stars = tour.get('stars', '4')
            rating = tour.get('rating', '4.5')
            date = tour.get('date', 'Уточняйте')
            nights = tour.get('nights', '7')

            # ПРОВЕРКА ФИЛЬТРОВ
            if any(c in country for c in TARGET_COUNTRIES) and price <= MAX_PRICE:
                card = (
                    f"{country}\n"
                    f"🏨 {hotel.upper()} ({stars}*) | ⭐ {rating}/5\n"
                    f"🗓 {date} ({nights} ночей) | Завтрак\n"
                    f"🔥 Мест: есть | Цена от {price:,} ₸".replace(',', ' ')
                )
                found_tours.append(card)

        if found_tours:
            header = "✈️ **Вылет из Астана (на 2-х взрослых)**\n\n"
            footer = (
                f"\n\n📲 **БРОНИРОВАНИЕ:** +7 747 257 43 40\n"
                f"⚠️ Не является офертой (ст. 395 ГК РК). Цены актуальны на момент публикации."
            )
            
            # Собираем сообщение (не более 10 туров, чтобы влезло в лимит Telegram)
            final_msg = header + "\n\n".join(found_tours[:10]) + footer
            send_telegram(token, chat_id, final_msg)
        else:
            print(f"Пока нет туров до {MAX_PRICE} тг в {', '.join(TARGET_COUNTRIES)}")

    except Exception as e:
        print(f"Ошибка при работе с API: {e}")

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
