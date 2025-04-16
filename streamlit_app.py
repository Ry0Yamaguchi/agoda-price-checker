import streamlit as st
import json
import hashlib
import os
from datetime import datetime
from scrape_prices import process_url_request

st.title("Agoda 最安国検索（URLベース）")

hotel_url = st.text_input("Agoda ホテルURLを入力")
checkin_date = st.date_input("チェックイン日")
checkout_date = st.date_input("チェックアウト日")
guest_count = st.selectbox("宿泊人数", [1, 2, 3, 4])
realtime = st.checkbox("リアルタイムで取得（テスト用）")

if st.button("検索する"):
    key_base = f"{hotel_url}_{checkin_date}_{checkout_date}_{guest_count}"
    key = hashlib.md5(key_base.encode()).hexdigest()
    cache_path = f"cache/{key}.json"

    if realtime:
        process_url_request(hotel_url, checkin_date, checkout_date, guest_count, cache_path)
    else:
        os.makedirs("cache", exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump({
                "hotel_url": hotel_url,
                "check_in": str(checkin_date),
                "check_out": str(checkout_date),
                "guest_count": guest_count,
                "is_pending": True
            }, f)

# 表示部
if hotel_url:
    key_base = f"{hotel_url}_{checkin_date}_{checkout_date}_{guest_count}"
    key = hashlib.md5(key_base.encode()).hexdigest()
    cache_path = f"cache/{key}.json"
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            data = json.load(f)
        if data.get("is_pending"):
            st.info("価格情報を取得中です。しばらくしてから再度お試しください。")
        elif not data.get("prices"):
            st.warning("価格が取得できませんでした。URLや日付を見直してください。")
        else:
            st.success(f"最安国: {data['prices'][0]['country']} ¥{data['prices'][0]['price']}")
            for p in data["prices"]:
                st.write(f"{p['country']} ¥{p['price']} ({p['currency']})")
                st.markdown(f"[予約はこちら]({p['url']})", unsafe_allow_html=True)
    else:
        st.warning("キャッシュがまだ存在していません。")
