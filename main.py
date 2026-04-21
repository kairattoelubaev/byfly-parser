import requests
import os
import json

# НАСТРОЙКИ
MAX_PRICE = 700000 
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
# Мы будем искать данные во всем коде страницы, так как они зашиты в JS-объекты
URL = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    
    try:
        response = requests.get(URL, headers=headers)
        html = response.text
        
        # Ищем блоки данных, которые обычно начинаются после определенных ключевых слов
        # На таких сайтах туры часто лежат в переменной window.__DATA__ или внутри тегов <script>
        found_tours = []
        
        # Метод: Поиск по регулярным выражениям названий стран и цен рядом с ними
        import re
        
        # Ищем паттерны: Название отеля (много букв) + Страна + Цена
        # Это более надежный способ для динамических сайтов
        pattern = r'([^|]{5,50}?(?:' + '|'.join(TARGET_COUNTRIES) + r')[^|]{0,100}?)(\d[\d\s]{4,7})\s?(?:тг|₸|KZT)'
        
        matches = re.findall(pattern, html)
        
        for match in matches:
            description = match[0].strip()
            price_raw = match[1].replace(' ', '').replace('\xa0', '')
            price_val = int(price_raw)
            
            if price_val <= MAX_PRICE:
                # Определяем страну для красоты
                country_tag = "🌍 Тур"
                for c in TARGET_COUNTRIES:
                    if c in description:
                        country_tag = c
                
                card = (
                    f"{country_tag}\n"
                    f"🏨 {description[:50].upper()}...\n"
                    f"🗓 Уточняйте дату | Завтрак\n"
                    f"🔥 Мест: есть | Цена от {price_val:,} ₸".replace(',', ' ')
                )
                found_tours.append(card)

        if found_tours:
            unique_tours = list(dict.fromkeys(found_tours))[:10]
            header = "✈️ **Вылет из Астана (на 2-х взрослых)**\n\n"
            footer = (
                f"\n📲 **БРОНИРОВАНИЕ:** +7 747 257 43 40\n"
                f"⚠️ Не является офертой (ст. 395 ГК РК). Цены актуальны на момент публикации."
            )
            send_telegram(token, chat_id, header + "\n\n".join(unique_tours) + footer)
        else:
            # Если ничего не нашли, попробуем отправить уведомление о проверке, но без "заглушки"
            print("Конкретные отели до 700к не найдены в коде страницы.")

    except Exception as e:
        print(f"Ошибка: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
