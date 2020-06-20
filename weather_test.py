import requests

data = requests.get('https://api.caiyunapp.com/v2/777/116.404412,39.915156/realtime.json').json()

print(data)

status = data['status']
if status == 'ok':
    result = data['result']
    if result['status'] == 'ok':
        temperature = result['temperature']
        humidity = result['humidity']
        cloudrate = result['cloudrate']
        visibility = result['visibility']
        wind = result['wind']
        wind_speed = wind['speed']
        wind_direction = wind['direction']
        pres = result['pres']
        apparent_temperature = result['apparent_temperature']
    else:
        print('get data failed')
else:
    print('get data failed')

data2 = requests.get('https://free-api.heweather.net/s6/weather/now?location=116.40,39.9&key=key').json()
print(data2)
if len(data2['HeWeather6']) > 0:
    result = data2['HeWeather6'][0]
    if result['status'] == 'ok':
        result = result['now']
        cloudrate = result['cloud']
        cond_code = result['cond_code']
        pres = result['pres']
        temperature = result['tmp']
        visibility = result['vis']
        apparent_temperature = result['fl']
    else:
        print('get data failed')
else:
    print('get data failed')


data3 = requests.get('https://api.caiyunapp.com/v2/key/116.404412,39.915156/daily.json').json()
status = data3['status']
if status == 'ok':
    result = data3['result']
    forcast = result['daily']
    skyicon = forcast['skycon']
    print(skyicon)
    tommorw_cast = skyicon[0]['value']
    print(tommorw_cast)

data = requests.get('https://free-api.heweather.net/s6/weather/forecast?location=116.40,39.9&key=key').json()
if len(data['HeWeather6']) > 0:
    result = data['HeWeather6'][0]
    if result['status'] == 'ok':
        result = result['daily_forecast']
        today_cast = result[0]['cond_txt_d']
        tommorw_cast = result[0]['cond_txt_d']
        print(tommorw_cast)
        print(today_cast)
        today_tmp_min = result[0]['tmp_min']
        tomorrwo_tmp_min = result[1]['tmp_min']
        today_tmp_max = result[0]['tmp_max']
        tomorrow_tmp_max = result[1]['tmp_max']