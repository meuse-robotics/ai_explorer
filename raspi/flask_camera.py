import requests
from camera_usb import Camera

cam = Camera()
image_path = cam.take_photo()  # 保存された画像ファイルのパスが返る

# 直接ファイルを開いて送信
with open(image_path, "rb") as f:
    files = {
        "image": ("photo.jpg", f, "image/jpeg")
    }
    response = requests.post("http://192.168.1.100:5000/upload", files=files)

print("サーバーの応答:", response.json())
