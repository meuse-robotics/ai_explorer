from flask import Flask, request, jsonify
import os
import base64
import requests
import json

# Flaskアプリケーションを初期化
app = Flask(__name__)

# 画像の保存先ディレクトリ
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ディレクトリが無ければ作成

# 画像アップロード用のエンドポイント（POSTのみ許可）
@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        # 画像の取得と検証
        if "image" not in request.files:
            return jsonify({"error": "画像ファイルが見つかりません"}), 400

        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"error": "ファイル名が空です"}), 400

        # 保存パスを生成
        save_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(save_path)

        # Base64に変換
        with open(save_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        detect_str = request.form.get("detect")  # フォームデータとして受け取る
        detect = json.loads(detect_str)          # JSON文字列 → dict に戻す
        print(detect)

        # ----------- 各プロンプト ----------- #
        prompt = f"""
あなたは前方カメラの画像をもとに目標(マグカップ)に向かって移動するロボットです。

以下はYOLOで検出した目標物の情報です:
{detect}

- 判定ルール（擬似コード）

if h > 100:
    action = "stop"
    angle_deg = 0
    forward_cm = 0
else:
    if cx < 130:
        action = "left"
        angle_deg = 5
        forward_cm = 0
    elif cx >190:
        action = "right"
        angle_deg = 5
        forward_cm = 0
    else:
        action = "forward"
        angle_deg = 0
        forward_cm = 5

- 出力形式（必ずJSONで返すこと）
{{
  "action": "stop | left | right | forward | back",
  "angle_deg": 数値,
  "forward_cm": 数値,
  "report": "任意の日本語で状況説明",
  "comment": "補足説明"
}}
"""

        # ----------- 共通ペイロード ----------- #
        payload = {
            "model": "qwen2.5vl:7b",
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }

        # ----------- APIリクエスト ----------- #
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response_data = response.json()
        
        return jsonify({"result": response_data["response"]})
        
    except Exception as e:
        print("エラー発生:", str(e))
        return jsonify({"error": str(e)}), 500

# サーバーの起動設定（全ネットワークからアクセス可能）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)




