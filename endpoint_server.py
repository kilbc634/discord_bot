# -*- coding: UTF-8 -*-
from flask import Flask, jsonify, request, send_from_directory
import threading
import requests
from datetime import datetime, timezone, timedelta
from discord_bot import client as DiscordClient
from discord_bot import userId_owner

EndPoint = Flask('EndPoint')

@EndPoint.route("/")
def welcome():
    return "This is EndPoint Service of Discord bot" , 200

@EndPoint.route("/message_user", methods=["POST"])
def message_user():
    data = request.json
    sender = data['sender']
    user = data['user']
    message = data['message']
    if user == 'me':
        userId = userId_owner
    else:
        userId = int(user)
    DiscordClient.loop.create_task(DiscordClient.send_DM(userId, 'from {sender}:\n{message}'.format(**locals())))
    return 'OK', 200

#############################################################
#
#       Support for IoT Device part
#
#############################################################

DeviceStore = dict()
AlertThreads = list()

def get_timestamp(utc=8):
    dt_now = datetime.now(tz=timezone(timedelta(hours=utc)))
    return int(dt_now.timestamp())

def check_timeout(deviceId, timeout=60):
    timestamp = DeviceStore[deviceId]['timestamp']
    now = get_timestamp()
    if now > int(timestamp) + timeout:
        return True
    else:
        return False

def alert_trigger(deviceId):
    name = DeviceStore[deviceId]['deviceName']
    vlaue = DeviceStore[deviceId]['value']
    t_rule = DeviceStore[deviceId]['triggerRule']
    t_value = DeviceStore[deviceId]['triggerValue']
    alert_text = '[Alert] 裝置 <{deviceId}>({name}) 被觸發了!\n原因: {vlaue}(當前數值) {t_rule} {t_value}'.format(**locals())
    ## for discord bot
    DiscordClient.loop.create_task(
        DiscordClient.send_DM(userId_owner, alert_text)
    )
    ## for line bot
    requests.post(LINE_HOST + '/alert_group/' + linebotapp.groupId_reporter,
        json={"message": alert_text}
    )

def timeout_trigger(deviceId, timeout_status=True):
    name = DeviceStore[deviceId]['deviceName']
    if timeout_status:
        alert_text = '[Timeout] 裝置 <{deviceId}>({name}) 失去回應!'.format(**locals())
    else:
        alert_text = '[Timeout] 裝置 <{deviceId}>({name}) 恢復回應!'.format(**locals())
    ## for discord bot
    DiscordClient.loop.create_task(
        DiscordClient.send_DM(userId_owner, alert_text)
    )
    ## for line bot
    requests.post(LINE_HOST + '/alert_group/' + linebotapp.groupId_reporter,
        json={"message": alert_text}
    )

def alert_thread(deviceId):
    timeouted = False
    while True:
        delayTime = 3
        if deviceId not in DeviceStore:  # will stop this Thread
            break
        if 'triggerEnable' in DeviceStore[deviceId]:
            triggerEnable = DeviceStore[deviceId]['triggerEnable']
            triggerRule = DeviceStore[deviceId]['triggerRule']
            triggerValue = DeviceStore[deviceId]['triggerValue']
            value = DeviceStore[deviceId]['value']
            if triggerRule == '>':
                if value > triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
            elif triggerRule == '>=':
                if value >= triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
            elif triggerRule == '=':
                if value == triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
            elif triggerRule == '<=':
                if value <= triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
            elif triggerRule == '<':
                if value < triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
        if check_timeout(deviceId):
            if timeouted == False:
                timeout_trigger(deviceId)
            timeouted = True
            if 'triggerEnable' in DeviceStore[deviceId]:
                DeviceStore[deviceId]['triggerEnable'] = False
            delayTime = 3
        elif timeouted:
            timeout_trigger(deviceId, timeout_status=False)
            timeouted = False
            if 'triggerEnable' in DeviceStore[deviceId]:
                DeviceStore[deviceId]['triggerEnable'] = True
            delayTime = 3
        time.sleep(delayTime)

@EndPoint.route("/device/<deviceId>", methods=["POST"])
def device_post(deviceId):
    data = request.json
    if 'value' in data['setData']:
        data['setData']['value'] = float(data['setData']['value'])  # string to float for device value
    if deviceId not in DeviceStore:
        DeviceStore[deviceId] = data['setData']
        DeviceStore[deviceId]['timestamp'] = get_timestamp()
        alertThread = threading.Thread(target=alert_thread, args=(deviceId,))
        AlertThreads.append(alertThread)
        alertThread.start()
    else:
        DeviceStore[deviceId]['timestamp'] = get_timestamp()
        for key in data['setData']:
            DeviceStore[deviceId][key] = data['setData'][key]
    deviceData = DeviceStore[deviceId]
    return jsonify({'currentData': deviceData}), 200

@EndPoint.route("/device/<deviceId>", methods=["GET"])
def device_get(deviceId):
    if deviceId not in DeviceStore:
        return jsonify({'errorData': 'Not found device [{0}]'.format(deviceId)}) , 202
    deviceData = DeviceStore[deviceId]
    return jsonify({'currentData': deviceData}), 200

@EndPoint.route("/device/<deviceId>", methods=["DELETE"])
def device_delete(deviceId):
    if deviceId not in DeviceStore:
        return jsonify({'errorData': 'Not found device [{0}]'.format(deviceId)}) , 202
    del DeviceStore[deviceId]
    return '', 204

@EndPoint.route("/device_store", methods=["GET"])
def device_all():
    return jsonify(DeviceStore), 200

@endPoint.route("/alert_remove/<deviceId>", methods=["GET"])
def alert_remove(deviceId):
    try:
        del DeviceStore[deviceId]['triggerEnable']
        del DeviceStore[deviceId]['triggerRule']
        del DeviceStore[deviceId]['triggerValue']
    except KeyError:
        pass
    return '', 204

#############################################################
#
#       Support for Robot Framework part
#
#############################################################

NodeDataStock = dict()

@EndPoint.route("/tempdata")
def index():
    return "Please don't come here" , 200

@EndPoint.route("/tempdata/create/<nodeName>" , methods=["POST"])
def createNode(nodeName):
    '''
    resp:
        {
            "data": {
                    "created": {
                        "id": "nodeName"
                    }
            }
        }
    '''
    if nodeName in NodeDataStock:
        return jsonify({"error":{"message":"Node name already exists"}}) , 200
    try:
        NodeDataStock[nodeName] = request.json
    except:
        return "ERRORS" , 200
    return jsonify({"data":{"created":{"id":nodeName}}}) , 200

@EndPoint.route("/tempdata/call/<nodeName>" , methods=["GET"])
def callNode(nodeName):
    '''
    resp:
        {
            "data": {
                "nodeContent": {dict....} ,
                "id": "nodeName"
            }
        }
    '''
    if nodeName not in NodeDataStock:
        return jsonify({"error":{"message":"Node name does not exist"}}) , 200
    res = NodeDataStock[nodeName]
    return jsonify({"data":{"nodeContent":res,"id":nodeName}})

@EndPoint.route("/report/<path:path>")
def view_report(path):
    return send_from_directory('report', path)

#############################################################

def run():
    EndPoint.run(host='0.0.0.0', debug=True, port=21090, use_reloader=False)

if __name__=='__main__':
    run()
