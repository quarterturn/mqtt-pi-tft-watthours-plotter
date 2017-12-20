import sys
import os, syslog
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot
import matplotlib.ticker as ticker
import pygame
from pygame.locals import *
import time
from time import strftime, localtime
import string
import pylab
import Image
import paho.mqtt.client as mqtt
import numpy as np
from collections import deque

# queue to hold graph data 
# use queue so we can push new data on from the left of the list
# which makes it easier for new data to appear at the origin of the graph
watthours = deque([])

# font colors
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)
colorRed = (255, 0, 0)


# matlibplot stuff
tftXSize = 2.90
tftYSize = 1.99
size = width, height = 480, 320

# se the tft as the display
os.environ["SDL_FBDEV"] = "/dev/fb1"
# initilalize pygame
pygame.init()
# hide the mouse pointer
pygame.mouse.set_visible(0)

print("press ctrl-c here")

# font size
matplotlib.rcParams.update({'font.size': 5})

# set up the window
screen = pygame.display.set_mode((480, 320))
fig, ax = pyplot.subplots()
fig.set_size_inches(tftXSize, tftYSize)
fig.dpi = 160
background = pygame.Surface(screen.get_size())
background = background.convert()

def on_connect(mqttc, obj, flags, rc):
    print("connected to mqtt publisher")
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    global humidity
    tick_spacing = 1
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    
    # clear off the last plot 
    pyplot.cla()

    # update the array and scroll off old data
    if msg.topic == "house_data/watthours":
        watthours.appendleft(msg.payload)
        watthours.pop()

    # watthours
    ax.set_title("Watthours")
    ax.set_ylabel("WH")
    ax.set_xlabel("minutes")
    # create x-axis ticks every 60 minutes
    ax.xaxis.set_major_locator(ticker.MultipleLocator(60))
    ax.xaxis.grid(True)
    ax.yaxis.grid(True)
    ax.plot(watthours)
    ax.set_ylim(ymin=0)

    pylab.savefig('graph.png', dpi=160)

    # render the data to the buffer and display
    img = pygame.image.load('graph.png')
    screen.blit(img, (0, 0))
    pygame.display.flip()

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')

# pre-load the queue
for i in range(0, 359):
    watthours.append(0)

# main code
client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect

client.connect("192.168.0.21")

client.subscribe("house_data/watthours")

client.loop_forever()
