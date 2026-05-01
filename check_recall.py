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
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("✅ LINE 訊息推送成功！")
    else:
        print(f"❌ 推送失敗: {response.text}")

def check_memories():
    try:
        # 讀取 CSV 並自動處理編碼字元
        df = pd.read_csv(SHEET_URL, encoding='utf-8-sig')
        
        # 關鍵修正：清理欄位名稱的所有前後空白與特殊字元
        df.columns = df.columns.str.strip()
        
        # 除錯資訊：在 GitHub Actions 日誌中顯示目前看到的欄位名
        print(f"🔍 偵測到的欄位清單: {list(df.columns)}")
        
        if '開啟日期' not in df.columns:
            print(f"⚠️ 找不到『開啟日期』！目前第一欄名稱是: '{df.columns[0]}'")
            return

        now = datetime.now()
        # 匹配多種日期顯示格式 (包含試算表常用的 YYYY/M/D)
        today_variants = [
            now.strftime('%Y-%m-%d'),
            now.strftime('%Y/%m/%d'),
            now.strftime('%Y/%-m/%-d'),
            f"{now.year}/{now.month}/{now.day}"
        ]
        
        df['開啟日期'] = df['開啟日期'].astype(str).str.strip()
        due_memories = df[df['開啟日期'].isin(today_variants)]
        
        if not due_memories.empty:
            msg = f"🔔 憶起 (Recall) 提醒：今天有 {len(due_memories)} 則回憶到期！\n"
            msg += "===================="
            for _, row in due_memories.iterrows():
                # 使用 get 防止欄位名微小差異導致當機
                ig_id = row.get('Instagram ID', '未知用戶')
                content = row.get('信件內容', '無內容')
                msg += f"\n👤 傳送者: {ig_id}\n📜 內容: {content}\n"
                msg += "--------------------"
            
            if LINE_TOKEN and USER_ID:
                send_line_push(msg)
            else:
                print("未設定 LINE 金鑰，僅列印訊息：\n", msg)
        else:
            print(f"✨ 檢查完畢（{now.strftime('%Y-%m-%d')}）：今日無到期回憶。")
            
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    check_memories()
