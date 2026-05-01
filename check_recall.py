import pandas as pd
import requests
import os
from datetime import datetime

# 試算表 CSV 連結
SHEET_URL = "https://docs.google.com/spreadsheets/d/13DzEOTqFqV1czjQVuz8zONNz51k0_A3YgL_o47POsbQ/export?format=csv"

# 從 GitHub Secrets 讀取資料
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
    requests.post(url, headers=headers, json=payload)

def check_memories():
    try:
        # 讀取 CSV，header=0 表示第一列是標題
        df = pd.read_csv(SHEET_URL, encoding='utf-8-sig')
        
        # 顯示目前讀取到的欄位數，確保有讀到 4 欄以上
        print(f"📊 目前讀取到的總欄位數: {len(df.columns)}")
        
        # 直接指定：第 2 欄是 ID, 第 3 欄是內容, 第 4 欄是日期
        # (Python 索引從 0 開始，所以是 1, 2, 3)
        col_ig = df.columns[1]
        col_content = df.columns[2]
        col_date = df.columns[3]
        
        print(f"✅ 自動鎖定欄位：ID={col_ig}, 內容={col_content}, 日期={col_date}")

        now = datetime.now()
        # 準備匹配日期 (YYYY/M/D 格式)
        today_str = f"{now.year}/{now.month}/{now.day}"
        today_dash = now.strftime('%Y-%m-%d')
        
        # 過濾日期
        df[col_date] = df[col_date].astype(str).str.strip()
        due_memories = df[df[col_date].isin([today_str, today_dash])]
        
        if not due_memories.empty:
            msg = f"🔔 憶起 (Recall) 提醒：今天有 {len(due_memories)} 則回憶到期！\n"
            msg += "===================="
            for _, row in due_memories.iterrows():
                msg += f"\n👤 傳送者: {row[col_ig]}\n📜 內容: {row[col_content]}\n"
                msg += "--------------------"
            
            if LINE_TOKEN and USER_ID:
                send_line_push(msg)
                print("✅ 訊息已送出！")
            else:
                print("⚠️ 缺少金鑰，僅列印：\n", msg)
        else:
            print(f"✨ 檢查完畢（{today_str}）：今日無到期回憶。")
            
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    check_memories()
