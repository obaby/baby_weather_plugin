# Baby weather plugin
#
# Author: obaby
# http://www.h4ck.org.cn
# http://www.findu.co
# http://www.obaby.org.cn
"""
<plugin key="BabyWeatherPlugin" name="Baby Weather Plugin" author="obaby" version="2.1.0" wikilink="http://www.h4ck.org.cn" externallink="https://github.com/obaby/baby_weather_plugin">
    <description>
        <h2>Baby Weather Plugin</h2><br/>
        支持从国内的天气服务器获取天气信息
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>版本号：2.1.0</li>
            <li>支持和风天气</li>
            <li>支持彩云天气</li>
            <li>支持今天明天的天气预报信息</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Temperature - 当前温度</li>
            <li>Feeling Temperature - 当前体感温度</li>
            <li>Humidity - 湿度</li>
            <li>Pressure - 气压</li>
            <li>PM25 - 当前PM25浓度</li>
            <li>PM10 - 当前PM10浓度</li>
            <li>SO2 - 当前PSO2浓度</li>
            <li>Weather forecast(Today) - 今天天气</li>
            <li>Weather forecast(Tomorrow) - 明天天气</li>
        </ul>
        <h3>Configuration</h3>
        <p>API KEY请自行注册相关的开发者账号，然后获取key。</p>
        <p>技术支持：http://www.h4ck.org.cn</p>
        <p>彩云天气：https://open.caiyunapp.com/</p>
        <p>和风天气：https://dev.heweather.com/</p>
    </description>
    <params>

    <param field="Mode1" label="服务器" width="100px">
        <options>
            <option label="彩云天气" value="Caiyun"/>
            <option label="和风天气" value="heweather"/>
        </options>
    </param>
    <param field="Mode2" label="API KEY" width="600px" required="true" default="**********************"/>
    <param field="Mode3" label="经度" width="600px" required="true" default="116.40"/>
    <param field="Mode4" label="纬度" width="600px" required="true" default="39.915156"/>
    <param field="Address" label="城市（拼音）" width="600px" required="true" default="qingdao"/>
    <param field="Mode5" label="更新频率(分钟)" width="60px" required="true" default="60"/>
    <param field="Mode6" label="Debug" width="75px">
        <options>
            <option label="True" value="Debug"/>
            <option label="False" value="Normal"  default="true" />
        </options>
    </param>
    </params>
</plugin>
"""
import requests
import datetime
import _thread

try:
    import Domoticz
except:
    import fakeDomoticz as Domoticz


def UpdateDevice(Unit, nValue, sValue, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or AlwaysUpdate == True:
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Log("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
    return


class BasePlugin:
    enabled = False
    httpConn = None
    server_name = ''
    server_path = ''
    server_type = 1
    forcast_path = ''

    def is_daytime_now(self):
        return 6 <= datetime.datetime.now().hour <= 16

    # https://pypi.org/project/buienradar/
    def getWindDirection(self, windBearing):

        if windBearing == None:
            return ""
        windBearing = int(windBearing)
        if windBearing < 0 or windBearing > 360:
            return ""

        if windBearing > 348 or windBearing <= 11:
            return "N"
        if windBearing > 11 and windBearing <= 33:
            return "NNE"
        if windBearing > 33 and windBearing <= 57:
            return "NE"
        if windBearing > 57 and windBearing <= 78:
            return "ENE"
        if windBearing > 78 and windBearing <= 102:
            return "E"
        if windBearing > 102 and windBearing <= 123:
            return "ESE"
        if windBearing > 123 and windBearing <= 157:
            return "SE"
        if windBearing > 157 and windBearing <= 168:
            return "SSE"
        if windBearing > 168 and windBearing <= 192:
            return "S"
        if windBearing > 192 and windBearing <= 213:
            return "SSW"
        if windBearing > 213 and windBearing <= 237:
            return "SW"
        if windBearing > 237 and windBearing <= 258:
            return "WSW"
        if windBearing > 258 and windBearing <= 282:
            return "W"
        if windBearing > 282 and windBearing <= 303:
            return "WNW"
        if windBearing > 303 and windBearing <= 327:
            return "NW"
        if windBearing > 327 and windBearing <= 348:
            return "NNW"

        # just in case
        return ""

    def calc_hum_status(self, hum):
        # Humidity status: 0 - Normal, 1 - Comfort, 2 - Dry, 3 - Wet
        status = '0'
        hum = int(hum)
        if 0 < hum < 30:
            status = '2'
        elif 31 <= hum <= 70:
            status = '1'
        elif 70 < hum:
            status = '3'
        return status

    def get_heweather_forecast_status(self, status):
        # Forecast: 0 - None, 1 - Sunny, 2 - PartlyCloudy, 3 - Cloudy, 4 - Rain
        forecast = '0'
        status = int(status)
        if status in [100, 200, 201, ]:
            forecast = '1'
        if status in [102, 103]:
            forecast = '2'
        if status in [101, 104]:
            forecast = '3'
        if 300 <= status <= 400:
            forecast = '4'
        return forecast

    def get_caiyun_forecast_status(self, status):
        forecast = '0'
        if status in ['CLEAR_DAY', 'CLEAR_NIGHT']:
            forecast = '1'
        if status in ['PARTLY_CLOUDY_DAY', 'PARTLY_CLOUDY_NIGHT']:
            forecast = '2'
        if status in ['CLOUDY']:
            forecast = '3'
        if status in ['LIGHT_RAIN', 'MODERATE_RAIN', 'HEAVY_RAIN', 'STORM_RAIN', 'LIGHT_SNOW', 'MODERATE_SNOW',
                      'HEAVY_SNOW', 'STORM_SNOW']:
            forecast = '4'
        return forecast

    def __init__(self):
        # self.var = 123
        return

    def update_device_value(self, unit_id, nvalue, svalue):
        # Devices[Unit].Update(nValue=nValue, sValue=str(sValue), SignalLevel=50, Image=8)
        # Devices[unit_id].Update(nValue=nvalue, sValue=str(svalue))
        UpdateDevice(unit_id, nvalue, svalue, AlwaysUpdate=True)

    def get_weather_data(self):
        data = requests.get(self.server_name + self.server_path).json()
        # Domoticz.Logdata)
        temperature = None
        humidity = None
        cloudrate = None
        visibility = None
        wind_speed = None
        wind_direction = None
        pres = None
        apparent_temperature = None
        pm25 = pm10 = so2 = no2 = co = None
        if self.server_type == 1:
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
                    pres = int(result['pres']) / 100
                    apparent_temperature = result['apparent_temperature']
                    pm25 = result['pm25']
                    pm10 = result['pm10']
                    so2 = result['so2']
                    no2 = result['no2']
                    co = result['co']
                else:
                    Domoticz.Log('get data failed')
            else:
                Domoticz.Log('get data failed')

        else:
            if len(data['HeWeather6']) > 0:
                result = data['HeWeather6'][0]
                if result['status'] == 'ok':
                    result = result['now']
                    cloudrate = result['cloud']
                    cond_code = result['cond_code']
                    pres = result['pres']
                    temperature = result['tmp']
                    visibility = result['vis']
                    apparent_temperature = result['fl']
                    wind_direction = result['wind_deg']
                    wind_speed = result['wind_spd']
                    humidity = float(result['hum']) /100
                else:
                    Domoticz.Log('get data failed')
            else:
                Domoticz.Log('get data failed')
            # 获取空气质量数据
            # weather_path = '/s6/air/now?location=' + Parameters['Mode3'] + ',' + Parameters['Mode4'] + '&key=' + \
            #                    Parameters['Mode2']
            #
            # wdata = requests.get(self.server_name + self.weather_path).json()

        # https://github.com/Xorfor/Domoticz-API/wiki/Device#properties

        if temperature:
            self.update_device_value(1, int(temperature), str(temperature))
        if humidity:
            self.update_device_value(2, int(humidity * 100), str(humidity))
        # if temperature and humidity:
        #     self.update_device_value(5, 0, str(temperature) + ';' + str(humidity * 100) + ';1')
        # if cloudrate:
        #     self.update_device_value()
        if visibility:
            self.update_device_value(7, int(visibility), str(visibility))
        if wind_speed and wind_direction:
            self.update_device_value(8, 0, str(wind_direction)
                                     + ";" + self.getWindDirection(wind_direction)
                                     + ";" + str(round(float(wind_speed) * 10))
                                     + ";" + str(round(float(wind_speed) * 10))
                                     + ";0;0")
            # UpdateDevice(8, 0, str(wind_speed)
            #              + ";" + str(wind_direction)
            #              + ";" + str(round(wind_speed * 10))
            #              + ";" + str(round(wind_speed * 10))
            #              + ";0;0")
        if pres:
            self.update_device_value(3, int(pres), str(pres))
        if apparent_temperature:
            self.update_device_value(6, int(apparent_temperature), str(apparent_temperature))

        if pm25:
            self.update_device_value(4, int(pm25), str(pm25))
        if pm10:
            self.update_device_value(41, int(pm10), str(pm10))
        if so2:
            self.update_device_value(41, int(so2), str(so2))
        if no2:
            self.update_device_value(43, int(no2), str(no2))
        if co:
            self.update_device_value(44, int(co), str(co))

    def get_heweather_air_data(self):
        data = requests.get(self.server_name + self.heweather_air_path).json()
        print(self.server_name + self.heweather_air_path)
        Domoticz.Log('air:')
        # print(data)
        pm25 = pm10 = so2 = no2 = co = None
        if len(data['HeWeather6']) > 0:
            result = data['HeWeather6'][0]
            if result['status'] == 'ok':
                result = result['air_now_city']
                pm25 = result['pm25']
                pm10 = result['pm10']
                no2 = result['no2']
                so2 = result['so2']
                co = result['co']
        if pm25:
            self.update_device_value(4, int(pm25), str(pm25))
        if pm10:
            self.update_device_value(41, int(pm10), str(pm10))
        if so2:
            self.update_device_value(41, int(so2), str(so2))
        if no2:
            self.update_device_value(43, int(no2), str(no2))
        if co:
            self.update_device_value(44, int(float(co)), str(co))



    def get_forecast_data(self):
        data = requests.get(self.server_name + self.forcast_path).json()
        Domoticz.Log('forcast:')
        # Domoticz.Log(data)
        today_cast = tommorow_cast = None
        today_tmp_min = today_tmp_max = None
        tomorrow_tmp_min = tomorrow_tmp_max = None
        today_hum = tomorrow_hum = None
        today_forecast_statu = forcast_status = '0'
        today_press = tommorw_press = None
        if self.server_type == 1:
            status = data['status']
            if status == 'ok':
                result = data['result']
                forcast = result['daily']
                skyicon = forcast['skycon']
                today_cast = skyicon[0]['value']
                tommorow_cast = skyicon[1]['value']
                # Domoticz.Log(tommorw_cast)
                tmps = forcast['temperature']
                today_tmp_min = tmps[0]['min']
                today_tmp_max = tmps[0]['max']
                tomorrow_tmp_min = tmps[1]['min']
                tomorrow_tmp_max = tmps[1]['max']
                hum = forcast['humidity']
                #  {
                #                     "date":"2020-06-21",
                #                     "max":0.55,
                #                     "min":0.21,
                #                     "avg":0.37
                #                 },
                today_hum = hum[0]['avg']  #
                today_hum = float(today_hum) * 100

                tomorrow_hum = hum[1]['avg']
                tomorrow_hum = float(tomorrow_hum) * 100
                forcast_status = self.get_caiyun_forecast_status(tommorow_cast)
                today_forecast_statu = self.get_caiyun_forecast_status(today_cast)
                press = forcast['pres']
                today_press = press[0]['avg']
                tommorw_press = press[1]['avg']
                today_press = int(today_press) / 100
                tommorw_press = int(tommorw_press) / 100
        else:
            if len(data['HeWeather6']) > 0:
                result = data['HeWeather6'][0]
                if result['status'] == 'ok':
                    result = result['daily_forecast']
                    if self.is_daytime_now():
                        today_cast = result[0]['cond_txt_d']
                    else:
                        today_cast = result[0]['cond_txt_n']
                    tommorow_cast = result[1]['cond_txt_d']
                    today_cast_id = result[0]['cond_code_d']
                    tomorrow_cast_id = result[1]['cond_code_d']
                    # Domoticz.Log(tommorw_cast)
                    # Domoticz.Log(today_cast)
                    today_tmp_min = result[0]['tmp_min']
                    tomorrow_tmp_min = result[1]['tmp_min']
                    today_tmp_max = result[0]['tmp_max']
                    tomorrow_tmp_max = result[1]['tmp_max']
                    today_hum = int(result[0]['hum'])
                    tomorrow_hum = int(result[1]['hum'])
                    forcast_status = self.get_heweather_forecast_status(tomorrow_cast_id)
                    today_forecast_statu = self.get_heweather_forecast_status(today_cast_id)
                    today_press = int(result[0]['pres'])
                    tommorw_press = int(result[1]['pres'])
        if today_cast:
            self.update_device_value(9, 0, str(today_cast) + ' 温度：' + str(today_tmp_min) + ' - ' + str(today_tmp_max))
        if tommorow_cast:
            self.update_device_value(10, 0,
                                     str(tommorow_cast) + ' 温度：' + str(tomorrow_tmp_min) + ' - ' + str(
                                         tomorrow_tmp_max))
        print('todayhum:', today_hum)
        print('tomorrowhum:', tomorrow_hum)
        if today_cast and tommorow_cast:
            # Temperature;Humidity;Humidity Status;Barometer;Forecast
            self.update_device_value(5, 0, str(today_tmp_min) + ';'
                                     + str(int(today_hum)) + ';'
                                     + str(self.calc_hum_status(today_hum)) + ';'
                                     + str(today_press) + ';'
                                     + str(today_forecast_statu))
            self.update_device_value(11, 0, str(tomorrow_tmp_max) + ';'
                                     + str(int(tomorrow_hum)) + ';'
                                     + str(self.calc_hum_status(tomorrow_hum)) + ';'
                                     + str(tommorw_press) + ';'
                                     + str(forcast_status))

    def onStart(self):
        Domoticz.Log("onStart called")
        Domoticz.Debugging(128)
        self.repeatTime = int(Parameters["Mode5"]) * 6
        self.intervalTime = self.repeatTime
        self.heweather_air_path = ''

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        if Parameters['Mode1'] == 'Caiyun':
            # https://api.caiyunapp.com/v2/Y2FpeXVuIGFuZHJpb2QgYXBp/116.404412,39.915156/realtime.json
            self.server_name = 'https://api.caiyunapp.com'
            self.server_path = '/v2/' + Parameters['Mode2'] + '/' + Parameters['Mode3'] + ',' + Parameters[
                'Mode4'] + '/realtime.json'
            self.server_type = 1
            self.forcast_path = '/v2/' + Parameters['Mode2'] + '/' + Parameters['Mode3'] + ',' + Parameters[
                'Mode4'] + '/weather.json'
        else:
            # https://free-api.heweather.net/s6/weather/now?location=116.40,39.9&key=8e73aadb5f014e23abc507360bcdfb34
            self.server_name = 'https://free-api.heweather.net'
            self.server_path = '/s6/weather/now?location=' + Parameters['Mode3'] + ',' + Parameters['Mode4'] + '&key=' + \
                               Parameters['Mode2']
            self.server_type = 2
            self.forcast_path = '/s6/weather/forecast?location=' + Parameters['Mode3'] + ',' + Parameters[
                'Mode4'] + '&key=' + Parameters['Mode2']

            self.heweather_air_path = '/s6/air/now?location=' + Parameters['Address'] + '&key=' + Parameters['Mode2']
            print(self.heweather_air_path)

        if (len(Devices) == 0):
            Domoticz.Device(Name="Temperature", Unit=1, TypeName='Temperature', Used=1).Create()
            Domoticz.Device(Name="Feeling Temperature", Unit=6, TypeName='Temperature', Used=1).Create()
            Domoticz.Device(Name="Humidity", Unit=2, TypeName='Humidity', Used=1).Create()
            Domoticz.Device(Name="Pressure", Unit=3, TypeName='Pressure', Used=1).Create()
            Domoticz.Device(Name="PM2.5", Unit=4, TypeName="Custom", Options={"Custom": "1;μg/m³"}, Used=1).Create()
            Domoticz.Device(Name="PM10", Unit=41, TypeName="Custom", Options={"Custom": "1;μg/m³"}, Used=1).Create()
            Domoticz.Device(Name="SO2", Unit=42, TypeName="Custom", Options={"Custom": "1;μg/m³"}, Used=1).Create()
            Domoticz.Device(Name="NO2", Unit=43, TypeName="Custom", Options={"Custom": "1;μg/m³"}, Used=1).Create()
            Domoticz.Device(Name="CO", Unit=44, TypeName="Custom", Options={"Custom": "1;μg/m³"}, Used=1).Create()
            # Domoticz.Device(Name="PM2.5", Unit=4, TypeName='Air Quality', Used=1).Create()
            # Domoticz.Device(Name="PM10", Unit=41, TypeName='Air Quality', Used=1).Create()
            # Domoticz.Device(Name="SO2", Unit=42, TypeName='Air Quality', Used=1).Create()
            # Domoticz.Device(Name="NO2", Unit=43, TypeName='Air Quality', Used=1).Create()
            # Domoticz.Device(Name="CO", Unit=44, TypeName='Air Quality', Used=1).Create()
            # https://en.domoticz.cn/wiki/Developing_a_Python_plugin#Available_Device_Types
            # Temperature + Humidity + Barometer sensor
            # Device.Update(nValue, sValue)
            # nValue is always 0,
            # sValue is string with values separated by semicolon: Temperature;Humidity;Humidity Status;Barometer;Forecast
            # Humidity status: 0 - Normal, 1 - Comfort, 2 - Dry, 3 - Wet
            # Forecast: 0 - None, 1 - Sunny, 2 - PartlyCloudy, 3 - Cloudy, 4 - Rain
            Domoticz.Device(Name="THB(Today)", Unit=5, TypeName='Temp+Hum+Baro', Used=1).Create()
            Domoticz.Device(Name="THB(Tomorrow)", Unit=11, TypeName='Temp+Hum+Baro', Used=1).Create()
            Domoticz.Device(Name="Visibility", Unit=7, TypeName='Visibility', Used=1).Create()
            Domoticz.Device(Name="Wind", Unit=8, TypeName='Wind', Used=1).Create()
            Domoticz.Device(Name="Weather forecast(Today)", Unit=9, TypeName='Text', Used=1).Create()
            Domoticz.Device(Name="Weather forecast(Tomorrow)", Unit=10, TypeName='Text', Used=1).Create()
        # self.get_weather_data()
        # self.get_forcast_data()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(
            "onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def update_all_data(self):
        self.get_weather_data()
        self.get_forecast_data()
        if self.server_type == 2:
            self.get_heweather_air_data()

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        self.intervalTime += 1
        if self.intervalTime >= self.repeatTime:
            try:
                _thread.start_new_thread(self.update_all_data, ())
            except Exception as e:
                print(e)
                pass
            self.intervalTime = 0


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

