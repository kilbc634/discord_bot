import redis
from ast import literal_eval
import copy
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
    if resp > 14400:
        RedisClient.brpop('device/' + deviceId)

def get_device_value(deviceId, start=0, end=-1, dataLimit=0):
    resp = RedisClient.lrange('device/' + deviceId, start, end)
    valueList = list()
    for text in resp:
        valueList.append(literal_eval(text))
    if dataLimit > 0 and len(valueList) > dataLimit:
        sampleRange = len(valueList) // dataLimit
        valueList = transform_to_average_data(valueList, sampleRange)
    return valueList

def transform_to_average_data(dataList, sampleRange):
    averageData = list()
    data = copy.deepcopy(dataList)
    while len(data) >= sampleRange:
        item = data[0]
        for key in data[0]:
            if not (isinstance(data[0][key], int) or isinstance(data[0][key], float)):
                continue
            sample = list()
            for d in data[0:sampleRange]:
                sample.append(d[key])
            sample_avg = sum(sample) / len(sample)
            item[key] = sample_avg
        averageData.append(item)
        del data[0:sampleRange]  
    return averageData
