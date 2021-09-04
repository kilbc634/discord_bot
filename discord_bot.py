# -*- coding: UTF-8 -*-
import discord
from lib import discord_bot_lib
import os
import threading
import asyncio
import linebotapp
from setting import *
import endpoint_server
import youtube_dl

client = None
AffectChannels = ['bot共闘', '車']

'''
TextChannel sample:
--------------------- header ---------------------
<Message id=766906008865210368 channel=<TextChannel id=643265881996132362 name='bot共闘' position=2 nsfw=False news=False category_id=557482649279528991> type=<MessageType.default: 0> author=<Member id=407554740906360833 name='tuyn76801' discriminator='2063' bot=False nick='芙蕾絲' guild=<Guild id=557482649279528990 name='二萌 會' shard_id=None chunked=True member_count=22>> flags=<MessageFlags value=0>>
--------------------- content ---------------------
test massage
--------------------- attachments -----------------
[<Attachment id=766906008530059274 filename='ed65b6be4df003d7.png' url='https://cdn.discordapp.com/attachments/643265881996132362/766906008530059274/ed65b6be4df003d7.png'>]
'''

'''
DMChannel sample:
--------------------- header ---------------------
<Message id=766906633942990899 channel=<DMChannel id=744227977432137838 recipient=<User id=407554740906360833 name='tuyn76801' discriminator='2063' bot=False>> type=<MessageType.default: 0> author=<User id=407554740906360833 name='tuyn76801' discriminator='2063' bot=False> flags=<MessageFlags value=0>>
--------------------- content ---------------------
test massage
--------------------- attachments -----------------
[<Attachment id=766906631014449152 filename='933eba98cf995628.png' url='https://cdn.discordapp.com/attachments/744227977432137838/766906631014449152/933eba98cf995628.png'>]
'''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MyClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.clannelId_onCar = 557487268580032512
        self.clannelId_onTest = 643265881996132362
        self.UserId_Owner = 407554740906360833

    async def on_ready(self):
        try:
            print('Logged on as', self.user)
        except UnicodeEncodeError:
            print('Logged on as ***UnicodeEncodeError***')
        await client.change_presence(activity=discord.Game(name='?HELP'))

    async def send_message_with_userId(self, userId, text, att=None):
        channel = client.get_user(userId)
        await channel.send(text)

    async def send_message_with_channelId(self, channelId, text, att=None):
        channel = client.get_channel(channelId)
        await channel.send(text)

    async def on_message(self, message):
        try:
            print("--------------------- header ---------------------")
            print(message)
            print("--------------------- content ---------------------")
            print(message.content)
            print("--------------------- attachments -----------------")
            print(message.attachments)
        except:
            print("[ERROR] Print the debug message failed")
        if message.author == self.user:
            return
        if message.author.bot == True:
            return
        # heart beat test
        if message.content == 'ping':
            await message.channel.send('pong')
            return
        elif message.content.find('外賣') >= 0 or message.content.find('咖哩拌飯') >= 0:
            if message.guild.voice_client == None:
                await message.author.voice.channel.connect()
            async with message.channel.typing():
                player = await YTDLSource.from_url('https://www.youtube.com/watch?v=mUjM7BRopt0', loop=self.loop)
                message.guild.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            if message.content.find('外賣') >= 0:
                await message.channel.send('有人提到外賣嗎?')
            elif message.content.find('咖哩拌飯') >= 0:
                await message.channel.send('有人提到咖哩拌飯嗎?')
            return
        
        response = dict()
        if str(message.channel.type) == 'private':  # as Direct Message(DM)
            if message.author.id != self.UserId_Owner:
                channel = self.get_user(self.UserId_Owner)
                sender = message.author.name
                text = message.content
                await channel.send('from {sender}:\n{text}'.format(**locals()))

            if discord_bot_lib.check_function(message.content):
                if message.author.id == self.UserId_Owner:
                    admin = True
                else:
                    admin = False
                response = discord_bot_lib.command_line(self,
                    message.content,
                    message.attachments,
                    admin=admin,
                    messageObj=message
                )
        elif str(message.channel.type) == 'text':
            if message.channel.name not in AffectChannels:
                return
            if message.author.id == self.UserId_Owner:
                if discord_bot_lib.check_function(message.content):
                    response = discord_bot_lib.command_line(self,
                        message.content,
                        message.attachments,
                        admin=True,
                        messageObj=message
                    )
            else:
                if discord_bot_lib.check_function(message.content):
                    response = discord_bot_lib.command_line(self,
                        message.content,
                        message.attachments,
                        admin=False,
                        messageObj=message
                    )
        
        if response:
            sendText = None
            sendFile = None
            if 'text' in response:
                sendText = response['text']
            if 'file' in response:
                sendFile = discord.File(response['file'])
            await message.channel.send(sendText, file=sendFile)


async def start():
    await client.start(TOKEN)

if __name__=='__main__':
    client = MyClient()
    thread1 = threading.Thread(target=endpoint_server.run, args=(client,), daemon=True)
    thread1.start()
    thread2 = threading.Thread(target=linebotapp.run, daemon=True)
    thread2.start()

    loop = asyncio.get_event_loop()
    loop.create_task(start())
    loop.run_forever()
