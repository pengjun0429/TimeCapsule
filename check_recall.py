import pandas as pd
import requests
import os
from datetime import datetime

# 試算表連結
SHEET_URL = "https://docs.google.com/spreadsheets/d/13DzEOTqFqV1czjQVuz8zONNz51k0_A3YgL_o47POsbQ/export?format=csv"

# 環境變數
LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def send_flex_message(ig_id, content):
    """發送美化後的 Flex Message 卡片"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    
    # 處理 IG 連結 (去掉 @ 符號以確保連結正確)
    clean_ig_id = ig_id.replace('@', '').strip()
    ig_link = f"https://www.instagram.com/{clean_ig_id}/"

    flex_contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "憶起 Recall", "weight": "bold", "color": "#e94560", "size": "sm", "tracking": "0.2em"}
            ]
        },
        "hero": {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1516533037047-282d815757f1?auto=format&fit=crop&q=80&w=600",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "時空膠囊到期", "weight": "bold", "size": "xl", "color": "#1a1a2e"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "傳送者", "color": "#aaaaaa", "size": "sm", "flex": 1},
                                {"type": "text", "text": f"{ig_id}", "wrap": True, "color": "#666666", "size": "sm", "flex": 4}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "md",
                            "contents": [
                                {"type": "text", "text": "封存內容：", "color": "#aaaaaa", "size": "sm"},
                                {"type": "text", "text": f"{content}", "wrap": True, "color": "#333333", "size": "md", "margin": "sm", "style": "italic"}
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#e94560",
                    "action": {
                        "type": "uri",
                        "label": "前往 Instagram",
                        "uri": ig_link
                    }
                }
            ]
        }
    }

    payload = {
        "to": USER_ID,
        "messages": [
            {
                "type": "flex",
                "altText": "您有一份到期的回憶！",
                "contents": flex_contents
            }
        ]
    }
    
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code

def check_memories():
    try:
        df = pd.read_csv(SHEET_URL, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        
        ig_col = df.columns[1]
        content_col = df.columns[2]
        date_col = df.columns[3]

        now = datetime.now()
        today_str = f"{now.year}/{now.month}/{now.day}"
        today_dash = now.strftime('%Y-%m-%d')
        
        df[date_col] = df[date_col].astype(str).str.strip()
        due_memories = df[df[date_col].isin([today_str, today_dash])]
        
        if not due_memories.empty:
            for _, row in due_memories.iterrows():
                status = send_flex_message(row[ig_col], row[content_col])
                if status == 200:
                    print(f"✅ 已成功為 {row[ig_col]} 發送精美卡片")
        else:
            print(f"✨ 檢查完畢：今日 ({today_str}) 無到期回憶")
            
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    check_memories()
