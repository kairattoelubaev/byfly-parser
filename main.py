import requests
from bs4 import BeautifulSoup
import os

# НАСТРОЙКИ
MAX_PRICE = 1000000 
TARGET_COUNTRIES = ["Вьетнам", "Китай", "Турция"]
URL = "https://byfly-shop.com/e5831fa5-d153-4418-8de1-630d748aed62"

def check_tours():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем все текстовые блоки (на таких сайтах туры часто в блоках div или span)
        found_items = []
        
        # Этот цикл ищет упоминание отелей и цен в тексте
        # Мы ищем строки, где есть название страны и цифры цены
        all_text = soup.get_text(separator='|', strip=True).split('|')
        
        current_hotel = ""
        for text in all_text:
            # Если текст похож на отель (обычно содержит звезды или слова Hotel/Resort)
            if any(country in text for country in TARGET_COUNTRIES):
                current_hotel = text
            
            # Если видим цену (цифры + тг/KZT) рядом с отелем
            if ("тг" in text or "KZT" in text) and current_hotel:
                # Очищаем цену от лишних символов, чтобы сравнить с лимитом
                price_digits = ''.join(filter(str.isdigit, text))
                if price_digits and int(price_digits) <= MAX_PRICE:
                    found_items.append(f"🏨 {current_hotel}\n💰 Цена: {text}")
                    current_hotel = "" # Сбрасываем для поиска следующего

        if found_items:
            message = "🌟 **Список найденных отелей:**\n\n" + "\n\n".join(found_items[:10])
            message += f"\n\n🔗 Ссылка на подборку: {URL}"
            send_telegram(token, chat_id, message)
        else:
            # Если парсер не смог выделить отели, пришлем общую инфу как раньше
            send_telegram(token, chat_id, f"✅ Туры найдены, но детальный список отелей не считался.\nПроверьте вручную: {URL}")

    except Exception as e:
        print(f"Ошибка: {e}")

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_tours()
