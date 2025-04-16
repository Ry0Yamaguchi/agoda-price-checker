
import streamlit as st
import requests
import json
import hashlib
from datetime import datetime

st.title("Agoda 最安国検索")

hotel_name = st.text_input("ホテル名")
checkin_date = st.date_input("チェックイン日")
checkout_date = st.date_input("チェックアウト日")
guest_count = st.selectbox("宿泊人数", [1, 2, 3, 4])

if st.button("検索する"):
    key = hashlib.md5(f"{hotel_name}_{checkin_date}_{checkout_date}_{guest_count}".encode()).hexdigest()
    try:
        with open(f"cache/{key}.json", "r") as f:
            data = json.load(f)
        if data["is_pending"]:
            st.info("データ取得中です。しばらくしてから再度ご確認ください。")
        else:
            st.success(f"最安国: {data['prices'][0]['country']} ¥{data['prices'][0]['price']}")
            for p in data["prices"]:
                st.write(f"{p['country']} ¥{p['price']} ({p['currency']})")
                st.markdown(f"[予約はこちら]({p['url']})", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("初回検索です。価格情報を取得中です。次回アクセスで表示されます。")
        with open(f"cache/{key}.json", "w") as f:
            json.dump({"is_pending": True}, f)
