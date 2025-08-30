from flask import Flask

app = Flask(__name__)  # アプリケーションのインスタンスを作成

@app.route("/")  # ルートURLにアクセスした時の処理
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
