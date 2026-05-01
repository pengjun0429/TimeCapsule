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
    res = requests.post(url, headers=headers, json=payload)
    print(f"LINE 伺服器回應: {res.status_code}")

def check_memories():
    try:
        # 讀取 CSV，並忽略第一列標題名稱，改用數字索引
        df = pd.read_csv(SHEET_URL, encoding='utf-8-sig', header=0)
        
        # 打印目前看到的總欄位數
        col_count = len(df.columns)
        print(f"🔍 診斷：偵測到 {col_count} 個欄位")
        
        if col_count < 4:
            print("❌ 錯誤：試算表欄位不足 4 欄，請檢查 Google Sheet！")
            return

        # 直接用位置拿資料 (iloc)
        # 第 1 欄 (index 0): 時戳 -> 忽略
        # 第 2 欄 (index 1): Instagram ID
        # 第 3 欄 (index 2): 信件內容
        # 第 4 欄 (index 3): 開啟日期
        
        now = datetime.now()
        # 匹配截圖中的格式: 2026/5/1
        today_str = f"{now.year}/{now.month}/{now.day}"
        # 匹配標準格式: 2026-05-01
        today_dash = now.strftime('%Y-%m-%d')
        
        print(f"📅 正在尋找日期為 {today_str} 或 {today_dash} 的資料...")

        # 找出第 4 欄符合今天日期的行
        # df.iloc[:, 3] 代表「所有列的第 4 欄」
        mask = df.iloc[:, 3].astype(str).str.strip().isin([today_str, today_dash])
        due_memories = df[mask]
        
        if not due_memories.empty:
            count = len(due_memories)
            msg = f"🔔 憶起 (Recall) 提醒：今天有 {count} 則回憶到期！\n"
            msg += "===================="
            for i in range(len(due_memories)):
                row = due_memories.iloc[i]
                ig_id = row.iloc[1]   # 第 2 欄
                content = row.iloc[2] # 第 3 欄
                msg += f"\n👤 傳送者: {ig_id}\n"
                msg += f"📜 內容: {content}\n"
                msg += "--------------------"
            
            if LINE_TOKEN and USER_ID:
                send_line_push(msg)
                print("✅ 成功：訊息已推送到 LINE！")
            else:
                print("⚠️ 警告：缺少 LINE 金鑰，僅在日誌顯示：\n", msg)
        else:
            print(f"✨ 檢查完畢：今日 ({today_str}) 沒有到期的回憶。")
            
    except Exception as e:
        print(f"💥 發生未知錯誤: {e}")

if __name__ == "__main__":
    check_memories()
