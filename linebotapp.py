from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

app = Flask(__name__)

line_bot_api = LineBotApi('bdEbnCAgdSE65B3/+Jha1LPxjUh/22T65vgOQjdmrJr/XdSQUAFHusJvtRb1XhuUGph810V3UZCG8hOPTB6TeVzp9Wj/hTkkEjij4qdJLLYt1YWhM2tr9riZBxzzQWkZspyvDRRpHZy7nG3FOVZCLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e6cc86689e3d9ca94205754ad263d268')
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

def update_alert(deviceId, setData):
    data = {'setData': setData}
    resp = requests.post('http://127.0.0.1:21090/device/' + deviceId, json=data)
    return resp.json()

def alert_remove(deviceId):
    resp = requests.get('http://127.0.0.1:21090/alert_remove/' + deviceId)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    ## for DM
    if event.source.type == 'user':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(event.message.text))
        )
    ## for group message
    elif event.source.type == 'group':
        print(event.source)
        print(dir(event.source))
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
                setData = dict()
                setData['triggerEnable'] = True
                setData['triggerRule'] = triggerRule
                setData['triggerValue'] = triggerValue
                update_alert(deviceId, setData)
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
                DeviceStore = get_device_store()
                try:
                    arg_list = msg_text.split(' ')[1:]
                    deviceId = arg_list[0]
                except:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請使用此格式\n?警報 [Device ID]")
                    )
                    return
                if deviceId not in DeviceStore:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="該裝置不存在")
                    )
                    return
                if 'triggerEnable' not in DeviceStore[deviceId]:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="裝置 {0}({1}) 警報尚未設定".format(deviceId, DeviceStore[deviceId]['deviceName']))
                    )
                else:
                    t_rule = DeviceStore[deviceId]['triggerRule']
                    t_value = DeviceStore[deviceId]['triggerValue']
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='警報觸發規則: (當前數值) {t_rule} {t_value}'.format(**locals()))
                    )


def run():
    app.run(host='0.0.0.0', debug=True ,port=21190, use_reloader=False, ssl_context=('fullchain.pem', 'privkey.pem'))

if __name__ == "__main__":
    run()