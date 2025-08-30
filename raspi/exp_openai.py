import os
from dotenv import load_dotenv # .envファイルから環境変数を読み込む
from openai import OpenAI # OpenAI API用のライブラリをインポート
import requests
from camera_usb import Camera
from servo import Servo
import time
import base64

class ExpOpenAI:
    
    def __init__(self):
        # drive
        self.drive = Servo()
        # camera
        self.cam = Camera()
        # AIと通信関連
        load_dotenv() # .envファイルを読み込む
        api_key = os.getenv('OPENAI_API_KEY') # 環境変数からAPIキーを取得
        self.client = OpenAI(api_key=api_key) # OpenAIクライアントを初期化
        # 状態管理
        self.is_moving = False

    # 画像ファイルをbase64にエンコード
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # LLMに問い合わせ
    def send_to_llm(self):
        system_prompt = {
            "role": "system",
            "content":f"""
            あなたは前方カメラの画像をもとに移動するロボットです。
            """
        }
        user_input = {
            "role": "user",
            "content": [
                {"type": "text", "text": f"""
カメラ画像で認識できた物について簡潔に説明して(report)から アクション指令をだします。
バーガーキングのカップが見えたら、
ステップ１：カップ縦方向が画面サイズの2/3より大きい
    YES : ステップ２へ
    NO : ステップ３へ
ステップ２：
     `"action": "stop"`
ステップ３：
    そのカップが画面全体で左右方向どの辺(A:左側、B:中央付近、C:右側)の位置にあるか
    - 位置 左側 → `"action": "left"`, `"angle_deg": 5～10`
    
    - 位置 中央付近 → `"action": "forward"`, `"forward_cm": 0～10`
    
    - 位置 右側 → `"action": "right"`, `"angle_deg": 5～10`

次のJSON形式で返答してください：
```json
{{
  "report":"",
  "action": "left|right|forward|stop",
  "angle_deg": 数値（前進の場合は0）,
  "forward_cm": 数値（左右旋回の場合は0）,
  "comment": ""
}}'''
"""
                },
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{self.encode_image(self.cam.take_photo())}"
                }},
            ],
        }
        messages_to_send = [system_prompt]  + [user_input]
        
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages = messages_to_send,
        )
        llm_message = response.choices[0].message.content
        
        return llm_message

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
        try:
            if self.is_moving == False:
                time.sleep(1)
                result = self.send_to_llm()
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
                print("終了します。")

if __name__ == "__main__":
    exp = ExpOpenAI()
    exp.run()

