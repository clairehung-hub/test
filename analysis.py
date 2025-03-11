import planetary_computer
import pystac_client
import rasterio
from rasterio.plot import show

# 連接 Microsoft Planetary Computer STAC API
catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

# 搜索 Sentinel-2 遙感影像
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[121.673, 24.91571, 121.73, 24.23321],  # 設定地理範圍 (taiwan)
    datetime="2025-03-01/2025-03-10",
)

# 取得符合條件的影像
items = list(search.items())
if items:
    item = items[0]
    signed_asset = planetary_computer.sign(item.assets["B08"]).href  # 取得紅光波段影像

    # ✅ 確保在 `with` 內部讀取數據，防止 "Dataset is closed" 錯誤
    with rasterio.open(signed_asset) as dataset:
        image_array = dataset.read(1)  # 讀取影像數據
        print(dataset)
        show(dataset)  # 顯示影像
        image_array.tofile("output_image.tif")  # ✅ 保存影像到本地
        print("✅ 影像已成功儲存到 output_image.tif")

else:
    print("❌ 未找到符合條件的 Sentinel-2 影像")
