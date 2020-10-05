# -*- coding: UTF-8 -*-
import discord
from lib import discord_bot_lib
import requests
import traceback
import os
import time
import subprocess
import threading
from flask import Flask, jsonify, request, send_from_directory
import json
import asyncio
import connect_server
import linebotapp
from setting import *

client = None
endPoint = Flask('extraService')

Affect_channels = ['bot乱交', '車']
clannelId_onCar = 557487268580032512
clannelId_onTest = 643265881996132362
userId_owner = 407554740906360833

class MyClient(discord.Client):
    async def send_DM(self, userId, text, att=None):
        channel = client.get_user(userId)
        await channel.send(text)

    async def send_message_to_channel(self, channelId, text, att=None):
        channel = client.get_channel(channelId)
        await channel.send(text)

    async def forDM(self, message):
        try:
            print("--------------------- header ---------------------")
            print(message)
            print("--------------------- content ---------------------")
            print(message.content)
            print("--------------------- attachments -----------------")
            print(message.attachments)
        except:
            print("!!! PRINT ERROR !!!")

        if message.content == 'systemcall:logout' or message.content == 'SC:logout':
            exit()

        if message.author.id != userId_owner:
            channel = client.get_user(userId_owner)
            sender = message.author.name
            msg = message.content
            await channel.send('from {sender}:\n{msg}'.format(**locals()))

        if message.content.find('?HOST') == 0:
            await message.channel.send(API_HOST)

        if message.content.find('?DEVICE') == 0:
            device_id_name = list()
            for deviceId in DeviceStore:
                deviceName = DeviceStore[deviceId]['deviceName']
                device_id_name.append('ID: {0}, NAME: {1}'.format(deviceId, deviceName))
            if len(device_id_name) == 0:
                await message.channel.send('No devices is active')
            else:
                await message.channel.send('\n'.join(device_id_name))

        if message.content.find('!ALERT') == 0:
            try:
                mathIcon = ['>', '>=', '=', '<=', '<']
                arg_list = message.content.split(' ')[1:]
                deviceId = arg_list[0]
                triggerRule = arg_list[1]
                if triggerRule not in mathIcon:
                    raise SyntaxError("[FAIL] I hope these math icons " + str(mathIcon))
                triggerValue = float(arg_list[2])
            except:
                await message.channel.send("請使用此格式\n!ALERT [Device ID] {0} [Vlaue]\n(刪除警報則使用 !R_ALERT 指令)".format(str(mathIcon).replace("'", "").replace(", ", "/")))
                return
            if deviceId not in DeviceStore:
                await message.channel.send("該裝置不存在")
                return
            DeviceStore[deviceId]['triggerEnable'] = True
            DeviceStore[deviceId]['triggerRule'] = triggerRule
            DeviceStore[deviceId]['triggerValue'] = triggerValue
            await message.channel.send("裝置 {0}({1}) 警報設定完成".format(deviceId, DeviceStore[deviceId]['deviceName']))

        if message.content.find('!R_ALERT') == 0:
            try:
                arg_list = message.content.split(' ')[1:]
                deviceId = arg_list[0]
            except:
                await message.channel.send("請使用此格式\n!R_ALERT [Device ID]")
                return
            if deviceId not in DeviceStore:
                await message.channel.send("該裝置不存在")
                return
            try:
                del DeviceStore[deviceId]['triggerEnable']
                del DeviceStore[deviceId]['triggerRule']
                del DeviceStore[deviceId]['triggerValue']
            except KeyError:
                await message.channel.send("裝置 {0}({1}) 警報尚未設定".format(deviceId, DeviceStore[deviceId]['deviceName']))
                return
            await message.channel.send("裝置 {0}({1}) 警報已被刪除".format(deviceId, DeviceStore[deviceId]['deviceName']))

        if message.content.find('?ALERT') == 0:
            try:
                arg_list = message.content.split(' ')[1:]
                deviceId = arg_list[0]
            except:
                await message.channel.send("請使用此格式\n?ALERT [Device ID]")
                return
            if deviceId not in DeviceStore:
                await message.channel.send("該裝置不存在")
                return
            if 'triggerEnable' not in DeviceStore[deviceId]:
                await message.channel.send("裝置 {0}({1}) 警報尚未設定".format(deviceId, DeviceStore[deviceId]['deviceName']))
            else:
                t_rule = DeviceStore[deviceId]['triggerRule']
                t_value = DeviceStore[deviceId]['triggerValue']
                await message.channel.send(
                    '警報觸發規則: (當前數值) {t_rule} {t_value}'.format(**locals())
                )

        if message.content.find('!SAY') == 0:
            text = message.content.split(' ', 1)[1]
            channel = client.get_channel(clannelId_onTest)
            await channel.send(text)
        
        if message.content.find('?MEMBER_LIST') == 0:
            members = client.get_all_members()
            members_list = list()
            for member in members:
                user_name = member.display_name
                user_id = member.id
                members_list.append('{user_name} ({user_id})'.format(**locals()))
            await message.channel.send('\n'.join(members_list))

        if message.content.find('?CHANNEL_LIST') == 0:
            channels = client.get_all_channels()
            channels_list = list()
            for channel in channels:
                try:
                    channel_name = channel.name
                    channel_id = channel.id
                    channel_guild = channel.guild.name
                except:
                    continue
                channels_list.append('{channel_name} ({channel_id}) IN <<{channel_guild}>>'.format(**locals()))
            await message.channel.send('\n'.join(channels_list))
    
    async def on_ready(self):
        try:
            print('Logged on as', self.user)
        except UnicodeEncodeError:
            print('Logged on as ***UnicodeEncodeError***')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        # specify a channel
        try:
            if message.channel.name not in Affect_channels:
                return
        except AttributeError: # if message object type is <DMChannel>
            await self.forDM(message)
            return
            
        try:
            print("--------------------- header ---------------------")
            print(message)
            print("--------------------- content ---------------------")
            print(message.content)
            print("--------------------- attachments -----------------")
            print(message.attachments)
        except:
            print("!!! PRINT ERROR !!!")
        ### SystemCall zone ###
        if message.content == 'systemcall:logout' or message.content == 'SC:logout':
            exit()
        ### function zone ###
        if message.content.find('!') == 0:
            functionType = message.content.split(' ', 1)[0]
            functionType = functionType.replace('!', '', 1)
            try:
                functionArg = message.content.split(' ', 1)[1]
            except IndexError:
                functionArg = None
            result = discord_bot_lib.exeFunction(functionType, functionArg, message.attachments, msgObj=message)
            if 'processes' in result:
                process = result['processes']
                channelId = message.channel.id
                def wait_robot_complated(process, reportChannelId=None):
                    returncode = process.wait()
                    if reportChannelId:
                        fileUrl = API_HOST + '/report/log.html'
                        reportText = 'Robot complated\nreport log: {fileUrl}'.format(fileUrl=fileUrl)
                        client.loop.create_task(client.send_message_to_channel(reportChannelId, reportText))
                waitingThread = threading.Thread(target=wait_robot_complated, args=(process, channelId))
                waitingThread.start()
        
        ### test zone ###
        if message.content == 'ping':
            await message.channel.send('pong')
        if message.content == '嘿':
            await message.channel.send('白')
        if message.content == 'file_test':
            await message.channel.send('send 圖片', file=discord.File(os.getcwd() + '/res/image/sample_image2.jpg'))
        if message.content == 'tag_test':
            await message.channel.send('<@300498879433146389>') # @Matcha#8964

@endPoint.route("/")
def welcome():
    return "This is End Point Service of Discord bot" , 200

@endPoint.route("/report/<path:path>")
def view_report(path):
    return send_from_directory('report', path)

@endPoint.route("/message_user", methods=["POST"])
def message_user():
    data = request.json
    sender = data['sender']
    user = data['user']
    message = data['message']
    if user == 'me':
        userId = userId_owner
    else:
        userId = int(user)
    client.loop.create_task(client.send_DM(userId, 'from {sender}:\n{message}'.format(**locals())))
    return 'OK', 200

DeviceStore = dict()
AlertThreads = list()
def alert_trigger(deviceId):
    name = DeviceStore[deviceId]['deviceName']
    vlaue = DeviceStore[deviceId]['value']
    t_rule = DeviceStore[deviceId]['triggerRule']
    t_value = DeviceStore[deviceId]['triggerValue']
    alert_text = '[Alert] 裝置 <{deviceId}>({name}) 被觸發了!\n原因: {vlaue}(當前數值) {t_rule} {t_value}'.format(**locals())
    ## for discord bot
    client.loop.create_task(
        client.send_DM(userId_owner, alert_text)
    )
    ## for line bot
    requests.post(LINE_HOST + '/alert_group/' + linebotapp.groupId_reporter,
        json={"message": alert_text}
    )

def alert_thread(deviceId):
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
                else:
                    DeviceStore[deviceId]['triggerEnable'] = True
            elif triggerRule == '>=':
                if value >= triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
                else:
                    DeviceStore[deviceId]['triggerEnable'] = True
            elif triggerRule == '=':
                if value == triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
                else:
                    DeviceStore[deviceId]['triggerEnable'] = True
            elif triggerRule == '<=':
                if value <= triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
                else:
                    DeviceStore[deviceId]['triggerEnable'] = True
            elif triggerRule == '<':
                if value < triggerValue:
                    if triggerEnable:
                        alert_trigger(deviceId)
                        delayTime = 60
                else:
                    DeviceStore[deviceId]['triggerEnable'] = True
        time.sleep(delayTime)

@endPoint.route("/device/<deviceId>", methods=["POST"])
def device_post(deviceId):
    data = request.json
    if deviceId not in DeviceStore:
        DeviceStore[deviceId] = data['setData']
        alertThread = threading.Thread(target=alert_thread, args=(deviceId,))
        AlertThreads.append(alertThread)
        alertThread.start()
    else:
        for key in data['setData']:
            DeviceStore[deviceId][key] = data['setData'][key]
    deviceData = DeviceStore[deviceId]
    return jsonify({'currentData': deviceData}), 200

@endPoint.route("/device/<deviceId>", methods=["GET"])
def device_get(deviceId):
    if deviceId not in DeviceStore:
        return jsonify({'errorData': 'Not found device [{0}]'.format(deviceId)}) , 202
    deviceData = DeviceStore[deviceId]
    return jsonify({'currentData': deviceData}), 200

@endPoint.route("/device/<deviceId>", methods=["DELETE"])
def device_delete(deviceId):
    if deviceId not in DeviceStore:
        return jsonify({'errorData': 'Not found device [{0}]'.format(deviceId)}) , 202
    del DeviceStore[deviceId]
    return '', 204

@endPoint.route("/device_store", methods=["GET"])
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


async def start():
    await client.start(TOKEN)

def run_it_forever(loop):
    loop.run_forever()

if __name__=='__main__':
    thread1 = threading.Thread(target=connect_server.run)
    thread1.start()
    thread2 = threading.Thread(target=linebotapp.run)
    thread2.start()

    client = MyClient()
    loop = asyncio.get_event_loop()
    loop.create_task(start())
    thread2 = threading.Thread(target=run_it_forever, args=(loop,))
    thread2.start()
    
    endPoint.run(host='0.0.0.0', debug=True, port=21090, use_reloader=False)
