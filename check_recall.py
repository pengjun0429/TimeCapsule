import pandas as pd
import requests
import os
from datetime import datetime

SHEET_URL = "https://docs.google.com/spreadsheets/d/13DzEOTqFqV1czjQVuz8zONNz51k0_A3YgL_o47POsbQ/export?format=csv"
LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def send_line_push(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    r = requests.post(url, headers=headers, json=payload)
    print(f"📡 LINE 伺服器回應: {r.status_code}")

def check_memories():
    try:
        # 1. 讀取並顯示基礎資訊
        df = pd.read_csv(SHEET_URL, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        print(f"📊 成功讀取試算表！總列數: {len(df)}，欄位: {list(df.columns)}")
        
        # 2. 鎖定日期欄位 (假設在第四欄)
        date_col = df.columns[3]
        
        # 3. 取得今天日期多種格式
        now = datetime.now()
        t1 = f"{now.year}/{now.month}/{now.day}"        # 2026/5/1
        t2 = f"{now.year}/{now.month:02d}/{now.day:02d}" # 2026/05/01
        t3 = now.strftime('%Y-%m-%d')                   # 2026-05-01
        print(f"📅 今天的目標日期格式: ['{t1}', '{t2}', '{t3}']")
        
        # 4. 顯示試算表內的前三筆日期 (檢查格式用)
        print(f"🔍 試算表內的前幾筆日期實際內容: {df[date_col].head(3).tolist()}")

        # 5. 過濾資料
        df[date_col] = df[date_col].astype(str).str.strip()
        due = df[df[date_col].isin([t1, t2, t3])]
        
        if not due.empty:
            print(f"🎯 找到 {len(due)} 則到期回憶！")
            msg = f"🔔 憶起提醒：今天有 {len(due)} 則回憶到期！"
            for _, row in due.iterrows():
                msg += f"\n\n👤 來源: {row.iloc[1]}\n📜 內容: {row.iloc[2]}"
            
            if LINE_TOKEN and USER_ID:
                send_line_push(msg)
            else:
                print("⚠️ 警告: 缺少 LINE Secrets 設定")
        else:
            print("📭 檢查完畢：今天沒有符合日期的回憶。")

    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    check_memories()
