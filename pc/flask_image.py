from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 保存先ディレクトリ
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "画像ファイルが見つかりません"}), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({"error": "ファイル名が空です"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    image_file.save(save_path)

    return jsonify({"message": "画像を受信しました", "filename": image_file.filename})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
