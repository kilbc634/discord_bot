# -*- coding: UTF-8 -*-
import discord
from lib import discord_bot_lib
import requests
import traceback
import os
import time
import subprocess

Affect_channels = ['bot乱交', '車']

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        # specify a channel
        if message.channel.name not in Affect_channels:
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
        if message.content == 'systemcall:logout':
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

if __name__=='__main__':
    myDir = os.getcwd()
    p = subprocess.Popen('python ' + myDir + '\connect_server.py')
    time.sleep(5)

    client = MyClient()
    client.run('NjA2NjY*****************************************90Y9MW8')
