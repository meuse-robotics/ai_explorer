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
        
        command = request.form["command"]
        print(command)

        # ----------- プロンプト ----------- #
        prompt = f"""
            あなたは前方カメラの画像をもとに移動するロボットです。
            ロボットへの動作命令 {command} に従い、コマンド、または報告を作成してください。
            
            
            1. 報告のみ → "report": "任意の日本語文章", "action": "stop"
            2. 右を向く → "action": "right", "angle_deg": 数値, "forward_cm": 数値
            3. 左を向く → "action": "left", "angle_deg": 数値, "forward_cm": 数値
            4. 直進 → "action": "forward", "angle_deg": 数値, "forward_cm": 数値
            5. バック → "action": "back", "angle_deg": 数値, "forward_cm": 数値

            以下のJSON形式で返答してください:
            ```json
            {{
                "report":"",
                "action": "left|right|forward|stop",
                "angle_deg": 数値（前進の場合は0）,
                "forward_cm": 数値（左右旋回の場合は0）,
                "comment": ""
            }}'''
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
