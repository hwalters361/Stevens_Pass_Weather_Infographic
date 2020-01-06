#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 13:05:54 2019

@author: hwalters



"""
CHANGE_WALLPAPER = True

import requests
from bs4 import BeautifulSoup
import os
import re

def get_page_content(url):
    agent = {"User-Agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    page = requests.get(url, headers=agent, timeout=5)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def print_dict(dict_):
    for x,y in dict_.items():
        print(str(x)+":"+str(y))

def remove_letters(string):
    for i in string:
        try:
            i = int(i)
        except ValueError:
            string=string.replace(i,"")
    return string

#items with the same key, values combined into tuple. also contains a 
def make_weather_dict(list1, list2):
    total_list = list1+list2
    total_list.sort()
    
    temp_dict = dict()
    for i in range(len(total_list)):
        item = total_list[i]
        #removes the number at the beginning of the item placed there for order
        item = item[1:]
        
        #finds the index of the slash separating the temperature from the day title
        slash_index = item.find("/")
        
        #finds the day_title based off the slash location
        day_title = item[slash_index+1:]
        
        #finds the temp value based off the slash location
        temp = item[:slash_index]
        
        temp_dict_keys = list(temp_dict.keys())
        
        if day_title in temp_dict_keys:
            prev_value = temp_dict[day_title]
            #takes the first value of the tuple, so the previous value isn't a tuple
            first,x = prev_value
            
            temp_dict[day_title] = (first, temp)
        else:
            temp_dict[day_title] = (temp, None)

    return temp_dict

def main():
    #NOAA HIGHS AND LOWS + SHORT DESCRIPTION
    
    noaa_soup = get_page_content("https://forecast.weather.gov/MapClick.php?lat=47.75&lon=-121.09#.XgsYhRdKhQI")
    noaa_results = noaa_soup.find(id='seven-day-forecast-list')
    
    noaa_twelve_hr_forecasts = noaa_results.find_all('li', class_='forecast-tombstone')

    noaa_desc = dict()
    
    noaa_high_temps = []
    noaa_low_temps = []
    order = 0
    for forecast in noaa_twelve_hr_forecasts:
        day_title = str(forecast.find('p', class_='period-name').text)
        day_title = re.sub(r"(?<=\w)([A-Z])", r" \1", day_title).replace("Night","").replace(" ","")
        
        if "NOW" in day_title.replace(" ",""):
            continue
        if forecast.find('p', class_='temp-low') == None:
        #must have a high temperature
            #removes all tags and then removes all whitespace
            high_temp = str(forecast.find('p', class_='temp-high').text)
            #removes all letters and all html tags from high_temp
            high_temp = "High "+remove_letters(high_temp)
            
            noaa_high_temps.append(str(order)+high_temp + "/" + day_title)
            
            description = str(forecast.find('p', class_='short-desc').text)
            noaa_desc[day_title] = description
        else:
            low_temp = str(forecast.find('p', class_='temp-low').text)
            #removes all letters and all html tags
            low_temp = "Low "+remove_letters(low_temp)
            
            noaa_low_temps.append(str(order)+low_temp + "/" + day_title)
            
            description = str(forecast.find('p', class_='short-desc').text)
            noaa_desc[day_title] = description
        order+=1

    noaa_all_temps = make_weather_dict(noaa_high_temps, noaa_low_temps)

    print("~~~~0~~~~\nWeather Forecast NOAA:\n")
    print_dict(noaa_all_temps)
    print("~~~~\nWeather Descriptions NOAA:\n")
    print_dict(noaa_desc)
    """
    #ACCU WEATHER HIGHS AND LOWS + SHORT DESCRIPTION
    accu_soup = get_page_content("https://www.accuweather.com/en/us/stevens-pass/98826/daily-weather-forecast/103026_poi")
    
    accu_daily_forecasts=[]
    #gets the forecasts for the week. There are more weather forecasts afterwards
    #but I don't want to collect those.
    for i in range(0,6):
        forecasts = accu_soup.find_all("a", class_="forecast-card")[i]
        accu_daily_forecasts.append(forecasts)
         

    accu_all_temps = dict()
    accu_desc = dict()
    accu_precip_chances = dict()
    
    for forecast in accu_daily_forecasts:
        high_temp = str(forecast.find('span',class_='high').text)
        low_temp = str(forecast.find('span',class_='low').text)
        
        description = str(forecast.find('span',class_='phrase').text)
        
        precip = str(forecast.find('div',class_='info precip').text)
        
        day_title = str(forecast.find('p',class_='dow').text)
        day_title = day_title.strip()
       
        #remove_letters() also acts as .strip() so adding .strip() is not needed for temps and precip chances
        accu_desc[day_title] = description.strip()
        accu_all_temps[day_title] = ("High "+remove_letters(high_temp), "Low "+remove_letters(low_temp))
        
        accu_precip_chances[day_title] = remove_letters(precip)+"%"
    print("~~~~0~~~~\nWeather Forecast Accuweather:\n")
    print_dict(accu_all_temps)
    print("~~~~\nWeather descriptions Accuweather:\n")
    print_dict(accu_desc)
    print("~~~~\nWeather Precip Chances Accuweather:\n")
    print_dict(accu_precip_chances)
    
    #WEATHER.COM
    weather_soup = get_page_content("https://weather.com/weather/tenday/l/b34e2407cc3f2fc39f372621e6ecbccbf0f1e8467b293bdb398370f53cb86e6a")
    weather_results = weather_soup.find("tbody")
    
    weather_daily_forecasts = weather_results.find_all("tr", class_="clickable closed")
    
    weather_all_temps = dict()
    weather_desc = dict()
    weather_precip_chances = dict()
    i=0
    for forecast in weather_daily_forecasts:
        day_title = forecast.find('td', headers="day")
        day_title = str(day_title.find('span',class_="date-time").text).strip() + " " + str(day_title.find('span', class_="day-detail clearfix").text).strip()
        
        temp = str(forecast.find('td',class_="temp").text)
        #the temperature right now looks like this "26º22º" with high and low
        #pressed together w/ a degree symbol in between. To separate I find the
        #first degree symbol and use that to separate the two numbers.
        if "-" not in temp:
            char_index = temp.find("°")
            high_temp = "High "+remove_letters(temp[:char_index])
            low_temp = "Low "+remove_letters(temp[char_index:])
        else:
            temp2 = temp.replace("--","").strip()
            if temp.find("-") == 0:
                high_temp = None
                low_temp = "Low "+remove_letters(temp2)
            else:
                low_temp = None
                high_temp = "High "+remove_letters(temp2)
            
        weather_all_temps[day_title] = (high_temp, low_temp)
        
        desc = str(forecast.find('td', class_="description").text).strip()
        weather_desc[day_title] = desc
        
        precip = str(forecast.find('td', class_="precip").text).strip()
        weather_precip_chances[day_title] = precip
        i+=1
        if i == 6:
            break
    print("~~~~0~~~~\nWeather Forecast Weather Channel:\n")
    print_dict(weather_all_temps)
    print("~~~~\nWeather descriptions Weather Channel:\n")
    print_dict(weather_desc)
    print("~~~~\nWeather Precip Chances Weather Channel:\n")
    print_dict(weather_precip_chances)
    
    #EDIT THE TEMPLATE INFOGRAPHIC
    os.remove("Stevens Pass Infographic Template.jpg")
    print("Copy template removed successfully")
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open('Stevens Pass Infographic.jpg')
    font = ImageFont.truetype('arial.ttf', size=20)
    color = (105,105,105)
    
    # initialise the drawing context with the image object as background
    draw = ImageDraw.Draw(im)
    
    #DISPLAY NOAA DATA ONTO JPG
    noaa_day_titles = list(noaa_all_temps.keys())
    accu_day_titles = list(accu_all_temps.keys())
    weather_day_titles = list(weather_all_temps.keys())
    
    all_tm = 150
    noaa_lm = 50
    for i in range(3):
        break
    
    draw.text((noaa_lm,all_tm), noaa_day_titles[0], fill=color, font=font)
        
        
    im.show()
    image_name_output = 'Stevens Pass Infographic Template.jpg'
    im.save(image_name_output)
    
    """
if __name__ == "__main__":
    main()
    
    
    