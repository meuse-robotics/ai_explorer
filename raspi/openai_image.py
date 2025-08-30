import os
from dotenv import load_dotenv # .envファイルから環境変数を読み込む
from openai import OpenAI # OpenAI API用のライブラリをインポート
import base64

load_dotenv() # .envファイルを読み込む
api_key = os.getenv('OPENAI_API_KEY') # 環境変数からAPIキーを取得
openai = OpenAI() # OpenAIクライアントを初期化

# 画像ファイルをbase64にエンコード
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 入力画像
image_path = "./test.jpg"
base64_image = encode_image(image_path)

# 画像認識プロンプト（内容を説明させる）
response = openai.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "この画像に何が写っていますか？"},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }},
            ],
        }
    ],
)

# 結果表示
print(response.choices[0].message.content)
