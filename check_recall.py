import pandas as pd
import requests
import os
from datetime import datetime

# 1. 配置資訊
# 建議將試算表連結也設為環境變數以增加安全感
SHEET_URL = "https://docs.google.com/spreadsheets/d/13DzEOTqFqV1czjQVuz8zONNz51k0_A3YgL_o47POsbQ/export?format=csv"

# 從 GitHub Secrets 讀取金鑰
LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def send_line_push(message):
    """透過 LINE Messaging API 發送推播訊息"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ LINE 訊息推送成功！")
        else:
            print(f"❌ 推送失敗：{response.status_code} - {response.text}")
    except Exception as e:
        print(f"💥 發送過程中發生異常：{e}")

def check_memories():
    """檢查試算表中是否有今日到期的回憶"""
    try:
        # 讀取試算表
        df = pd.read_csv(SHEET_URL)
        
        # 取得今天日期（考慮到不同格式）
        now = datetime.now()
        today_variants = [
            now.strftime('%Y-%m-%d'),
            now.strftime('%Y/%m/%d'),
            now.strftime('%Y/%-m/%-d')
        ]
        
        # 格式化日期欄位並篩選
        df['開啟日期'] = df['開啟日期'].astype(str).str.strip()
        due_memories = df[df['開啟日期'].isin(today_variants)]
        
        if not due_memories.empty:
            count = len(due_memories)
            msg = f"🔔 憶起 (Recall) 提醒：今天有 {count} 則回憶到期了！\n"
            msg += "===================="
            
            for _, row in due_memories.iterrows():
                # 根據試算表欄位名稱獲取資料
                ig_id = row.get('Instagram ID', '未知用戶')
                content = row.get('信件內容', '無內容')
                msg += f"\n👤 傳送者: {ig_id}\n"
                msg += f"📜 內容: {content}\n"
                msg += "--------------------"
            
            # 執行推送
            if LINE_TOKEN and USER_ID:
                send_line_push(msg)
            else:
                print("⚠️ 錯誤：找不到 LINE 金鑰或 User ID。請檢查 GitHub Secrets 設定。")
                print(msg)
        else:
            print(f"✨ 檢查完畢（{now.strftime('%Y-%m-%d')}）：今日無到期回憶。")
            
    except Exception as e:
        print(f"💥 讀取或檢查過程出錯：{e}")

if __name__ == "__main__":
    check_memories()
