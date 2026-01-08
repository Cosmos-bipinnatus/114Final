import requests
import urllib3

# 忽略安全憑證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_csv():
    url = "https://tw-aed.mohw.gov.tw/openData?t=csv"
    print(f"正在下載資料: {url} ...")
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        
        # 將下載的內容直接寫入專案目錄下的 aed_data.csv
        with open("aed_data.csv", "wb") as f:
            f.write(response.content)
            
        print("🎉 下載成功！已儲存為 aed_data.csv")
        
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        exit(1) # 回傳錯誤代碼讓 GitHub Action 知道失敗了

if __name__ == "__main__":
    download_csv()