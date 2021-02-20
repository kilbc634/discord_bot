from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
from setting import *

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)
groupId_reporter = 'C59f111fe80e1a8364c279aa11a42f2c4'
#groupId_reporter = 'Cd5279b85d7161334726118757342f693'
uesrId_owner = 'U0ce5a329035e3e684efbe387bec539c9'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@app.route("/report_group/<groupId>", methods=['POST'])
def report_group(groupId):
    data = request.json
    msg = data['message']
    line_bot_api.push_message(
        groupId,
        TextSendMessage(text=msg)
    )
    return 'OK', 200

@app.route("/alert_group/<groupId>", methods=['POST'])
def alert_group(groupId):
    data = request.json
    msg = data['message']
    line_bot_api.push_message(
        groupId,
        TextSendMessage(text='==========')
    )
    line_bot_api.push_message(
        groupId,
        TextSendMessage(text=msg)
    )
    line_bot_api.push_message(
        groupId,
        TextSendMessage(text='==========')
    )
    return 'OK', 200

def get_device_store():
    resp = requests.get('http://127.0.0.1:21090/device_store')
    return resp.json()

def alert_get(deviceId):
    resp = requests.get('http://127.0.0.1:21090/alert_get/' + deviceId)
    return resp.json()

def alert_add(deviceId, alertData):
    data = {'alertData': alertData}
    resp = requests.post('http://127.0.0.1:21090/alert_add/' + deviceId, json=data)
    return resp.json()

def alert_remove(deviceId):
    resp = requests.get('http://127.0.0.1:21090/alert_remove/' + deviceId)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    ## for DM
    if event.source.type == 'user':
        user_name = line_bot_api.get_profile(event.source.user_id).display_name
        msg_text = event.message.text
        if msg_text.find('ping') == 0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='pong')
            )
        else:
            data = {
                'sender': '[LINE] ' + user_name,
                'user': '407554740906360833',
                'message': msg_text
            }
            resp = requests.post('http://127.0.0.1:21090/message_user', json=data)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='OK!')
            )
    ## for group message
    elif event.source.type == 'group':
        # print(event.source)
        # print(dir(event.source))
        if event.source.group_id == groupId_reporter:
            msg_text = event.message.text
            if msg_text.find('?裝置') == 0:
                DeviceStore = get_device_store()
                device_id_name = list()
                for deviceId in DeviceStore:
                    deviceName = DeviceStore[deviceId]['deviceName']
                    device_id_name.append('ID: {0}, NAME: {1}'.format(deviceId, deviceName))
                if len(device_id_name) == 0:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='No devices is active')
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='\n'.join(device_id_name))
                    )

            if msg_text.find('!警報') == 0:
                DeviceStore = get_device_store()
                try:
                    mathIcon = ['>', '>=', '=', '<=', '<']
                    arg_list = msg_text.split(' ')[1:]
                    deviceId = arg_list[0]
                    triggerRule = arg_list[1]
                    if triggerRule not in mathIcon:
                        raise SyntaxError("[FAIL] I hope these math icons " + str(mathIcon))
                    triggerValue = float(arg_list[2])
                except:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請使用此格式\n!警報 [Device ID] {0} [Vlaue]\n(刪除警報則使用 !R_ALERT 指令)".format(str(mathIcon).replace("'", "").replace(", ", "/")))
                    )
                    return
                if deviceId not in DeviceStore:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="該裝置不存在")
                    )
                    return
                alertData = dict()
                alertData['triggerRule'] = triggerRule
                alertData['triggerValue'] = triggerValue
                alert_add(deviceId, alertData)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="裝置 {0}({1}) 警報設定完成".format(deviceId, DeviceStore[deviceId]['deviceName']))
                )

            if msg_text.find('!刪警報') == 0:
                DeviceStore = get_device_store()
                try:
                    arg_list = msg_text.split(' ')[1:]
                    deviceId = arg_list[0]
                except:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請使用此格式\n!刪警報 [Device ID]")
                    )
                    return
                if deviceId not in DeviceStore:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="該裝置不存在")
                    )
                    return
                alert_remove(deviceId)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="裝置 {0}({1}) 警報已被刪除".format(deviceId, DeviceStore[deviceId]['deviceName']))
                )

            if msg_text.find('?警報') == 0:
                try:
                    arg_list = msg_text.split(' ')[1:]
                    deviceId = arg_list[0]
                except:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請使用此格式\n?警報 [Device ID]")
                    )
                    return
                alertData = alert_get(deviceId)
                if 'errorData' in alertData:
                    if alertData['errorData'].find('Not found') >= 0:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="該裝置不存在")
                        )
                        return
                    elif alertData['errorData'].find('Not set') >= 0:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="裝置警報尚未設定\n可以嘗試使用指令 !警報 ...")
                        )
                        return
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="未知錯誤")
                        )
                        return
                else:
                    replyText = "警報觸發規則:"
                    for alert in alertData['alertData']:
                        triggerRule = alert['triggerRule']
                        triggerValue = alert['triggerValue']
                        replyText += "\n(當前數值) {triggerRule} {triggerValue}".format(**locals())
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=replyText)
                    )


def run():
    app.run(host='0.0.0.0', debug=True ,port=21190, use_reloader=False, ssl_context=('fullchain.pem', 'privkey.pem'))

if __name__ == "__main__":
    run()