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
def combine_two_dicts(dict1, dict2):
    days = ["Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    
    if len(dict1) > len(dict2):
        bigger = dict1
        smaller = dict2
    elif len(dict1) < len(dict2):
        bigger = dict2
        smaller = dict1
    else:
        #the value for bigger/smaller here doesn't matter since both dicts same length
        bigger = dict1
        smaller = dict2
    
    bigger_key_list = list(bigger.keys())
    smaller_key_list = list(smaller.keys())
    bigger_val_list = list(bigger.values())
    smaller_val_list = list(smaller.values())
    
    final_dict = dict()
    start = 0
    if bigger_key_list[0] not in days and smaller_key_list[0] not in days:
            final_dict["Today"] = (bigger_val_list[0], smaller_val_list[0])
            start = 1
            
    for i in range(start,len(bigger)):
        
        if (bigger_key_list[i] in smaller_key_list):
            #find the index of the key in dict 2 for the value
            smaller_key_index = smaller_key_list.index(bigger_key_list[i])
            new_val = (bigger_val_list[i],smaller_val_list[smaller_key_index])
            final_dict[bigger_key_list[i]] = new_val
        else:
            final_dict[bigger_key_list[i]] = (bigger_val_list[i], None)
            try:
                final_dict[smaller_key_list[i]] = (smaller_val_list[i], None)
            except IndexError:
                continue
    return final_dict
                
        

def main():
    #NOAA HIGHS AND LOWS + SHORT DESCRIPTION
    
    noaa_soup = get_page_content("https://forecast.weather.gov/MapClick.php?lat=47.75&lon=-121.09#.XgsYhRdKhQI")
    noaa_results = noaa_soup.find(id='seven-day-forecast-list')
    
    noaa_twelve_hr_forecasts = noaa_results.find_all('li', class_='forecast-tombstone')
    
    noaa_high_temps = dict()
    noaa_low_temps = dict()
    noaa_desc = dict()
    
    for forecast in noaa_twelve_hr_forecasts:
        if forecast.find('p', class_='temp-low') == None and forecast.find('p', class_="temp-high") != None:
            day_title = str(forecast.find('p', class_='period-name').text)
            day_title = re.sub(r"(?<=\w)([A-Z])", r" \1", day_title)
            #removes all tags and then removes all whitespace
            high_temp = str(forecast.find('p', class_='temp-high').text)
            #removes all letters and all html tags from high_temp
            high_temp = "High "+remove_letters(high_temp)
            
            noaa_high_temps[day_title] = high_temp
            
            description = str(forecast.find('p', class_='short-desc').text)
            noaa_desc[day_title] = description
            
        elif forecast.find('p', class_='temp-high') == None and forecast.find('p', class_='temp-low') != None:
            day_title= str(forecast.find('p', class_='period-name').text)
            day_title = day_title.replace("Night","")
            
            low_temp = str(forecast.find('p', class_='temp-low').text)
            #removes all letters and all html tags
            low_temp = "Low "+remove_letters(low_temp)
            
            noaa_low_temps[day_title] = low_temp
            
            description = str(forecast.find('p', class_='short-desc').text)
            noaa_desc[day_title] = description
    
    noaa_all_temps = combine_two_dicts(noaa_high_temps, noaa_low_temps)
    
    print("~~~~0~~~~\nWeather Forecast NOAA:\n")
    print_dict(noaa_all_temps)
    print("~~~~\nWeather Descriptions NOAA:\n")
    print_dict(noaa_desc)
    
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
    
    
    for i in range(3):
        break
    
    draw.text((50,150), noaa_day_titles[0], fill=color, font=font)
        
        
    im.show()
    image_name_output = 'Stevens Pass Infographic Template.jpg'
    im.save(image_name_output)
    
    
if __name__ == "__main__":
    main()
    
    
    