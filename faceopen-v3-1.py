# Try

# === AI臉部辨識門禁系統攻略程式 ====
# 匯入相關模組
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

import os
import argparse
import io
import time
import tkinter as tk
from tkinter import messagebox

# 匯入Google Tensorflow Lite模組
import tensorflow.lite as tflite

# 設定拍攝解析度
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# 設定蜂鳴器
import RPi.GPIO as gpio     
piano = list([433 ])    # 無音源蜂鳴器，提供頻率
buzzer = 13             # GPIO 13(實體pin 3)，另一線接GND
gpio.setmode(gpio.BCM)  # 設定GPIO 接腳功能
gpio.setup(buzzer, gpio.OUT)

# 設定超音波 
gpio.setwarnings(False)  	# 不顯示警告訊息
trig = 5  	 # GPIO 5(實體pin 29)
echo = 6  	 # GPIO 6(實體pin 31)  
gpio.setup(trig, gpio.OUT)  
gpio.setup(echo, gpio.IN)

# 設定Led 
from gpiozero import LED    # 匯入GPIO模組
ledr=LED(19)  	 # GPIO 19(實體pin 35)
ledb=LED(26)  	 # GPIO 26(實體pin 37)

# 設定 電磁鎖
import RPi.GPIO as gpio 
door = 21             # GPIO 21(實體pin 40)，另一線接GND
gpio.setmode(gpio.BCM)  # 設定GPIO 接腳功能
gpio.setup(door, gpio.OUT)

# 設定字形大小、顏色
size = 35 
color = (255, 255, 255)  
colorr = (255, 255, 255) 
colorb = (255, 255,255) 

# 設定繁體中文採用字形-華康超黑體
fontStyle1 = ImageFont.truetype(r"./font/dffn_2.ttc", size, encoding="utf-8") 
fontStyle2 = ImageFont.truetype(r"./font/dffn_2.ttc", (size-10), encoding="utf-8") 

# 設定全域變數
id = 0
temp=1 
ledx=1

# 使用OpenCV模組方法cv2.face.LBPHFaceRecognizer_create()
recognizer = cv2.face.LBPHFaceRecognizer_create()

# 使用OpenCV模組已訓練的臉部識別模型文件hhaarcascade_frontalface_default.xml
cascadePath = "Cascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
    
# 讀取SQLite 資料表輸出的txt檔(names.txt)
with open('names.txt','r') as f:
    names=f.read().split("\n") 

# 設定蜂鳴器功能
def play(pitch, sec):
    half_pitch = (1 / pitch) / 2
    t = int(pitch * sec)
    for i in range(t):
        gpio.output(buzzer, gpio.HIGH)
        time.sleep(half_pitch/2)
        gpio.output(buzzer, gpio.LOW)
        time.sleep(half_pitch/2)
        
# 設定電磁鎖功能=======================================================
def get_door():
    gpio.output(door, gpio.HIGH)
    time.sleep(0.5)
    gpio.output(door, gpio.LOW)
    time.sleep(0.5)

# 設定超音波功能
def get_distance():          
        gpio.output(trig, gpio.HIGH)  
        time.sleep(0.02)          # 設定20ms，讓超音波有間隔，可較準確量測距離    
        gpio.output(trig, gpio.LOW)    
        while gpio.input(echo)==0:  
            start1 = time.time()    
        while gpio.input(echo)==1:  
            end = time.time()  
        D=(end - start1) * 17150  # 聲音速度343m/s，須除以2（因來回音波）
        return D

# 設定紅色Led功能
def get_ledr(ledx):       
    ledy=ledx%20
    if(ledy<10):
        ledr.on()
    else:
        ledr.off()
        
    ledx=ledx+1
    ledb.off()
    return ledx

# 設定藍紅色Led功能
def get_ledb():      
    ledb.on()
    ledr.off()

# 設定目前時間 
lastTime=time.time()
pwtime=time.time()
detect=0

# 設定Webcam及解析度640*480
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height


# 設定臉部識別的影像視窗的最小解析度64*48
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

# 讀取Tensorflow Lite 標籤檔
def load_labels(label_path):
    r"""Returns a list of labels"""
    with open(label_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

# 讀取Tensorflow Lite 模型檔
def load_model(model_path):
    r"""Load TFLite model, returns a Interpreter instance."""
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

# 使用Tensorflow Lite 臉部辨識方法
def process_image(interpreter, image, input_index, k):
    r"""Process an image, Return top K result in a list of 2-Tuple(confidence_score, _id)"""
    input_data = np.expand_dims(image, axis=0)  

    # 使用Tensorflow Lite方法
    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()

    # 得到輸出結果
    output_details = interpreter.get_output_details()
    output_data = interpreter.get_tensor(output_details[0]['index'])    
    output_data = np.squeeze(output_data)

    # 可獲到臉部辨識的個數，一般指定1個即可(辨識率最高)
    top_k = output_data.argsort()[-k:][::-1]  
    result = []
    
    for _id in top_k:
        score = float(output_data[_id] / 255.0)
        result.append((_id, score))

    return result

# 檔案被直接執行時，以下程式將被執行
if __name__ == "__main__":
    # 設定Tonsorflow Lite 模型檔
    model_path = './trainer/model.tflite'
    
    # 設定Tonsorflow Lite 標籤檔
    label_path = './trainer/labels.txt'
    interpreter = load_model(model_path)
    labels = load_labels(label_path)

    input_details = interpreter.get_input_details()

    #獲得TensorFlow Lite 深度學習臉部辨識結果
    input_shape = input_details[0]['shape']
    height = input_shape[1]
    width = input_shape[2]

    # 獲得辨識結果的第1個索引
    input_index = input_details[0]['index']

    # 處理拍攝影像、框架及辨識
    while True: 
        ledx=get_ledr(ledx)  
        ret, img = cam.read()  
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
            )
        lapTime=round(time.time()-lastTime,2)

        image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        image = image.resize((width, height))
        k = 1 # 設定獲得辨識結果的個數1個(最高辨識率）  
        top_result = process_image(interpreter, image, input_index,k)

        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))     
            draw = ImageDraw.Draw(img)   
            # 獲得辨識結果索引、辨識率
            for idx, (_id, score) in enumerate(top_result): 
                id = labels[_id]
                confidence=score
                confidence=round(float(confidence)*100,1)   # 辨識率取1位小數                                 
        
            draw.text((x+20,y-5-30), str(id), colorb, font = fontStyle1)     
            draw.text((x+20,y+h+5), "正確率", colorr, font = fontStyle2)
            draw.text((x+120,y+h+5), str(confidence)+"%", colorb, font = fontStyle2)              
            timex=str(lapTime)+' sec'                
            distance_x=str(round(get_distance(),1))+" cm"  # 距離鏡頭 round 取1位小數        
            draw.text((x+w+3,y), "距離鏡頭", colorr, font = fontStyle2)
            draw.text((x+w+120,y), distance_x,colorb, font = fontStyle2)        
            draw.text((x+w+3,y+40), "回應時間", colorr, font = fontStyle2)
            draw.text((x+w+120,y+40), str(timex), colorb, font = fontStyle2)      
                
            img=cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR) # 輸出資料
            
            if (id in names):		# 辨識標籤結果與資料庫names.txt作比對
                if (int(confidence)>=90):           # 設定辨識率達80%為辨識成功
                    pwtime=time.time()
                    detect = 0
                    if (lapTime<3) :                # 限定3秒   
                        get_ledb()                  # 執行藍色Led        
                        for p in piano:             # 執行㖓鳴器
                            play(p, 0.2)
                            time.sleep(0.01)         

                        
                        if (temp==1):
                            lastTime=time.time()    # 當藍色Led亮起，重算時間    
                            get_door()                  # ================================================       
                            print("Open_door")           # ===============================================                           

                            temp=0
                            localtime = time.localtime()
                            result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime) #時間
                            with open("success.txt","a",encoding="utf8") as file: #覆蓋檔案
                                file.write("名稱："+id+"  時間："+result+"\n") 
                    else:
                        get_ledr(ledx)              # 執行紅色Led
                        if (lapTime>8):             # 超過8秒，重算時間   
                            lastTime=time.time()
                            pwtime=time.time()
                            temp=1
                else:
                    #==================================================================
                    #print(time.time()-pwtime)
                    if (round(time.time()-pwtime,2)>8 and detect==0):          #偵測8秒
                        window = tk.Tk()                #新增視窗
                        window.title('智慧門鎖')         #命名此視窗
                        window.geometry("480x320+0-40") #設定視窗大小
                        window.configure(bg='#E8CCFF')  #設定設窗背景顏色
                        detect=1                        # =============================

                        def validate(P):                #註冊輸入框使其只能輸入數字
                            if str.isdigit(P) or P == '':
                                return True
                            else:
                                return False

                        def exitc():                     #關閉
                            detect = 1
                            pwtime=time.time()          # ======================================    
                            window.destroy()

                        def enter():
                            if entry.get() != '':
                                get_text = entry.get() #取得輸入欄數值
                                if get_text == '12345':
     
                                    
                                    tk.messagebox.showinfo('智慧門鎖', '密碼輸入正確！\n門鎖已開啟')   #正確
                                    localtime = time.localtime()
                                    result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime)    #時間
                                    with open("success.txt","a",encoding="utf8") as file:        #紀錄開門資訊
                                        file.write("名稱：VIP  時間："+result+"\n")
                                    detect = 1
                                    get_door()                  # ================================================       
                                    print("Open_door")           # ===============================================   
                                    exitc()
                                  
                                else:
                                    tk.messagebox.showinfo('智慧門鎖', '密碼輸入錯誤！\n請再重新嘗試') #錯誤
                                    entry.delete(0,"end")

                        label = tk.Label(window,text = '\n請輸入密碼：',font = ('Arial', 12),   bg = '#E8CCFF',width = 15, height = 2) #新增文字
                        label.pack()

                        vcmd = (window.register(validate), '%P')
                        entry = tk.Entry(window,width = 20,validate='key',validatecommand=vcmd) #新增輸入框
                        entry.pack()

                        #新增輸入用數字按鈕
                        button = tk.Button(window,text="1",command=lambda:entry.insert(100,1))
                        button.place(relx=0.312,rely=0.28)
                        button = tk.Button(window,text="2",command=lambda:entry.insert(100,2))
                        button.place(relx=0.462,rely=0.28)
                        button = tk.Button(window,text="3",command=lambda:entry.insert(100,3))
                        button.place(relx=0.612,rely=0.28)
                        button = tk.Button(window,text="4",command=lambda:entry.insert(100,4))
                        button.place(relx=0.312,rely=0.48)
                        button = tk.Button(window,text="5",command=lambda:entry.insert(100,5))
                        button.place(relx=0.462,rely=0.48)
                        button = tk.Button(window,text="6",command=lambda:entry.insert(100,6))
                        button.place(relx=0.612,rely=0.48)
                        button = tk.Button(window,text="7",command=lambda:entry.insert(100,7))
                        button.place(relx=0.312,rely=0.68)
                        button = tk.Button(window,text="8",command=lambda:entry.insert(100,8))
                        button.place(relx=0.462,rely=0.68)
                        button = tk.Button(window,text="9",command=lambda:entry.insert(100,9))
                        button.place(relx=0.612,rely=0.68)
                        button = tk.Button(window,text="9",command=lambda:entry.insert(100,9))
                        button.place(relx=0.612,rely=0.68)


                        #新增功能按鈕
                        button = tk.Button(window,text = '離開',width = 5,command = exitc)
                        button.place(relx=0.282, rely=0.87)
                        button = tk.Button(window,text = '清除',width = 5,command = lambda:entry.delete(0,"end"))
                        button.place(relx=0.433, rely=0.87)
                        button = tk.Button(window,text = '輸入',width = 5,command = enter) 
                        button.place(relx=0.584, rely=0.87)

                        window.mainloop() #執行視窗

                if (lapTime>8):                             # 超過8秒執行紅色Led             
                    ledx=get_ledr(ledx) 
            else:
                ledx=get_ledr(x) 
        #else:
        #if (temp==0):
        ledx=get_ledr(ledx)                
                  
        cv2.imshow('camera',img)    
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

