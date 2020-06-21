Domoticz Baby Weather Plugin
====

支持彩云天气，和风天气，需要注册开发者账号之后添加apikey之后才能使用。  
彩云天气：https://open.caiyunapp.com/  
和风天气：https://dev.heweather.com/  

支持信息：  
- Temperature - 当前温度
- Feeling Temperature - 当前体感温度
- Humidity - 湿度
- Pressure - 气压
- PM25 - 当前PM25浓度
- PM10 - 当前PM10浓度
- SO2 - 当前PSO2浓度
- Weather forecast(Today) - 今天天气
- Weather forecast(Tomorrow) - 明天天气
- 等等  

安装方法：
> 1. 下载zip之后解压缩，放入Domoticz/plugins目录下，重启服务端。去网页端添加硬件即可。  
> 2. 切换到插件目录下，git clone https://github.com/obaby/baby_weather_plugin 重启服务端。去网页端添加硬件即可。  

添加硬件截图：  
![device](screenshot/device.jpg)  

终端运行效果:  
![console](screenshot/console.png)  

数据信息：  
![weather](screenshot/weather.png)  
![wind](screenshot/wind.png)  
![temp](screenshot/temp.png)  
![home](screenshot/home.png)  

项目依赖：  
requests
```bash
pip3 install requests
```


> @author: obaby  
> @license: (C) Copyright 2013-2020, obaby@mars.  
> @contact: root@obaby.org.cn  
> @link: http://www.obaby.org.cn  
> @blog: http://www.h4ck.org.cn  
> @findu: http://www.findu.co  