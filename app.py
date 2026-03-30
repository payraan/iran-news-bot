import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from database.models import News
from cache.redis_client import redis_client
from config.settings import settings

# استفاده از قابلیت مخفی تشخیص موضوعات داغ
from services.topic_detector import detect_topics 

# --- Auto Refresh System ---
st_autorefresh(interval=5 * 60 * 1000, key="iran_news_refresh") 

# --- Setup Sync Database ---
SYNC_DB_URL = settings.DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(SYNC_DB_URL)
SyncSession = sessionmaker(bind=engine)

# --- Page Config ---
st.set_page_config(page_title="پایگاه فرماندهی اخبار", layout="wide", initial_sidebar_state="collapsed")

# --- Cyberpunk CSS (Persian Adjusted) ---
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
    
    .mono { 
        font-family: 'JetBrains Mono', monospace; 
        direction: ltr;
        display: inline-block;
    }
    
    .header-title { font-size: 2.2rem; font-weight: 900; color: white; margin-bottom: 0; direction: rtl; text-align: right; display: block; }
    .header-neon { color: #00ff41; }
    .live-badge { background-color: #dc2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; animation: pulse 2s infinite; vertical-align: middle; margin-right: 10px;}
    
    .glass-box { background: rgba(20, 20, 20, 0.7); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    
    .border-red { border-right: 4px solid #ff3131; }
    .border-yellow { border-right: 4px solid #ffdf00; }
    .border-green { border-right: 4px solid #00ff41; }

    /* استایل تگ‌های موضوعات داغ */
    .topic-tag { background: rgba(255,255,255,0.05); padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; margin-left: 8px; margin-bottom: 8px; display: inline-block; border: 1px solid rgba(255,255,255,0.1); color: #ccc;}
    
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<p class='header-title'>موتور پردازش اخبار ایران <span class='live-badge'>زنده</span></p>", unsafe_allow_html=True)

st.markdown("---")

# --- Fetch Data (Synchronous) ---
def fetch_dashboard_data():
    with SyncSession() as session:
        result = session.execute(
            select(News).where(News.summary != None).order_by(News.published_at.desc()).limit(20)
        )
        return result.scalars().all()

news_list = fetch_dashboard_data()

if not news_list:
    st.error("خطای سیستم: داده‌ای در دیتابیس یافت نشد.")
else:
    avg_sentiment = sum(n.sentiment for n in news_list if n.sentiment is not None) / len(news_list)
    tension_level = int(((1 - avg_sentiment) / 2) * 100)
    
    # پردازش موضوعات داغ
    trending_topics = detect_topics(news_list)
    
    left_col, right_col = st.columns([1, 1.5])
    
    with left_col:
        st.markdown("<p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// شاخص التهاب سیستم</p>", unsafe_allow_html=True)
        
        # تعیین رنگ بر اساس درصد
        t_color = "#ff3131" if tension_level > 60 else ("#ffdf00" if tension_level > 40 else "#00ff41")
        
        # نمایش درصد + نوار پیشرفت (Progress Bar)
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;">
            <h1 class='mono' style='color: {t_color}; font-size: 4.5rem; margin: 0;'>{tension_level}%</h1>
        </div>
        <div style="width: 100%; background-color: #1a1a1a; border-radius: 10px; margin-bottom: 20px; overflow: hidden; border: 1px solid #333;">
            <div style="width: {tension_level}%; height: 12px; background-color: {t_color}; box-shadow: 0 0 10px {t_color}; transition: width 1s ease-in-out;"></div>
        </div>
        """, unsafe_allow_html=True)

        if tension_level > 60:
            st.markdown("<p style='color: #ff3131; font-weight: bold;'>وضعیت بحرانی</p>", unsafe_allow_html=True)
            st.markdown("""
            <div class='glass-box border-red'>
                <p style='color: #888; font-size: 0.8rem;'>هشدار سیستم</p>
                <h4 style='color: #ff3131;'>وضعیت قرمز - التهاب شدید اخبار</h4>
                <p>توصیه سیستم: از پیگیری لحظه‌ای اخبار خودداری کنید و تمرکز را روی کارهای شخصی بگذارید.</p>
            </div>
            """, unsafe_allow_html=True)
            
        elif tension_level > 40:
            st.markdown("<p style='color: #ffdf00; font-weight: bold;'>ریسک بالا</p>", unsafe_allow_html=True)
            st.markdown("""
            <div class='glass-box border-yellow'>
                <p style='color: #888; font-size: 0.8rem;'>هشدار سیستم</p>
                <h4 style='color: #ffdf00;'>احتیاط استراتژیک</h4>
                <p>توصیه سیستم: اخبار را فقط روزی یک‌بار چک کنید. وضعیت بازار پرنوسان است.</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("<p style='color: #00ff41; font-weight: bold;'>پایدار</p>", unsafe_allow_html=True)
            st.markdown("""
            <div class='glass-box border-green'>
                <p style='color: #888; font-size: 0.8rem;'>پیام سیستم</p>
                <h4 style='color: #00ff41;'>عملیات عادی</h4>
                <p>وضعیت اخبار باثبات است. می‌توانید با خیال راحت به برنامه‌های روتین بپردازید.</p>
            </div>
            """, unsafe_allow_html=True)

        # --- بخش جدید: موضوعات داغ ---
        if trending_topics:
            st.markdown("<br><p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// موضوعات داغ لحظه‌ای</p>", unsafe_allow_html=True)
            tags_html = "".join([f"<span class='topic-tag'>🔥 {topic}</span>" for topic, count in trending_topics])
            st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

        st.markdown("<br><p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// پیش‌بینی هوش مصنوعی (۷ روز آینده)</p>", unsafe_allow_html=True)
        scenario = redis_client.get("latest_scenarios")
        if scenario:
            st.info(scenario)
        else:
            st.warning("در حال محاسبه سناریو... دکمه 'آینده ایران' را در تلگرام بزنید.")

    with right_col:
        st.markdown("<p style='color: #888; letter-spacing: 1px; font-weight: bold;'>// جریان زنده اخبار</p>", unsafe_allow_html=True)
        for news in news_list:
            s_color = "#00ff41" if news.sentiment > 0.2 else ("#ff3131" if news.sentiment < -0.2 else "#ffdf00")
            sentiment_label = "مثبت" if news.sentiment > 0.2 else ("منفی" if news.sentiment < -0.2 else "خنثی")
            
            st.markdown(f"""
            <div style='background: rgba(20,20,20,0.5); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-right: 2px solid {s_color}; text-align: right;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px; flex-direction: row-reverse;'>
                    <span class='mono' style='font-size: 0.7rem; color: #666;'>{news.source}</span>
                    <span style='font-size: 0.7rem; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; color: {s_color}; border: 1px solid {s_color}40;'>تحلیل حس: {sentiment_label}</span>
                </div>
                <h4 style='margin-top: 0; color: white; font-size: 1.1rem; line-height: 1.5;'>{news.title}</h4>
                <p style='color: #aaa; font-size: 0.9rem; line-height: 1.8;'>{news.summary}</p>
            </div>
            """, unsafe_allow_html=True)
