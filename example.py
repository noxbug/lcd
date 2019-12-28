import re
import urllib.request
from lcd import LCD


def get_weather_data():
    res = urllib.request.urlopen('https://www.meteo.be/nl/beringen').read().decode()

    keyVal = re.search(r'<observation-comp (.*?)>',res).group(1)
    weatherData = {}
    for match in re.finditer(r'(\S+?)=\"(.+?)\"',keyVal):
        weatherData[match.group(1)] = match.group(2)
    return(weatherData)


# def get_indoor_temperature():
#     nIter = 8
#     temp = 0 
#     for k in range(nIter):
#         with open('/sys/class/thermal/thermal_zone0/temp') as file:  
#             temp = temp + (int(file.read())/1000-17)/nIter
#     return(temp)


# def main():
#     
# 
# if __name__ == '__main__':
#     main()
    
weatherData = get_weather_data()
# indoorTemp  = get_indoor_temperature()
lcd = LCD()
lcd.jump_line(1)
lcd.write(weatherData['weatherDescription'])
lcd.jump_line(2)
tempStr = weatherData['temp'] + 'ßC'
windStr = weatherData['windAmount'] + weatherData['windUnit'] + ' ' + weatherData['windDirectionTxt']
weatherStr = tempStr + ' '*(20-len(tempStr)-len(windStr)) + windStr
lcd.write(weatherStr)



