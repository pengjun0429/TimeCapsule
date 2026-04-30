import pandas as pd
from datetime import datetime

# 這是使用者提供的試算表 CSV 匯出連結
SHEET_URL = "https://docs.google.com/spreadsheets/d/13DzEOTqFqV1czjQVuz8zONNz51k0_A3YgL_o47POsbQ/export?format=csv"

def check_memories():
    try:
        # 讀取試算表
        df = pd.read_csv(SHEET_URL)
        
        # 取得今天日期 (格式如 2026/05/01)
        # 注意：Google 表單寫入的日期格式可能包含斜線，所以這裡要彈性處理
        today_format1 = datetime.now().strftime('%Y/%m/%d')
        today_format2 = datetime.now().strftime('%Y-%m-%d')
        
        # 篩選「開啟日期」等於今天的資料
        # 使用 .astype(str) 確保日期比對不會出錯
        due_memories = df[(df['開啟日期'].astype(str) == today_format1) | 
                          (df['開啟日期'].astype(str) == today_format2)]
        
        print(f"--- 憶起 Recall 自動檢查報告 ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---")
        
        if not due_memories.empty:
            print(f"找到 {len(due_memories)} 則到期的回憶！")
            for index, row in due_memories.iterrows():
                # 這裡會列印出 IG ID，方便使用者去標記對方
                print(f"📍 目標對象: {row['Instagram ID']}")
                print(f"📜 回憶內容: {row['信件內容']}")
                print("--------------------------------------")
        else:
            print("今天沒有到期的回憶。")
            
    except Exception as e:
        print(f"讀取資料時發生錯誤: {e}")

if __name__ == "__main__":
    check_memories()
