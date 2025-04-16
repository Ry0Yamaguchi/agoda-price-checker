# scrape_prices.py
import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# ★ 本番用 APIキー
SCRAPERAPI_KEY = "5cb364f033d6fa47cbccf3d48074ce0f"

# 比較対象の国（国名 → 国コード）
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

def main():
    for fname in os.listdir("cache"):
        fpath = os.path.join("cache", fname)
        with open(fpath, "r") as f:
            data = json.load(f)

        if not data.get("is_pending"):
            continue

        hotel = data.get("hotel")
        checkin = data.get("check_in")
        checkout = data.get("check_out")
        guests = data.get("guest_count", 1)

        print(f"🔍 {hotel} の価格取得中...")

        result = {
            "hotel": hotel,
            "check_in": checkin,
            "check_out": checkout,
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

        with open(fpath, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ 完了: {fname}")

if __name__ == "__main__":
    main()
