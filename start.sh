#!/bin/bash

echo "================================================="
echo " 📡 INITIATING IRAN NEWS ENGINE V1.0 "
echo "================================================="
echo "LOCATION: ISTANBUL | MODE: LOCAL COMMAND CENTER"
echo ""

# ۱. فعال‌سازی محیط مجازی (Virtual Environment)
source venv/bin/activate

# ۲. اجرای ربات تلگرام و سیستم جمع‌آوری در پس‌زمینه
echo "⚙️ [1/2] Booting up AI Backend & Telegram Bot..."
python main.py &
BOT_PID=$!

# ۳. سیستم امنیتی: اگر ترمینال رو بستی، ربات هم متوقف بشه تا منابعت هدر نره
cleanup() {
    echo ""
    echo "🛑 SHUTTING DOWN ENGINES..."
    kill $BOT_PID
    exit
}
trap cleanup SIGINT SIGTERM

# ۴. اجرای داشبورد سینمایی
echo "🖥️ [2/2] Launching Cyberpunk Dashboard..."
echo "-------------------------------------------------"
streamlit run app.py
