
import streamlit as st
import json
import hashlib
import os
from datetime import datetime
from scrape_prices import process_single_request

st.title("Agoda 最安国検索")

hotel_name = st.text_input("ホテル名")
checkin_date = st.date_input("チェックイン日")
checkout_date = st.date_input("チェックアウト日")
guest_count = st.selectbox("宿泊人数", [1, 2, 3, 4])
realtime = st.checkbox("リアルタイムで取得（テスト用）")

if st.button("検索する"):
    key = hashlib.md5(f"{hotel_name}_{checkin_date}_{checkout_date}_{guest_count}".encode()).hexdigest()
    cache_path = f"cache/{key}.json"

    if realtime:
        process_single_request(hotel_name, checkin_date, checkout_date, guest_count, cache_path)
    else:
        os.makedirs("cache", exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump({
                "hotel": hotel_name,
                "check_in": str(checkin_date),
                "check_out": str(checkout_date),
                "guest_count": guest_count,
                "is_pending": True
            }, f)

    st.experimental_rerun()

# 表示部
if hotel_name:
    key = hashlib.md5(f"{hotel_name}_{checkin_date}_{checkout_date}_{guest_count}".encode()).hexdigest()
    try:
        with open(f"cache/{key}.json", "r") as f:
            data = json.load(f)
        if data.get("is_pending"):
            st.info("価格情報を取得中です。しばらくしてから再度お試しください。")
        else:
            st.success(f"最安国: {data['prices'][0]['country']} ¥{data['prices'][0]['price']}")
            for p in data["prices"]:
                st.write(f"{p['country']} ¥{p['price']} ({p['currency']})")
                st.markdown(f"[予約はこちら]({p['url']})", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("キャッシュファイルが存在しません。")
