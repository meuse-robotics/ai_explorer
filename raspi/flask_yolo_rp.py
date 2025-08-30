import requests
import io
from camera_usb import Camera
from servo import Servo
import time
from yolo_detector import YoloDetector
import json

class FlaskYolo:
    
    def __init__(self):
        # drive
        self.drive = Servo()
        # camera
        self.cam = Camera()
        # 状態管理
        self.is_moving = False
        # YOLO
        self.yolo = YoloDetector()

    # LLMに問い合わせ
    def send_to_llm(self, detect):
        # 直接ファイルを開いて送信
        with open(self.image_path, "rb") as f:
            files = {
                "image": ("captured.jpg", f, "image/jpeg")
            }
            data = {
                "detect" : detect
            }
            response = requests.post("http://192.168.1.100:5000/upload", files=files, data=data)
        print("サーバーの応答:", response.json())
        return response.json()

    @staticmethod
    def extract_json_from_content(content):
        import re
        import json
        match = re.search(r'\{.*?\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print("JSONとして読み込めませんでした:", e)
        return None

    def run(self):
        self.running = True
        try:
            # while self.running:
                if self.is_moving == False:
                    self.image_path = self.cam.take_photo()  # 保存された画像ファイルのパスが返る
                    detect = self.yolo.detect_cup(self.image_path)
                    if detect is None:
                        print("マグカップを検出できませんでした")
                        return
                    time.sleep(1)
                    response = self.send_to_llm(detect)
                    result = response.get("result", "")
                    result_dict = self.extract_json_from_content(result)

                    self.is_moving = True
                    if result_dict:
                        self.is_moving = True
                        if result_dict["action"] == "forward":
                            self.drive.action(self, "forward", result_dict["angle_deg"], result_dict["forward_cm"])
                        elif result_dict["action"] == "right":
                            self.drive.action(self, "right", result_dict["angle_deg"], result_dict["forward_cm"])
                        elif result_dict["action"] == "left":
                            self.drive.action(self, "left", result_dict["angle_deg"], result_dict["forward_cm"])
                        else:
                            self.drive.action(self, "stop", result_dict["angle_deg"], result_dict["forward_cm"])
                    else:
                        print("JSONの抽出または解析に失敗しました")
            
        except KeyboardInterrupt:
            print("終了します。")

if __name__ == "__main__":
    
    exp = FlaskYolo()
    exp.run()