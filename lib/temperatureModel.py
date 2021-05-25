import requests
import json
from configparser import ConfigParser
import datetime

class requestLib():
    def __init__(self, debug=False):
        self.DEBUG = debug
        self.WEEKS_STR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.URL = 'https://epidemicapi.ncut.edu.tw/api/'
        self.SESSION = requests.Session()
        self.SESSION.headers.clear()
        self.SESSION.headers.update({
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://epidemic.ncut.edu.tw',
            'referer': 'https://epidemic.ncut.edu.tw/bodyTemp'
        })

    def __request(self, method, node='', **kwargs):
        resp = self.SESSION.request(method, self.URL + node, **kwargs)
        if DEBUG:
            try:
                print(resp)
                print(resp.text)
            except (UnicodeDecodeError, UnicodeDecodeError, UnicodeError):
                print('[Error] Unknow unicode error from response')
        return resp

    #------------------------------------------------------------------------------------
    # Function Zone
    #------------------------------------------------------------------------------------

    def login(self, account, password , remember=False):
        '''
        Note: 拿取新的token，也不會因此讓舊token失效
        '''
        data = {
            'userId': account,
            'password': password,
            'remember': remember
        }
        self.SESSION.headers.update({'referer': 'https://epidemic.ncut.edu.tw/login'})
        resp = self.__request('post', 'login', json=data)
        respJson = json.loads(resp.text)
        return respJson

    def getToken(self, account, password):
        resp = self.login(account, password)
        token = resp['token']
        return token

    def checkPosted(self, token, userId, date):
        resp = self.get_tempData(token, userId, date)
        if len(resp.text) == 0:
            if DEBUG:
                print('[Info] {userId}-{date} date not exist'.format(userId=userId, date=date))
            return False
        else:
            if DEBUG:
                print('[Info] {userId}-{date} date exist'.format(userId=userId, date=date))
            return True

    def loadConfig(self, filePath):
        config = ConfigParser()
        config.read(filePath, encoding='utf-8-sig')
        return config

    #-------------------------------------------------------------------------------------

    def get_departments(self, token):
        self.SESSION.headers.update({'authorization': 'Bearer %s' % token})
        resp = self.__request('get', 'departments')
        return resp

    def get_tempData(self, token, userId, date):
        self.SESSION.headers.update({'authorization': 'Bearer %s' % token})
        resp = self.__request('get', 'temperatureSurveys/{userId}-{date}'.format(userId=userId, date=date))
        return resp

    def post_tempData(self, token, userId, departmentId, departmentName, className, date,
        morningTemp=34, morningActivity='',
        noonTemp=34, noonActivity='',
        nightTemp=34, nightActivity='',
        method='post'):
        self.SESSION.headers.update({'authorization': 'Bearer %s' % token})
        data = {
            "id": userId + "-undefined",
            "saveDate": date,
            "morningTemp": morningTemp,
            "noonTemp": noonTemp,
            "nightTemp": nightTemp,
            "isValid": False,
            "morningManner": 0,
            "noonManner": 0,
            "nightManner": 0,
            "isMorningFever": None,
            "isNoonFever": False,
            "isNightFever": None,
            "morningActivity": morningActivity,
            "noonActivity": noonActivity,
            "nightActivity": nightActivity,
            "measureTime": "20:00",
            "userId": userId,
            "departmentId": departmentId,
            "className": className,
            "departmentName": departmentName,
            "type": "1"
        }
        resp = self.__request(method, 'temperatureSurveys', json=data)
        if resp.status_code == 200:
            respJson = json.loads(resp.text)
            respJson["messages"] = [
                "[OK] {userId} {date} 已填入正常體溫".format(userId=userId, date=date)
            ]
            print(respJson["messages"][0])
            return respJson
        elif resp.status_code == 500:
            respJson = {
                "success": False,
                "messages": [
                    "[Warning] {userId} {date} 當天資料已存在".format(userId=userId, date=date)
                ]
            }
            print(respJson["messages"][0])
            return respJson
        else:
            resp.raise_for_status()
