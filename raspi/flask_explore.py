import requests
import io
from camera_usb import Camera
from servo import Servo
import time

class FlaskExplore:
    
    def __init__(self):
        # drive
        self.drive = Servo()
        # camera
        self.cam = Camera()
        # 状態管理
        self.is_moving = False

    # LLMに問い合わせ
    def send_to_llm(self):
        image_path = self.cam.take_photo()  # 保存された画像ファイルのパスが返る

        # 直接ファイルを開いて送信
        with open(image_path, "rb") as f:
            files = {
                "image": ("photo.jpg", f, "image/jpeg")
            }
            response = requests.post("http://192.168.1.100:5000/upload", files=files)
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
                    time.sleep(1)
                    response = self.send_to_llm()
                    result = response.get("result", "")
                    print(result)
                    result_dict = self.extract_json_from_content(result)
                    if result_dict:
                        print(result_dict["comment"])
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
                    time.sleep(5)
        except KeyboardInterrupt:
            self.running = False
            print("終了します。")

if __name__ == "__main__":
    
    exp = FlaskExplore()
    exp.run()