import os
import re
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from openai import OpenAI

app = Flask(__name__)

# --- 設定 ---
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def is_chinese(text: str) -> bool:
    """判斷文字是否包含中文"""
    return bool(re.search(r"[一-鿿]", text))


def translate_zh_to_en(text: str) -> str:
    prompt = f"""你是一位專業的英文翻譯和英語教學老師。

使用者輸入了以下中文句子：
「{text}」

請依照以下格式回覆（不要加多餘的標題或分隔線）：

📝 英文翻譯：
[翻譯結果]

📚 關鍵單字與片語：
• [單字/片語 1]（詞性）：中文意思
  例句：English example sentence.
• [單字/片語 2]（詞性）：中文意思
  例句：English example sentence.
• [單字/片語 3]（詞性）：中文意思
  例句：English example sentence.

請選出 3～5 個最值得學習的單字或片語，優先選擇較進階或實用的表達方式。"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def translate_en_to_zh(text: str) -> str:
    prompt = f"""你是一位專業的英中翻譯和英語教學老師。

使用者輸入了以下英文句子：
"{text}"

請依照以下格式回覆（不要加多餘的標題或分隔線）：

📝 繁體中文翻譯：
[翻譯結果]

✅ 語法檢查：
[若句子正確，說明「語法正確」並簡單說明句型結構；若有錯誤，指出錯誤並給出修正版本]

💡 相似句型：
• [相同語意的替換句型 1]
• [相同語意的替換句型 2]
• [相同語意的替換句型 3]

請給出 2～3 個相似句型，盡量涵蓋不同語氣或正式程度的表達。"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip()

    if not user_text:
        return

    try:
        if is_chinese(user_text):
            reply = translate_zh_to_en(user_text)
        else:
            reply = translate_en_to_zh(user_text)
    except Exception as e:
        reply = f"⚠️ 發生錯誤，請稍後再試。\n{str(e)}"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)],
            )
        )


@app.route("/", methods=["GET"])
def index():
    return "LINE Translation Bot is running! 🚀"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
