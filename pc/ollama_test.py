import requests
import base64

# モデル名とエンドポイント
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5vl:7b"
IMAGE_PATH = "test.jpg"

# 画像をbase64にエンコード
def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# base64化した画像
image_base64 = image_to_base64(IMAGE_PATH)

# 送信データ
payload = {
    "model": MODEL_NAME,
    "prompt": "この画像には何が写っていますか？",
    "images": [image_base64],
    "stream": False
}

# APIにPOST
response = requests.post(OLLAMA_URL, json=payload)

# 結果を表示
if response.status_code == 200:
    result = response.json()
    print("応答内容:")
    print(result.get("response", "[応答なし]"))
else:
    print(f"エラーが発生しました: {response.status_code}")
    print(response.text)
