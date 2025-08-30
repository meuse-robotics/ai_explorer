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
        
        # YOLO情報取得
        detect_str = request.form.get("detect")  # フォームデータとして受け取る
        detect = json.loads(detect_str)          # JSON文字列 → dict に戻す
        print(detect)

        # ----------- 各プロンプト ----------- #
        prompt = f"""
あなたは前方カメラの画像をもとに目標(マグカップ)に向かって移動するロボットです。

以下はYOLOで目標物を検出し決定した動作の情報です:
{detect}
カメラ画像と動作情報から、周囲の状況と動作に関する簡潔なレポートを作成してください

- 出力形式（必ずJSONで返すこと）
{{
  "report": "任意の日本語で状況説明",
}}
"""

        # ----------- ペイロード ----------- #
        payload = {
            "model": "gemma3:4b",
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

