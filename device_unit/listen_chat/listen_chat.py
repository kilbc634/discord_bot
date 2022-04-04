import sys
import requests
from time import sleep
import traceback

REPORT_API = 'http://tsukumonet.ddns.net:21090/message_user'

if __name__ == '__main__':
    cookie = sys.argv[1]
    token = sys.argv[2]
    currentStates = dict()
    '''
    currentStates = {
        'channelId1': {
            'unread': 0,
            'unread_comment': 0,
            'unread_mention': 0,
            'unread_mention_comment': 0,
            'unread_thread': {}
        },
        'channelId2': {
            .....
        },
        .....
    }
    '''
    print('[INFO] Start listen...')

    try:
        while True:
            resp = requests.post('https://chat.gpms365.net/webapi/entry.cgi',
            headers={
                'cookie': cookie,
                'x-syno-token': token
            },
            data={
                'is_joined': 'true',
                'api': 'SYNO.Chat.Channel',
                'method': 'list',
                'version': '2'
            }).json()

            for channel in resp['data']['channels']:
                channelName = channel['name']
                channelId = str(channel['channel_id'])
                if str(channelId) not in currentStates:
                    currentStates[str(channelId)] = {
                        'unread': 0,
                        'unread_comment': 0,
                        'unread_mention': 0,
                        'unread_mention_comment': 0,
                        'unread_thread': {}
                    }
                if channel['unread'] != currentStates[channelId]['unread'] \
                or channel['unread_comment'] != currentStates[channelId]['unread_comment'] \
                or channel['unread_mention'] != currentStates[channelId]['unread_mention'] \
                or channel['unread_mention_comment'] != currentStates[channelId]['unread_mention_comment'] \
                or channel['unread_thread'] != currentStates[channelId]['unread_thread']:
                    print('[INFO] States change, will update and report current state')
                    print(str(channel))
                    currentStates[channelId]['unread'] = channel['unread']
                    currentStates[channelId]['unread_comment'] = channel['unread_comment']
                    currentStates[channelId]['unread_mention'] = channel['unread_mention']
                    currentStates[channelId]['unread_mention_comment'] = channel['unread_mention_comment']
                    currentStates[channelId]['unread_thread'] = channel['unread_thread']
                    requests.post(REPORT_API, json={
                        'sender': sys.argv[0],
                        'user': '407554740906360833',
                        'message': '[SYNO] 你有未讀訊息於 {0}\n{1}'.format(channelName, str(currentStates[channelId]))
                    })

            sleep(60)
    except:
        traceback.print_exc()
        if resp:
            print(resp)
        requests.post(REPORT_API, json={
            'sender': sys.argv[0],
            'user': '407554740906360833',
            'message': '[SYNO] 監聽意外性終止'
        })
