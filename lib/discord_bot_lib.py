# -*- coding: UTF-8 -*-
import subprocess
import os
import time
from datetime import datetime, timezone, timedelta
import threading
import requests
from lxml import etree
from setting import *
from endpoint_server import DeviceStore
from lib import redis_lib
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

FunctionInfo = {
    "?HELP": "Format:\n?HELP [(Optional: command)]",
    "!CMD": "Format:\n!CMD [logout|(etc...)]",
    "?HOST": "Format:\n?HOST",
    "!SAY": "Format:\n!SAY [message]",
    "?DEVICE": "Format:\n?DEVICE",
    "!ALERT": "Format:\n!ALERT [device ID] [=|>=|<=|>|<] [vlaue]",
    "!R_ALERT": "Format:\n!R_ALERT [device ID]",
    "?ALERT": "Format:\n?ALERT [device ID]",
    "?MEMBER_LIST": "Format:\n?MEMBER_LIST",
    "?CHANNEL_LIST": "Format:\n?CHANNEL_LIST",
    "!PO": "Format:\n!PO [message]\nAttachment: (Optional: upload one image file)",
    "!TELEGRAM": "Format:\n!TELEGRAM [setup(S)|verify(V)|end(E)] [value]\n(value of setup: Phone number after +886)\n(value of verify: Verify number from Telegram mobile app)"
}

def check_function(content):
    for functionHeader in FunctionInfo:
        if content.startswith(functionHeader):
            return True
    return False

def command_line(client, content, attachments=[], admin=False, messageObj=None):
    output = dict()
    cmdList = content.split(' ')
    functionHeader = cmdList[0]
    if len(cmdList) > 1:
        functionArgs = cmdList[1:]
    else:
        functionArgs = []

    if functionHeader == '!CMD':
        if not admin:
            output['text'] = '貴方に権限がありません'
            return output
        res = system_command(functionArgs[0])
        output['text'] = 'ログアウトを実行します...'

    elif functionHeader == '?HELP':
        helpText = help_message()
        if len(functionArgs) > 0:
            if functionArgs[0] in FunctionInfo:
                helpText = FunctionInfo[functionArgs[0]]
        output['text'] = helpText

    elif functionHeader == '?HOST':
        output['text'] = API_HOST

    elif functionHeader == '!SAY':
        msg = ' '.join(functionArgs)
        client.loop.create_task(
            client.send_message_with_channelId(client.clannelId_onTest, msg)
        )
        output['text'] = '送信しました'

    elif functionHeader == '?DEVICE':
        if len(functionArgs) > 0:
            targetDevice = functionArgs[0]
            if redis_lib.check_device(targetDevice):
                imagePath = create_device_data_image(targetDevice)
                output['file'] = imagePath
                output['text'] = 'デバイスデータを表示します'
            else:
                output['text'] = 'そのデバイスは存在しません'
        else:
            device_id_name = list()
            for deviceId in DeviceStore:
                deviceName = DeviceStore[deviceId]['deviceName']
                device_id_name.append('ID: {0}, NAME: {1}'.format(deviceId, deviceName))
            if len(device_id_name) == 0:
                output['text'] = 'No devices is active'
            else:
                output['text'] = '\n'.join(device_id_name)

    elif functionHeader == '!ALERT':
        if not admin:
            output['text'] = '貴方に権限がありません'
            return output
        try:
            mathIcon = ['>', '>=', '=', '<=', '<']
            deviceId = functionArgs[0]
            triggerRule = functionArgs[1]
            if triggerRule not in mathIcon:
                raise SyntaxError("[FAIL] I hope these math icons " + str(mathIcon))
            triggerValue = float(functionArgs[2])
        except:
            output['text'] = "請使用此格式\n!ALERT [Device ID] {0} [Vlaue]\n(刪除警報則使用 !R_ALERT 指令)".format(str(mathIcon).replace("'", "").replace(", ", "/"))
            return output
        if deviceId not in DeviceStore:
            output['text'] = "そのデバイスは存在しません"
            return output
        DeviceStore[deviceId]['triggerEnable'] = True
        if 'triggers' not in DeviceStore[deviceId]:
            DeviceStore[deviceId]['triggers'] = []
        DeviceStore[deviceId]['triggers'].append({
            'triggerRule': triggerRule,
            'triggerValue': triggerValue
        })
        output['text'] = "裝置 {0}({1}) 警報設定完成".format(deviceId, DeviceStore[deviceId]['deviceName'])

    elif functionHeader == '!R_ALERT':
        if not admin:
            output['text'] = '貴方に権限がありません'
            return output
        try:
            deviceId = functionArgs[0]
        except:
            output['text'] = "請使用此格式\n!R_ALERT [Device ID]"
            return output
        if deviceId not in DeviceStore:
            output['text'] = "該裝置不存在"
            return output
        try:
            del DeviceStore[deviceId]['triggerEnable']
            del DeviceStore[deviceId]['triggers']
        except KeyError:
            output['text'] = "裝置 {0}({1}) 警報尚未設定".format(deviceId, DeviceStore[deviceId]['deviceName'])
            return output
        output['text'] = "裝置 {0}({1}) 警報已被刪除".format(deviceId, DeviceStore[deviceId]['deviceName'])

    elif functionHeader == '?ALERT':
        try:
            deviceId = functionArgs[0]
        except:
            output['text'] = "請使用此格式\n?ALERT [Device ID]"
            return output
        if deviceId not in DeviceStore:
            output['text'] = "該裝置不存在"
            return output
        if 'triggerEnable' not in DeviceStore[deviceId]:
            output['text'] = "裝置 {0}({1}) 警報尚未設定".format(deviceId, DeviceStore[deviceId]['deviceName'])
        else:
            outputText = '警報觸發規則:'
            for alertData in DeviceStore[deviceId]['triggers']:
                triggerRule = alertData['triggerRule']
                triggerValue = alertData['triggerValue']
                outputText += '\n(當前數值) {triggerRule} {triggerValue}'.format(**locals())
            output['text'] = outputText

    elif functionHeader == '?MEMBER_LIST':
        members = client.get_all_members()
        membersList = list()
        for member in members:
            userName = member.display_name
            userId = member.id
            membersList.append('{userName} ({userId})'.format(**locals()))
        output['text'] = '\n'.join(membersList)

    elif functionHeader == '?CHANNEL_LIST':
        channels = client.get_all_channels()
        channelsList = list()
        for channel in channels:
            try:
                channelName = channel.name
                channelId = channel.id
                channelGuild = channel.guild.name
            except:
                continue
            channelsList.append('{channelName} ({channelId}) IN <<{channelGuild}>>'.format(**locals()))
        output['text'] = '\n'.join(channelsList)

    elif functionHeader == '!PO':
        text = ' '.join(functionArgs)
        atts = attachments
        # create node data
        nodeName = str(int(time.time()))
        nodeData = dict()
        nodeData['message'] = text
        if len(atts) > 0:
            nodeData['image'] = atts[0].url
        else:
            nodeData['image'] = ''
        res = requests.post('http://127.0.0.1:21090/tempdata/create/{nodeName}'.format(**locals()), json=nodeData)

        # run robot to send post on FB page
        myDir = os.getcwd()
        process = subprocess.Popen('python3 -m robot -d {myDir}/report -v callNode:"{nodeName}" {myDir}/lib/upload_to_FB.robot'.format(**locals()), shell=True)
        channelId = messageObj.channel.id
        def wait_robot_complated(process, reportChannelId=None):
            returncode = process.wait()
            status, emoji = get_report_status()
            if reportChannelId:
                fileUrl = API_HOST + '/report/log.html'
                reportText = '{emoji} Robot complated [ {status} ]\nreport log: {fileUrl}'.format(**locals())
                client.loop.create_task(
                    client.send_message_with_channelId(reportChannelId, reportText)
                )
        waitingThread = threading.Thread(target=wait_robot_complated, args=(process, channelId), daemon=True)
        waitingThread.start()
        output['text'] = '処理中、少々お待ちください...'

    elif functionHeader == '!TELEGRAM':
        try:
            actionType = functionArgs[0]
            contentValue = functionArgs[1]
        except:
            output['text'] = '語法錯誤!\n' + FunctionInfo['!TELEGRAM']
            return output
        if actionType not in ['setup', 'S', 'verify', 'V', 'end', 'E']:
            output['text'] = '異常的 actionType，請執行 [setup(S)|verify(V)|end(E)]'
            return output

        output['text'] = '執行中....'

        authorId = messageObj.author.id
        if actionType in ['setup', 'S']:
            pass
            # check authorId 是否存在於 endpoint_server/telegram/<authorId>，是則拒絕
            # 否則 create for <authorId>
            # run robot script to submit phone number step
        if actionType in ['verify', 'V']:
            pass
            # send verify code to endpoint_server/telegram/<authorId>
            # robot script will get this data
        if actionType in ['end', 'E']:
            pass
            # send end status to endpoint_server/telegram/<authorId>
            # robot script will self end when getend status

    else:
        text = help_message()
        output['text'] = text
    
    return output

def system_command(command):
    if command == 'logout':
        exit()

def help_message():
    return '\n'.join(FunctionInfo)

def get_report_status():
    myDir = os.getcwd()
    doc = etree.parse(myDir + '/report/output.xml')
    failedTestCount_element = doc.xpath('//statistics/total/stat[text()="All Tests"]')[0]
    failedTestCount = int(failedTestCount_element.get("fail"))
    if failedTestCount > 0:
        return 'FAIL', ':x:'
    else:
        return 'PASS', ':white_check_mark:'

def create_device_data_image(deviceId, folderPath='/res/image/'):
    savePath = os.getcwd() + folderPath + 'device_{0}_{1}.png'.format(deviceId, str(int(time.time())))
    valueList = redis_lib.get_device_value(deviceId, dataLimit=100)
    x = list()
    y = list()
    dt_now = datetime.now(tz=timezone(timedelta(hours=8)))
    for data in valueList:
        value = data['value']
        timestamp = data['timestamp']
        dt = datetime.fromtimestamp(int(timestamp), tz=timezone(timedelta(hours=8)))
        if dt_now - dt > timedelta(hours=48):
            break
        x.insert(0, dt)
        y.insert(0, value)
    # write data points
    plt.plot(x, y)
    # write alert line if exists
    if 'triggers' in DeviceStore[deviceId]:
        for alertData in DeviceStore[deviceId]['triggers']:
            y.append(alertData['triggerValue'])
            plt.axhline(y=alertData['triggerValue'], color='r', linestyle='-')
    # set graphic view area limit
    yMid = ( max(y) + min(y) ) / 2
    yHalfLength = ( max(y) - min(y) ) / 2
    yMax = yMid + yHalfLength * 1.1
    yMin = yMid - yHalfLength * 1.1
    plt.ylim(yMin, yMax)
    # fill color between alert line and limit if need
    if 'triggers' in DeviceStore[deviceId]:
        for alertData in DeviceStore[deviceId]['triggers']:
            if alertData['triggerRule'] in ['>', '>=']:
                plt.axhspan(ymin=alertData['triggerValue'], ymax=yMax, color='r', alpha=0.2)
            elif alertData['triggerRule'] in ['<', '<=']:
                plt.axhspan(ymin=yMin, ymax=alertData['triggerValue'], color='r', alpha=0.2)
    # auto format data time for x axis
    plt.gcf().autofmt_xdate()
    # set label and title text
    plt.xlabel('Time')
    plt.ylabel(DeviceStore[deviceId]['unit'])
    plt.title(deviceId)
    # invert the y axis, 
    plt.gca().invert_yaxis()
    # save(output) graphic
    plt.savefig(savePath)
    plt.clf()
    plt.cla()
    return savePath
