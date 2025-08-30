import os
from dotenv import load_dotenv # .envファイルから環境変数を読み込む
from openai import OpenAI # OpenAI API用のライブラリをインポート

load_dotenv() # .envファイルを読み込む
api_key = os.getenv('OPENAI_API_KEY') # 環境変数からAPIキーを取得
openai = OpenAI() # OpenAIクライアントを初期化

# ユーザーからの入力（メッセージ）を送る
response = openai.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "あなたは親切な日本語アシスタントです。"},
        {"role": "user", "content": "生成AIについて100字程度で教えて"}
    ]
)

# 応答を表示
reply = response.choices[0].message.content
print("ChatGPTの応答:\n", reply)
