# 輸入密碼程式

import time
import tkinter as tk
from tkinter import messagebox

window = tk.Tk()

window.title('Test')

window.geometry("640x480+250+150")
window.configure(bg='#E8CCFF')

def exit():
    window.destroy() 

def enter():
    if entry.get() != '':
        get_text = entry.get()
        if get_text == 'ccsh110':
            tk.messagebox.showinfo('智慧門鎖', '密碼輸入正確！\n門鎖已開啟')
            localtime = time.localtime()
            result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime) #時間
            with open("success.txt","a",encoding="utf8") as file: #覆蓋檔案
                file.write("名稱：VIP  時間："+result+"\n")
            window.destroy() 
        else:
            tk.messagebox.showinfo('智慧門鎖', '密碼輸入錯誤！\n請再重新嘗試')

label = tk.Label(window,                
                 text = '\n請輸入密碼：',      
                 font = ('Arial', 12),   
                 bg = '#E8CCFF',
                 width = 15, height = 2)

label.pack()

entry = tk.Entry(window,    
                 width = 20)
entry.pack()

label = tk.Label(window,              
                 text = '\n',  
                 font = ('Arial', 12), 
                 bg = '#E8CCFF',
                 width = 15, height = 2)

label.pack()

button = tk.Button(window,         
                   text = '離開',  
                   command = exit) 
button.pack()
button = tk.Button(window,       
                   text = '輸入',  
                   command = enter) 
button.pack()

window.mainloop()