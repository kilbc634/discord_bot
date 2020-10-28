import redis
from ast import literal_eval
from setting import *

RedisClient = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_AUTH, decode_responses=True)

def check_device(deviceId):
    resp = RedisClient.exists('device/' + deviceId)
    return resp

def add_device_value(deviceId, value, timestamp):
    data = dict()
    data['value'] = value
    data['timestamp'] = timestamp
    resp = RedisClient.lpush('device/' + deviceId, data)
    if resp > 100:
        RedisClient.brpop('device/' + deviceId)

def get_device_value(deviceId, start=0, end=-1):
    resp = RedisClient.lrange('device/' + deviceId, start, end)
    valueList = list()
    for text in resp:
        valueList.append(literal_eval(text))
    return valueList
