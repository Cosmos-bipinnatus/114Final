from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import folium

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # 1. 建立地圖
    m = folium.Map(location=[23.97, 120.98], zoom_start=7, tiles=None)

    # 2. 設定國土測繪中心 API
    nlsc_url = "https://wmts.nlsc.gov.tw/wmts/EMAP/default/GoogleMapsCompatible/{z}/{y}/{x}"

    # 3. 加入圖層
    folium.TileLayer(
        tiles=nlsc_url,
        attr="國土測繪中心",
        name="Taiwan e-Map"
    ).add_to(m)

    # 4. 將地圖轉為 HTML 字串回傳 (而不是存成檔案)
    return m.get_root().render()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)