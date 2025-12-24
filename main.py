from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import folium
from folium.plugins import LocateControl
import requests
import csv
import io
import urllib3 # 新增這行

# 忽略安全憑證的警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

def load_real_aed_data():
    url = "https://tw-aed.mohw.gov.tw/openData?t=csv"
    print(f"正在連線至衛福部下載資料: {url} ...")
    
    try:
        # 【關鍵修改】 verify=False 表示不檢查 SSL 憑證
        response = requests.get(url, verify=False) 
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        csv_file = io.StringIO(response.text)
        reader = csv.DictReader(csv_file)
        
        real_locations = []
        
        for row in reader:
            address = row.get('場所地址') or row.get('地址') or ''
            
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

    except Exception as e:
        # 如果還是失敗，會印出詳細錯誤原因
        print(f"❌ 下載失敗！錯誤原因: {e}")
        return [
             {"name": "(備用) 雲林縣政府", "lat": 23.7095, "lon": 120.5435, "desc": "下載失敗，這是備用資料"},
             {"name": "(備用) 斗六火車站", "lat": 23.7119, "lon": 120.5414, "desc": "下載失敗，這是備用資料"}
        ]

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