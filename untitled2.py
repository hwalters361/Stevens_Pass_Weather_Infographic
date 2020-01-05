#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 14:53:49 2020

@author: hwalters
"""
# desc: 
# date: 2019-02-10
# Author: conquistadorjd
################################################################################################
from PIL import Image, ImageDraw, ImageFont

print('*** Program Started ***')

image_font_path = 'arial.ttf'

image_name_input = 'noaa.png'

######################################################################## Writing simple text on file
im = Image.open(image_name_input)
position = (50, 50)
message = "sample text"
font = ImageFont.truetype('arial.ttf', size=20)
color = (238, 242, 4)


# initialise the drawing context with the image object as background
draw = ImageDraw.Draw(im)
draw.text(position, message, fill=color, font=font)

im.show()
image_name_output = 'noaa.png'
im.save(image_name_output)

print('*** Program Ended ***')