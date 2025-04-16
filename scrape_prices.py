
import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

SCRAPERAPI_KEY = "5cb364f033d6fa47cbccf3d48074ce0f"

TARGET_COUNTRIES = {
    "Japan": "JP",
    "Thailand": "TH",
    "India": "IN",
    "United States": "US"
}

def get_agoda_url(hotel_name, checkin, checkout, guests):
    return f"https://www.agoda.com/Search?checkIn={checkin}&checkOut={checkout}&rooms=1&adults={guests}&children=0&text={quote(hotel_name)}"

def fetch_price_from_agoda(url, country_code):
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&country_code={country_code}&url={quote(url)}"
    try:
        response = requests.get(api_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find('span', {'data-selenium': 'price'})
        if price_tag:
            price_text = price_tag.get_text(strip=True).replace(',', '').replace('¥', '')
            price_value = int(''.join(filter(str.isdigit, price_text)))
            return price_value
        else:
            print(f"[{country_code}] 価格情報が見つかりません")
            return None
    except Exception as e:
        print(f"[{country_code}] 取得失敗: {e}")
        return None

def process_single_request(hotel, checkin, checkout, guests, fpath):
    result = {
        "hotel": hotel,
        "check_in": str(checkin),
        "check_out": str(checkout),
        "guest_count": guests,
        "updated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "prices": []
    }

    for country, code in TARGET_COUNTRIES.items():
        agoda_url = get_agoda_url(hotel, checkin, checkout, guests)
        price = fetch_price_from_agoda(agoda_url, code)
        if price:
            result["prices"].append({
                "country": country,
                "price": price,
                "currency": "local",
                "url": agoda_url + "&cid=XXXX"
            })

    result["prices"].sort(key=lambda x: x["price"])
    result["is_pending"] = False

    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
