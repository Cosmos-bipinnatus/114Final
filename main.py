from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import folium
from folium.plugins import LocateControl

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # 1. 設定定位中心：雲林 (以斗六車站附近為例)
    yunlin_center = [23.7119, 120.5414] 
    
    # 建立地圖，zoom_start 設定大一點 (15) 才能看清街道
    m = folium.Map(location=yunlin_center, zoom_start=15, tiles=None)

    # 2. 設定國土測繪中心 API (通用版電子地圖)
    nlsc_url = "https://wmts.nlsc.gov.tw/wmts/EMAP/default/GoogleMapsCompatible/{z}/{y}/{x}"

    # 加入底圖圖層
    folium.TileLayer(
        tiles=nlsc_url,
        attr="國土測繪中心",
        name="Taiwan e-Map"
    ).add_to(m)

    # 3. 加入 AED 資料 (模擬數據)
    # 在實際專案中，這裡通常會從資料庫或政府 Open Data API 讀取
    aed_locations = [
        {"name": "雲林縣政府 AED", "lat": 23.7095, "lon": 120.5435, "desc": "位於一樓大廳"},
        {"name": "斗六火車站 AED", "lat": 23.7119, "lon": 120.5414, "desc": "售票口旁"},
        {"name": "雲林科技大學 AED", "lat": 23.6961, "lon": 120.5342, "desc": "行政大樓"},
        {"name": "雲林國中 AED", "lat": 23.7060, "lon": 120.5380, "desc": "警衛室"}
    ]

    # 將每一個 AED 畫在地圖上
    for aed in aed_locations:
        folium.Marker(
            location=[aed["lat"], aed["lon"]],
            popup=folium.Popup(f"<b>{aed['name']}</b><br>{aed['desc']}", max_width=300),
            tooltip=aed["name"],
            icon=folium.Icon(color="red", icon="heart", prefix="fa") # 使用紅色愛心圖示
        ).add_to(m)

    # 4. 加入使用者自我定位按鈕 (GUI 功能)
    # 這會在地圖左上角增加一個按鈕，點擊後瀏覽器會請求位置權限並定位使用者
    LocateControl(
        auto_start=False,
        strings={"title": "顯示我的位置"}
    ).add_to(m)

    # 5. 將地圖轉為 HTML 字串回傳
    return m.get_root().render()

if __name__ == "__main__":
    import uvicorn
    # 執行伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)