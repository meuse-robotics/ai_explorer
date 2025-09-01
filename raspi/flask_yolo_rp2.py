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
    def send_to_llm(self, action, angle, distance):
        with open(self.image_path, "rb") as f:
            files = {
                "image": ("captured.jpg", f, "image/jpeg")
            }
            data = {
                "detect": json.dumps({
                "action": action,
                "angle": angle,
                "distance": distance
            })
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
                    w, h, cx, cy = detect
                    pos = cx / 320
                    dist = 42 - 20 * h / 73
                    if dist < 10:
                        action = "stop"
                        angle = 0
                        distance = 0
                    else:
                        if pos < 0.4:
                            action = "left"
                            angle = (0.5 - pos) * 20
                            distance = 0
                        elif pos > 0.6:
                            action = "right"
                            angle = (pos-0.5) * 20
                            distance = 0
                        else:
                            action = "forward"
                            angle = 0
                            distance = dist - 10

                    try:
                        time.sleep(1)
                        response = self.send_to_llm(action, angle, distance)
                    except KeyboardInterrupt:
                        print("Ctrl+Cで中断されました")
                    result = response.get("result", "")
                    result_dict = self.extract_json_from_content(result)

                    self.is_moving = True
                    self.drive.action(self, action, angle, distance)

                    print(result_dict)
                                
        except KeyboardInterrupt:
            print("終了します。")

if __name__ == "__main__":
    
    exp = FlaskYolo()
    exp.run()
