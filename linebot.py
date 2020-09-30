from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import random

app = Flask(__name__)

line_bot_api = LineBotApi('bdEbnCAgdSE65B3/+Jha1LPxjUh/22T65vgOQjdmrJr/XdSQUAFHusJvtRb1XhuUGph810V3UZCG8hOPTB6TeVzp9Wj/hTkkEjij4qdJLLYt1YWhM2tr9riZBxzzQWkZspyvDRRpHZy7nG3FOVZCLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e6cc86689e3d9ca94205754ad263d268')


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    pretty_text = 'test'
    print(event.message.text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(event.message.text))
    )

def run():
    app.run(host='0.0.0.0', debug=True ,port=21190, use_reloader=False, ssl_context=('fullchain.pem', 'privkey.pem'))

if __name__ == "__main__":
    run()