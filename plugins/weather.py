import pywapi
from datetime import datetime
from slackbot.bot import *
import json


result=pywapi.get_weather_from_weather_com('JAXX0085')
result_format=json.dumps(result,indent=4,separators=(',',': '))
print(result_format)

@respond_to('今日の天気は？')
def weather_func(message):
    d1 = []
    d2 = []
    wt = []
    cp = []
    tl = []
    th = []
    for i in range(0, 5):
        d1 = d1 + [result["forecasts"][i]["date"]]
        d2 = d2 + [result["forecasts"][i]["day_of_week"]]
        wt = wt + [result["forecasts"][i]["day"]["text"]]
        cp = cp + [result["forecasts"][i]["day"]["chance_precip"]]
        tl = tl + [result["forecasts"][i]["low"]]
        th = th + [result["forecasts"][i]["high"]]
    sr = result["forecasts"][0]["sunrise"]
    ss = result["forecasts"][0]["sunset"]
    loc = result['location']['name']
    lon = result['location']['lon']
    lat = result['location']['lat']
    udn = result['current_conditions']['last_updated']
    wtn = result['current_conditions']['text']
    ten = result['current_conditions']['temperature'] + "°C"
    message.reply('==================================================')
    message.reply(loc + ' (lon=' + lon + ' lat=' + lat + ')')
    message.reply('Last updated: ' + udn)
    message.reply('Weather: ' + wtn + ' (' + ten + ')')
    message.reply('sunrise: ' + sr + ' sunset: ' + ss)
    message.reply('--------------------------------------------------')
    for i in range(0, 5):
        message.reply('{0:6} {1:10} {2:3}% {3:2}/{4:2}°C {5:}'.format(d1[i], d2[i], cp[i], th[i], tl[i], wt[i]))

