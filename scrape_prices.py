import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

SCRAPERAPI_KEY = "5cb364f033d6fa47cbccf3d48074ce0f"

TARGET_COUNTRIES = {
    "Japan": "JP",
    "Thailand": "TH",
    "India": "IN",
    "United States": "US"
}

def modify_url(original_url, checkin, checkout, guests):
    parsed = urlparse(original_url)
    query = parse_qs(parsed.query)
    query["checkIn"] = [str(checkin)]
    query["checkOut"] = [str(checkout)]
    query["adults"] = [str(guests)]
    query["rooms"] = ["1"]
    query["children"] = ["0"]
    new_query = urlencode(query, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

def fetch_price(url, country_code):
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&country_code={country_code}&url={url}"
    try:
        res = requests.get(proxy_url, timeout=20)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.find('span', {'data-selenium': 'price'})
        if price_tag:
            price = ''.join(filter(str.isdigit, price_tag.text))
            return int(price)
        return None
    except Exception as e:
        print(f"[{country_code}] 取得失敗: {e}")
        return None

def process_url_request(hotel_url, checkin, checkout, guests, fpath):
    result = {
        "hotel_url": hotel_url,
        "check_in": str(checkin),
        "check_out": str(checkout),
        "guest_count": guests,
        "updated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "prices": []
    }

    for country, code in TARGET_COUNTRIES.items():
        modified_url = modify_url(hotel_url, checkin, checkout, guests)
        price = fetch_price(modified_url, code)
        if price:
            result["prices"].append({
                "country": country,
                "price": price,
                "currency": "local",
                "url": modified_url + "&cid=XXXX"
            })

    result["prices"].sort(key=lambda x: x["price"])
    result["is_pending"] = False

    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
