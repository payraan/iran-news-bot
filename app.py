import streamlit as st
import random
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import asyncio

# اضافه شدن موتور رتبه‌بندی هوشمند به داشبورد
from database.connection import AsyncSessionLocal
from services.news_ranker import get_top_news
from cache.redis_client import redis_client
from config.settings import settings
from services.topic_detector import detect_topics 

# --- Auto Refresh System ---
st_autorefresh(interval=5 * 60 * 1000, key="iran_news_refresh") 

# --- Page Config ---
st.set_page_config(page_title="Project ORACLE", layout="wide", initial_sidebar_state="collapsed")

# --- Fake Live Users ---
live_users = random.randint(53, 487)

# --- Cyberpunk CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Vazirmatn:wght@300;400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Vazirmatn', sans-serif;
        background-color: #050505;
        color: #e0e0e0;
        direction: rtl; 
        text-align: right;
    }
    .mono { font-family: 'JetBrains Mono', monospace; direction: ltr; display: inline-block; }
    .header-title { font-size: 2.5rem; font-weight: 900; color: white; margin-bottom: 0; letter-spacing: 2px; }
    .live-badge { background-color: #dc2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; animation: pulse 2s infinite; vertical-align: middle; margin-right: 10px;}
    .users-badge { background-color: rgba(0, 255, 65, 0.1); color: #00ff41; padding: 5px 12px; border-radius: 20px; font-size: 0.9rem; border: 1px solid #00ff41; float: left; margin-top: 15px;}
    .glass-box { background: rgba(20, 20, 20, 0.7); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .topic-tag { background: rgba(255,255,255,0.05); padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; margin-left: 8px; margin-bottom: 8px; display: inline-block; border: 1px solid rgba(255,255,255,0.1); color: #ccc;}
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown(f"""
    <div>
        <span class='users-badge'>👁‍🗨 {live_users} کاربر در حال رصد</span>
        <p class='header-title'>PROJECT ORACLE <span style='font-size: 1.5rem; color: #888;'>| پیشگوی سایبری</span> <span class='live-badge'>LIVE</span></p>
    </div>
    <hr style='border-color: #333;'>
""", unsafe_allow_html=True)

# --- Fetch Data (Using AI Ranker) ---
def fetch_dashboard_data():
    async def _fetch():
        async with AsyncSessionLocal() as session:
            # دقیقاً همون تابعی که ربات تلگرام استفاده می‌کنه
            return await get_top_news(session, limit=20)
    return asyncio.run(_fetch())

news_list = fetch_dashboard_data()

if not news_list:
    st.error("خطای سیستم: داده‌ای در دیتابیس یافت نشد.")
else:
    avg_sentiment = sum(n.sentiment for n in news_list if n.sentiment is not None) / len(news_list)
    tension_level = int(((1 - avg_sentiment) / 2) * 100)
    trending_topics = detect_topics(news_list)
    
    left_col, right_col = st.columns([1, 1.5])
    
    with left_col:
        st.markdown("<p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// دماسنج التهاب کشور</p>", unsafe_allow_html=True)
        
        # --- Speedometer (Gauge Chart) ---
        gauge_color = "#ff3131" if tension_level > 60 else ("#ffdf00" if tension_level > 40 else "#00ff41")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=tension_level,
            number={'suffix': "%", 'font': {'color': gauge_color, 'size': 50, 'family': 'JetBrains Mono'}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#333"},
                'bar': {'color': gauge_color, 'thickness': 0.25},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': "rgba(0, 255, 65, 0.1)"},
                    {'range': [40, 60], 'color': "rgba(255, 223, 0, 0.1)"},
                    {'range': [60, 100], 'color': "rgba(255, 49, 49, 0.1)"}],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': tension_level}
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white", 'family': "Vazirmatn"})
        st.plotly_chart(fig, use_container_width=True)

        # --- Trending Topics ---
        if trending_topics:
            tags_html = "".join([f"<span class='topic-tag'>🔥 {topic}</span>" for topic, count in trending_topics])
            st.markdown(f"<div>{tags_html}</div><br>", unsafe_allow_html=True)

        # --- 24-Hour AI Report ---
        st.markdown("<p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// گزارش ۲۴ ساعت گذشته</p>", unsafe_allow_html=True)
        daily_report = redis_client.get("daily_report")
        if daily_report:
            st.markdown(f"<div class='glass-box' style='border-right: 4px solid #00ff41;'><p style='font-size: 0.9rem; line-height: 1.8;'>{daily_report}</p></div>", unsafe_allow_html=True)
        else:
            st.info("سیستم در حال جمع‌آوری دیتا برای پردازش گزارش ۲۴ ساعته می‌باشد (منتظر بمانید)...")

        # --- 7-Day Scenario ---
        st.markdown("<p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// پیش‌بینی آینده (۷ روز)</p>", unsafe_allow_html=True)
        scenario = redis_client.get("latest_scenarios")
        if scenario:
            st.warning(scenario)

    with right_col:
        st.markdown("<p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// جریان زنده اخبار</p>", unsafe_allow_html=True)
        for news in news_list:
            s_color = "#00ff41" if news.sentiment > 0.2 else ("#ff3131" if news.sentiment < -0.2 else "#ffdf00")
            st.markdown(f"""
            <div style='background: rgba(20,20,20,0.5); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-right: 2px solid {s_color}; text-align: right;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px; flex-direction: row-reverse;'>
                    <span class='mono' style='font-size: 0.7rem; color: #666;'>{news.source}</span>
                </div>
                <h4 style='margin-top: 0; color: white; font-size: 1.1rem; line-height: 1.5;'>{news.title}</h4>
                <p style='color: #aaa; font-size: 0.9rem; line-height: 1.8;'>{news.summary}</p>
            </div>
            """, unsafe_allow_html=True)
