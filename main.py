import requests
import os
import re

# НАСТРОЙКИ
MAX_PRICE = 700000 
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
# Ссылка на API, которую мы нашли
API_URL = "https://byfly-shop.com/api/list_start.php"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Очень важные заголовки, чтобы сайт думал, что мы — браузер
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62'
    }

    try:
        # Отправляем запрос к API
        response = requests.get(API_URL, headers=headers)
        
        # Если API выдает ошибку доступа, попробуем через саму страницу
        if response.status_code != 200:
            response = requests.get("https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62", headers=headers)

        text_data = response.text
        
        # Регулярка для поиска туров в сырых данных API
        # Мы ищем связку: Страна + Отель + Цена
        found_tours = []
        
        # Ищем все цены с валютой
        prices = re.findall(r'(\d[\d\s]*)(?:тг|₸|KZT)', text_data)
        
        # Чтобы не усложнять, мы просто поищем куски текста, где есть страна и цена рядом
        blocks = re.split(r'(?i)' + '|'.join(TARGET_COUNTRIES), text_data)
        
        for i in range(1, len(blocks)):
            country = TARGET_COUNTRIES[i-1]
            block = blocks[i][:500] # берем кусок текста после страны
            
            price_match = re.search(r'(\d[\d\s]{4,7})', block)
            if price_match:
                price_raw = price_match.group(1).replace(' ', '').replace('\xa0', '')
                price_val = int(price_raw)
                
                if price_val <= MAX_PRICE:
                    # Пытаемся вытащить что-то похожее на название отеля
                    hotel_match = re.search(r'([A-Z\s]{5,30})', block)
                    hotel_name = hotel_match.group(1).strip() if hotel_match else "HOTEL"

                    card = (
                        f"🌍 {country}\n"
                        f"🏨 {hotel_name.upper()} | ⭐ 4.0/5\n"
                        f"🗓 Уточняйте дату | Завтрак\n"
                        f"🔥 Мест: есть | Цена от {price_val:,} ₸".replace(',', ' ')
                    )
                    found_tours.append(card)

        if found_tours:
            unique_tours = list(dict.fromkeys(found_tours))[:10]
            header = "✈️ **Вылет из Астана (на 2-х взрослых)**\n\n"
            footer = (
                f"\n\n📲 **БРОНИРОВАНИЕ:** +7 747 257 43 40\n"
                f"⚠️ Не является офертой (ст. 395 ГК РК). Цены актуальны на момент публикации."
            )
            send_telegram(token, chat_id, header + "\n\n".join(unique_tours) + footer)
        else:
            print(f"В данных API пока нет туров до {MAX_PRICE} тг.")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
