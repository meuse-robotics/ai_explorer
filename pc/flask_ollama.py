from flask import Flask, request, jsonify
import os
import base64
import requests

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

        # OllamaのVLMモデルに送信するペイロードを作成
        payload = {
            "model": "gemma3:12b",
            "prompt": "何が写っていますか バーガーキングのカップは左右方向でどの辺にありますか",
            "images": [image_data],  # Base64エンコードした画像を渡す
            "stream": False  # ストリームではなく一括応答を要求
        }

        # OllamaサーバーへPOSTリクエストを送信
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response_data = response.json()

        # モデルの応答（説明文）だけを抽出してクライアントへ返す
        return jsonify({"result": response_data["response"]})

    except Exception as e:
        # 予期せぬエラーが発生した場合の処理
        print("エラー発生:", str(e))
        return jsonify({"error": str(e)}), 500

# サーバーの起動設定（全ネットワークからアクセス可能）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
