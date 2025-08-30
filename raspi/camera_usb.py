import cv2
import time
import base64
import os
#import datetime

class Camera:
    def __init__(self, save_dir="images", resolution=(320, 240), camera_index=0):
        self.save_dir = save_dir
        self.resolution = resolution
        self.camera_index = camera_index

    def take_photo(self):
        try:
            # カメラ初期化（毎回）
            cap = cv2.VideoCapture(self.camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            time.sleep(1)  # カメラのウォームアップ

            # 撮影
            ret, frame = cap.read()
            cap.release()

            if not ret:
                print("カメラから画像を取得できませんでした")
                return None

            # 保存
            #timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            #image_path = os.path.join(self.save_dir, f"captured_{timestamp}.jpg")
            image_path = os.path.join(self.save_dir, f"captured.jpg")
            cv2.imwrite(image_path, frame)
            print(f"{image_path} に保存しました")

            return image_path

        except KeyboardInterrupt:
            print("Ctrl+Cで中断されました")
            raise
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
