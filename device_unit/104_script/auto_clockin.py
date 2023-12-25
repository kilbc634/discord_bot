import sys
import requests
import datetime


def get_start_of_day_unix_timestamp():
    # 获取当前时间（系统默认时区为 UTC）
    current_time_utc = datetime.datetime.utcnow()

    # 将系统时间转换为 UTC+8 时区的时间
    utc_offset = datetime.timedelta(hours=8)  # UTC+8 时区的时间偏移量
    current_time_utc_plus_eight = current_time_utc + utc_offset

    # 获取当天的开始时间（零点时间）
    start_of_day = datetime.datetime(year=current_time_utc_plus_eight.year,
                                    month=current_time_utc_plus_eight.month,
                                    day=current_time_utc_plus_eight.day,
                                    hour=0, minute=0, second=0)

    # 转换为 Unix 时间戳
    tz = datetime.timezone(utc_offset)
    start_of_day = start_of_day.replace(tzinfo=tz)
    start_of_day_unix_timestamp = int(start_of_day.timestamp())

    return start_of_day_unix_timestamp

def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def get_current_datetime():
    # 获取当前时间（系统默认时区为 UTC）
    current_time_utc = datetime.datetime.utcnow()

    # 将系统时间转换为 UTC+8 时区的时间
    utc_offset = datetime.timedelta(hours=8)  # UTC+8 时区的时间偏移量
    current_time_utc_plus_eight = current_time_utc + utc_offset

    return current_time_utc_plus_eight

def check_hours_difference(startDate, endDate, hours=9):
    # 计算时间差
    timeDifference = endDate - startDate

    # 定义一个N小时的时间间隔
    timeThreshold = datetime.timedelta(hours=hours)

    # 检查时间差是否超过N小时
    if timeDifference > timeThreshold:
        return True
    else:
        return False


if __name__ == '__main__':
    cookie = sys.argv[1]
    # TODO: 實作過期自動重新登入
    # account = sys.argv[2]
    # password = sys.argv[3]

    # setup API token for https://pro.104.com.tw/psc2/api
    print("Setup session....")
    session = requests.Session()
    session.headers.clear()
    session.headers.update({
        'authority': 'pro.104.com.tw',
        'accept': 'application/json',
        'content-type': 'application/json;charset=UTF-8',
        'referer': 'https://pro.104.com.tw/psc2',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'cookie': cookie
    })

    # response sample:
    # {
    #     "code": 200,
    #     "message": "OK",
    #     "data": [
    #         {
    #             "date": 1703001600000,
    #             "clockIn": {
    #                 "clockInCode": 4,
    #                 "start": 1703036344000,
    #                 "end": 1703070042000,
    #                 "times": [
    #                     {
    #                         "id": 889827015387616,
    #                         "time": 1703036344000,
    #                         "temperature": 0
    #                     },
    #                     {
    #                         "id": 738234117821936,
    #                         "time": 1703070042000,
    #                         "temperature": 0
    #                     }
    #                 ]
    #             },
    #             "events": [],
    #             "leave": []
    #         }
    #     ]
    # }

    # get today info
    print("Get Today Info....")
    todayTimestamp = get_start_of_day_unix_timestamp() * 1000
    respDayInfo = session.get('https://pro.104.com.tw/psc2/api/home/newCalendar/day/info/{timestamp}'.format(
        timestamp=str(todayTimestamp)
    )).json()
    print('[DEBUG] show respDayInfo')
    print(respDayInfo)

    # check data is today
    todayData = None
    if respDayInfo['data'][0]['date'] == todayTimestamp:
        todayData = respDayInfo['data'][0]
    else:
        raise RuntimeError("Today Data Error")
    
    startDate = None
    if todayData['clockIn']['start']:
        startDate = timestamp_to_datetime(todayData['clockIn']['start'] / 1000)
    endDate = None
    if todayData['clockIn']['end']:
        endDate = timestamp_to_datetime(todayData['clockIn']['end'] / 1000)


    # check clockIn if NEED
    print("Check ClockIn If NEED....")
    doClockIn = False
    currentDate = get_current_datetime()

    if len(todayData['events']) > 0 or len(todayData['leave']) > 0:  # when dayoff
        pass
    elif datetime.time(9, 30) <= currentDate.time() <= datetime.time(10, 0):  # 如果在 9:30 ~ 10:00 之間
        if startDate is None:
            doClockIn = True
    elif currentDate.time() >= datetime.time(18, 30):  # 如果在 18:30 之後
        if startDate is None and endDate is None:
            doClockIn = True
        elif startDate and endDate is None:
            if check_hours_difference(startDate, currentDate, hours=9):
                doClockIn = True
        elif startDate and endDate:
            if check_hours_difference(startDate, endDate, hours=9):
                pass
            elif check_hours_difference(startDate, currentDate, hours=9):
                doClockIn = True
                

    # response sample:
    # {
    #     "code": 200,
    #     "message": "OK",
    #     "data": {
    #         "isTemperatureOpen": false,
    #         "isEnable": false,
    #         "isRequiredReason": false,
    #         "overAttCardDataId": 238874091002883
    #     }
    # }
                
    # do clockIn
    if doClockIn:
        print("Do ClockIn....")
        respClockIn = session.post('https://pro.104.com.tw/psc2/api/f0400/newClockin').json()
        print('[DEBUG] show respClockIn')
        print(respClockIn)
        
        if respClockIn['message'] == 'OK':
            print("Do ClockIn Done")
        else:
            raise  RuntimeError("Do ClockIn Fail")
        
    else:
        print("Skip ClockIn")
    