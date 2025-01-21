import os
import sys
from dotenv import load_dotenv

# Loyiha asosiy papkasini sys.path ga qo‘shamiz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# .env faylni yuklash
load_dotenv()

# app.py faylni ishga tushirish
from bot.app import executor, dp, on_startup

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
