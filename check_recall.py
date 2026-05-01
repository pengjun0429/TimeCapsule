import pandas as pd
import requests
import os
from datetime import datetime

SHEET_URL = "https://docs.google.com/spreadsheets/d/13DzEOTqFqV1czjQVuz8zONNz51k0_A3YgL_o47POsbQ/export?format=csv"
LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def send_line_push(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("✅ LINE 訊息推送成功！")
    else:
        # 這裡會印出為什麼失敗，例如 401 代表 Token 錯誤
        print(f"❌ LINE 傳送失敗！狀態碼: {response.status_code}")
        print(f"原因: {response.text}")

def check_memories():
    try:
        df = pd.read_csv(SHEET_URL, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        
        # 取得欄位名稱
        ig_col, content_col, date_col = df.columns[1], df.columns[2], df.columns[3]
        print(f"🔍 診斷：偵測到 {len(df.columns)} 個欄位")

        now = datetime.now()
        today_str = f"{now.year}/{now.month}/{now.day}"
        today_dash = now.strftime('%Y-%m-%d')
        print(f"📅 正在尋找日期為 {today_str} 的資料...")

        df[date_col] = df[date_col].astype(str).str.strip()
        due_memories = df[df[date_col].isin([today_str, today_dash])]
        
        if not due_memories.empty:
            msg = f"🔔 憶起提醒：今天有 {len(due_memories)} 則回憶到期！\n"
            msg += "===================="
            for _, row in due_memories.iterrows():
                msg += f"\n👤 帳號: {row[ig_col]}\n📜 內容: {row[content_col]}\n"
                msg += "--------------------"
            
            if LINE_TOKEN and USER_ID:
                send_line_push(msg)
        else:
            print(f"✨ 檢查完畢：今日無到期回憶")
            
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    check_memories()
