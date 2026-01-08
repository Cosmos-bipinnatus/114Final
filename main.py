from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import folium
from folium.plugins import LocateControl
import requests
import csv
import io
import urllib3 # 新增這行

# ... (上面的 import 不變)
# 移除 requests, io, urllib3 (因為主程式不需要連網下載了)

app = FastAPI()

def load_real_aed_data():
    # 改為讀取本地檔案
    csv_filename = "aed_data.csv"
    print(f"正在讀取本地資料: {csv_filename} ...")
    
    real_locations = []
    
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                address = row.get('場所地址') or row.get('地址') or ''
                
                # 這裡保留原本的篩選邏輯
                if "雲林" in address:
                    try:
                        name = row.get('場所名稱')
                        lat = row.get('地點LAT') or row.get('WGS84緯度')
                        lon = row.get('地點LNG') or row.get('WGS84經度')
                        desc = row.get('AED放置地點') or row.get('地點詳述')
                        
                        if lat and lon:
                            real_locations.append({
                                "name": name, 
                                "lat": float(lat), 
                                "lon": float(lon), 
                                "desc": desc
                            })
                    except ValueError:
                        continue
        
        print(f"🎉 成功！載入了 {len(real_locations)} 筆雲林 AED 資料！")
        return real_locations

    except FileNotFoundError:
        # 如果還沒有跑過下載腳本，會回傳空或備用資料
        print("⚠️ 找不到 CSV 檔案！")
        return [
             {"name": "(資料尚未同步)", "lat": 23.7095, "lon": 120.5435, "desc": "請等待系統更新"}
        ]
    except Exception as e:
        print(f"❌ 讀取失敗: {e}")
        return []

# ... (其餘路由程式碼保持不變)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    yunlin_center = [23.7119, 120.5414] 
    m = folium.Map(location=yunlin_center, zoom_start=15, tiles=None)

    nlsc_url = "https://wmts.nlsc.gov.tw/wmts/EMAP/default/GoogleMapsCompatible/{z}/{y}/{x}"

    folium.TileLayer(
        tiles=nlsc_url,
        attr="國土測繪中心",
        name="Taiwan e-Map"
    ).add_to(m)

    aed_locations = load_real_aed_data()

    for aed in aed_locations:
        popup_html = f"""
        <div style="font-family: Microsoft JhengHei; width: 200px;">
            <h4>{aed['name']}</h4>
            <p><b>位置:</b> {aed['desc']}</p>
            <a href="https://www.google.com/maps/dir/?api=1&destination={aed['lat']},{aed['lon']}" target="_blank" style="color: blue;">
                🚗 導航到這裡
            </a>
        </div>
        """

        folium.Marker(
            location=[aed["lat"], aed["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=aed["name"],
            icon=folium.Icon(color="green", icon="heart-pulse", prefix="fa") 
        ).add_to(m)

    LocateControl(
        auto_start=False,
        strings={"title": "顯示我的位置"}
    ).add_to(m)

    return m.get_root().render()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)