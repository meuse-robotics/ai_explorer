from flask import Flask, request, jsonify
import os
import base64
import requests
import json
import re

# Flaskアプリケーションを初期化
app = Flask(__name__)

# 画像の保存先ディレクトリ
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ディレクトリが無ければ作成

# 画像アップロード用のエンドポイント（POSTのみ許可）
@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        # リクエストに画像ファイルが含まれているかチェック
        if "image" not in request.files:
            return jsonify({"error": "画像ファイルが見つかりません"}), 400

        image_file = request.files["image"]
        
        # ファイル名が空でないかチェック
        if image_file.filename == "":
            return jsonify({"error": "ファイル名が空です"}), 400

        # 保存先のパスを生成して保存
        save_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(save_path)

        # 画像ファイルをBase64形式にエンコード
        with open(save_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # ----------- プロンプト ----------- #
        prompt = (
            f"""
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
  "angle_deg": 数値（左右旋回の場合のみ）,
  "forward_cm": 数値（前進の場合のみ）,
  "comment": ""
}}'''
"""
        )

        # ----------- ペイロード ----------- #
        payload = {
            "model": "qwen2.5vl:7b",
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }

        # ----------- APIリクエスト ----------- #
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response_data = response.json()

        return jsonify({"result": response_data.get("response", "")})

    except Exception as e:
        print("エラー発生:", str(e))
        return jsonify({"error": str(e)}), 500
  
# サーバーの起動設定（全ネットワークからアクセス可能）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
