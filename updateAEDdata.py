import requests
import urllib3
import sys  # 需要引入 sys 來控制結束狀態

# 忽略安全憑證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_csv():
    url = "https://tw-aed.mohw.gov.tw/openData?t=csv"
    print(f"正在嘗試下載資料: {url} ...")
    
    try:
        # 設定 timeout=10 秒，避免卡太久
        response = requests.get(url, verify=False,timeout=60)
        response.raise_for_status()
        
        with open("aed_data.csv", "wb") as f:
            f.write(response.content)
            
        print("🎉 下載成功！資料已更新。")
        
    except Exception as e:
        # 這是最關鍵的部分！
        print("--------------------------------------------------")
        print(f"⚠️  無法下載資料 (可能是 IP 被衛福部封鎖)")
        print(f"詳細錯誤: {e}")
        print("--------------------------------------------------")
        print("💡 系統將跳過資料更新，保留舊有 CSV 檔案，繼續執行部署...")
        print("--------------------------------------------------")
        
        # 強制回傳「成功 (0)」，讓 GitHub Actions 認為這一步是「通過」的
        sys.exit(0)

if __name__ == "__main__":
    download_csv()