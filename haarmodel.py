# OpenCV Haar cascades建模程式

import cv2
import numpy as np
from PIL import Image
import os

# 照片資料庫儲存路徑，將蒐集照片存此資料夾
path = 'dataset'

# 使用Haar cascades LBPH建模方法
recognizer = cv2.face.LBPHFaceRecognizer_create()

# 使用Haar cascades 臉部辨識方法
detector = cv2.CascadeClassifier("Cascades/haarcascade_frontalface_default.xml");

# 建立照片集及標籤函數
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    faceSamples=[]
    ids = []
    for imagePath in imagePaths:
		# 利用PIL模組建立將照片轉成灰階
        PIL_img = Image.open(imagePath).convert('L') 
		
		# 利用numpy模組將照片轉成array方式
        img_numpy = np.array(PIL_img,'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
		
		# 使用Haar cascades 方法界定臉部框架
        faces = detector.detectMultiScale(
 			img_numpy,
 			scaleFactor = 1.2,
 			minNeighbors = 5,
 			minSize = (64, 48),
 			)

		
		# 將辨識照片及標籤存於faces
        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)
    return faceSamples,ids

faces,ids = getImagesAndLabels(path)
# 開始訓練建模
recognizer.train(faces, np.array(ids))
# 將訓練完的模型存trainer/trainer.yml
recognizer.write('trainer/trainer.yml')