# OpenCV Haar cascades 臉部辨識程式

import cv2
import numpy as np
import os

from PIL import ImageFont, ImageDraw, Image
from PIL import Image

import argparse
import io
import time

# Set buzzer
import RPi.GPIO as gpio     
import time
piano = list([433 ]) # 無音源蜂鳴器，須提供頻率(赫茲)
buzzer = 18         # 實體pin 12，接地GND pin 14

gpio.setmode(gpio.BCM)
gpio.setup(buzzer, gpio.OUT)

# Set ultrasonic 
gpio.setwarnings(False)  	# 不顯示警告訊息
trig = 23  	 # 實體pin 16
echo = 24  	 # 實體pin 18  
gpio.setup(trig, gpio.OUT)  
gpio.setup(echo, gpio.IN)

# Set led 
from gpiozero import LED
ledr=LED(25)  	 # 實體pin 22 Red led
ledb=LED(7)  	 # 實體pin 26 Blue led

#os.chdir("/home/pi/opencv-3.5.5/data/haarcascades")
recognizer = cv2.face.LBPHFaceRecognizer_create()

#recognizer.read('/home/pi/FaceRecognition/trainer/trainer.yml')
recognizer.read('trainer/trainer.yml')

#cascadePath = "/home/pi/opencv-3.4.1/data/haarcascades/haarcascade_frontalface_default.xml"
cascadePath = "Cascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

# Define min window size to be recognized as a face
size = 30 #text size
color = (255, 255, 255) # text color 
colorr = (255, 255, 153)    # red color 
colorb = (204, 255,255)  # orange color 

fontStyle1 = ImageFont.truetype(r"./font/dffn.ttc", size, encoding="utf-8") #text font
fontStyle2 = ImageFont.truetype(r"./font/dffn.ttc", (size-10), encoding="utf-8") #text font

# iniciate id counter
id = 0
temp=1          # 0315 Add

# open file
# SQLite export table to names.txt = ['丹尼爾•克雷格','巴拉克•奧巴馬','茱莉亞•羅勃茲','梅格•萊恩']
with open('names.txt','r') as f:
    names=f.read().split("\n") 

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

# Set Buzzer
def play(pitch, sec):
    half_pitch = (1 / pitch) / 2
    t = int(pitch * sec)
    for i in range(t):
        gpio.output(buzzer, gpio.HIGH)
        time.sleep(half_pitch/2)
        gpio.output(buzzer, gpio.LOW)
        time.sleep(half_pitch/2)

# Set ultrasonic
def get_distance():          
        gpio.output(trig, gpio.HIGH)  
        time.sleep(0.02)  
        gpio.output(trig, gpio.LOW)  
  
        while gpio.input(echo)==0:  
            start = time.time()  
  
        while gpio.input(echo)==1:  
            end = time.time()  
  
        D=(end - start) * 17150  
        return D

# Set Led
def get_ledr():    
    ledr.on()
    ledb.off()

def get_ledb():      
    ledb.on()
    ledr.off()

# main 
lastTime=time.time()
while True:
    ret, img =cam.read()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )
    lapTime=round(time.time()-lastTime,2) 
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

        # Check if confidence is less them 100 ==> "0" is perfect match
        if (confidence < 100):
            id = names[id]
            confidence = "{0}%".format(round(100 - confidence))
        else:
            id = "unknown"
            confidence = "{0}%".format(round(100 - confidence))

        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))     
        draw = ImageDraw.Draw(img)                                      
        
        draw.text((x+20,y-5-30), str(id), colorb, font = fontStyle1)     
        draw.text((x,y+h+5), "正確率", colorr, font = fontStyle2)
        draw.text((x+60,y+h+5), str(confidence), colorb, font = fontStyle2)
        
        # ============================================================
        
        #elapsed_ms = (time.time() - start_time) * 10000
        timex=str(lapTime)+' sec'                
        distance_x=str(round(get_distance(),1))+" cm"  # 距離鏡頭 round 保留1個小數點        
        draw.text((x+w+3,y), "距離鏡頭", colorr, font = fontStyle2)
        draw.text((x+w+83,y), distance_x,colorb, font = fontStyle2)        
        draw.text((x+w+3,y+40), "回應時間", colorr, font = fontStyle2)
        draw.text((x+w+83,y+40), str(timex), colorb, font = fontStyle2)      
                
        img=cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR) #output data
        if (id in names):		# when id is in names  
          if (lapTime<3) :
            get_ledb()                   # blue led        
            for p in piano:              # buzzer
              play(p, 0.2)
              time.sleep(0.01)         
            if (temp==1):
              lastTime=time.time() 
              temp=0     
          else:
            get_ledr()                  # red led
            if (lapTime>6):
              lastTime=time.time()
              temp=1    
    if (lapTime>6):  
      get_ledr()
                
    cv2.imshow('camera',img)    
    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
  

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
