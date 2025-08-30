import os
import base64
import time
from picamera2 import Picamera2

class Camera:
    def __init__(self, save_dir="images", resolution=(320, 240)):
        self.save_dir = save_dir
        self.resolution = resolution
        
        # カメラ初期化
        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration(main={"size": resolution})
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(2)  # カメラウォームアップ

    def take_photo(self):
        try:
            # 保存パスを設定
            image_path = os.path.join(self.save_dir, f"captured.jpg")

            # 撮影して保存
            self.picam2.capture_file(image_path)

            return image_path

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None

if __name__ == "__main__":
    cam = Camera()
    b64 = cam.take_photo()
    if b64:
        print("撮影成功、base64データを取得しました。")
    else:
        print("撮影に失敗しました。")
