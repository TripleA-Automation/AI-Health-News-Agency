

import os
import json
import requests
import ollama
import smtplib
import gspread
from email.mime.text import MIMEText
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


# 1. THE FOUNDATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GMAIL_USER = "your email" # <-- Replace with your real email
GMAIL_PASS = "***********" # <-- Your App Password
SHEET_NAME = "*************" # <-- Your exact Sheet Name
CREDENTIALS_FILE = os.path.join(BASE_DIR, "service_account.json")
# 2. THE LOCAL BRAIN (Llama 3.2 - Strict Mode)
def generate_viral_content(news_headlines):
    print("🧠 Llama is generating your Daily Health Update...")
    prompt = f"""
    News: {news_headlines}
    Pick ONE news item. Create a Viral TikTok Bundle.
    Respond ONLY with these 5 text strings:
    "selected_news": (The headline),
    "tiktok_hook": (The 3-second hook),
    "video_script": (A short script),
    "caption": (Text with hashtags),
    "importance_score": (A number from 1-10)
    """
    try:
        response = ollama.chat(model='llama3.2', format='json', messages=[{'role': 'user', 'content': prompt}])
        return json.loads(response['message']['content'])
    except Exception:
        return None
# 3. DIRECT SHEET (Matching Columns A:Date, B:Hook, C:Rank)
def add_to_sheet(bundle):
    print("📄 Polishing Spreadsheet Columns...")
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        
        new_row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"), # Col A: Date
            str(bundle.get("tiktok_hook", "N/A")),      # Col B: TikTok Hook
            str(bundle.get("importance_score", "9")),   # Col C: AI Rank
            str(bundle.get("selected_news", "N/A")),    # Col D: News Source
            str(bundle.get("caption", "N/A"))           # Col E: Caption
        ]
        sheet.append_row(new_row)
        print("✅ SPREADSHEET UPDATED DIRECTLY!")
    except Exception as e:
        print(f"❌ SHEET ERROR: {e}")
# 4. DIRECT EMAIL (Professional Subject & Body)
def send_direct_email(bundle):
    print("📧 Sending Human-Friendly Email...")
    
    clean_hook = bundle.get('tiktok_hook', 'No hook')
    headline = bundle.get('selected_news', 'Health Update')
    caption = bundle.get('caption', '#health')
    
    msg_content = f"Today's Viral Health Idea:\n\n🎯 TIKTOK HOOK:\n{clean_hook}\n\n📰 BASED ON NEWS:\n{headline}\n\n📱 CAPTION READY:\n{caption}"
    msg = MIMEText(msg_content)
    msg['Subject'] = "Daily Health News Update" # <--- Fixed Subject
    msg['From'] = GMAIL_USER
    msg['To'] = "ammarfareed1947@yahoo.com"
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print("✅ CLEAN EMAIL SENT!")
    except Exception as e:
        print(f"❌ EMAIL ERROR: {e}")
# 5. DATA HUNTER (NewsAPI)
def get_health_news():
    api_key = "ffef754a092244cb9fca0f888f92dc27" 
    url = f"https://newsapi.org/v2/top-headlines?category=health&language=en&apiKey={api_key}"
    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])
        return [a["title"] for a in articles[:5] if a["title"]]
    except:
        return ["Backup: Study on Walking and Health"]
# --- EXECUTION ---
if __name__ == "__main__":
    print("👑 THE PURE PYTHON AGENCY STARTING...")
    news = get_health_news()
    content = generate_viral_content(news)
    if content:
        add_to_sheet(content)
        send_direct_email(content)