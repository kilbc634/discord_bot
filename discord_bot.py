# -*- coding: UTF-8 -*-
import discord
from lib import discord_bot_lib
import requests
import traceback
import os
import time
import subprocess
import threading
from flask import Flask, jsonify, request
import json
import asyncio
import connect_server
from setting import *

client = None
endPoint = Flask('extraService')

Affect_channels = ['bot乱交', '車']
clannelId_onCar = 557487268580032512
clannelId_onTest = 643265881996132362
userId_owner = 407554740906360833

class MyClient(discord.Client):
    async def send_DM(self, userId, text):
        channel = client.get_user(userId)
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

        if message.content.find('!SAY') == 0:
            text = message.content.split(' ', 1)[1]
            channel = client.get_channel(clannelId_onTest)
            await channel.send(text)
        
        if message.content.find('!MEMBER_LIST') == 0:
            members = client.get_all_members()
            members_list = list()
            for member in members:
                user_name = member.display_name
                user_id = member.id
                members_list.append('{user_name} ({user_id})'.format(**locals()))
            await message.channel.send('\n'.join(members_list))
    
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
            result = discord_bot_lib.exeFunction(functionType, functionArg, message.attachments[0].url)
        
        ### test zone ###
        if message.content == 'ping':
            await message.channel.send('pong')
        if message.content == '嘿':
            await message.channel.send('白')
        if message.content == 'オラオラ':
            await message.channel.send('ムダムダ')
        if message.content == 'file_test':
            await message.channel.send('send 圖片', file=discord.File(os.getcwd() + '/res/image/sample_image2.jpg'))
        if message.content == 'tag_test':
            await message.channel.send('<@300498879433146389>') # @Matcha#8964

@endPoint.route("/")
def welcome():
    return "This is End Point Service of Discord bot" , 200

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


async def start():
    await client.start(TOKEN)

def run_it_forever(loop):
    loop.run_forever()

if __name__=='__main__':
    thread1 = threading.Thread(target=connect_server.run)
    thread1.start()

    client = MyClient()
    loop = asyncio.get_event_loop()
    loop.create_task(start())
    thread2 = threading.Thread(target=run_it_forever, args=(loop,))
    thread2.start()
    
    endPoint.run(host='0.0.0.0', debug=True, port=21090, use_reloader=False)
