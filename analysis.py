import os
import planetary_computer
import pystac_client
import rasterio
from rasterio.plot import show
from rasterio.transform import from_origin

# 連接 Microsoft Planetary Computer STAC API
catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

# ✅ 搜索台灣範圍的 Sentinel-2 遙感影像
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[120.0, 21.5, 122.0, 25.5],  # ✅ 設定地理範圍 (台灣)
    datetime="2023-01-01/2023-12-31",  # ✅ 修正 datetime 格式錯誤，補上逗號
)

# 取得符合條件的影像
items = list(search.items())
if items:
    item = items[0]
    signed_asset = planetary_computer.sign(item.assets["B08"]).href  # 取得紅光波段影像

    # ✅ 讀取影像數據，確保在 `with` 內部
    with rasterio.open(signed_asset) as dataset:
        image_array = dataset.read(1)  # 讀取影像數據
        profile = dataset.profile  # 取得原始影像的 metadata

        # ✅ 更新 metadata 以確保儲存正確的 GeoTIFF
        profile.update(
            dtype=rasterio.uint16,  # 影像類型
            count=1,  # 單波段
            compress="lzw"  # 使用 LZW 壓縮
        )

        # ✅ 設定輸出 GeoTIFF
        output_path = "output_image.tif"
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(image_array, 1)  # 寫入波段數據

        print(f"✅ 台灣範圍影像已成功儲存為 {output_path}")

    # ✅ 檢查影像是否正確儲存
    if os.path.exists(output_path):
        print(f"✅ {output_path} 存在，準備上傳到 GitHub Actions Artifacts")
    else:
        print(f"❌ 錯誤：{output_path} 未成功儲存，請檢查程式碼！")

else:
    print("❌ 未找到符合條件的 Sentinel-2 影像")
