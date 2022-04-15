import time
import tkinter as tk
from tkinter import messagebox

window = tk.Tk() #新增視窗
window.title('智慧門鎖') #命名此視窗
window.geometry("480x320+0-40") #設定視窗大小
window.configure(bg='#E8CCFF') #設定設窗背景顏色

def validate(P): #註冊輸入框使其只能輸入數字
    if str.isdigit(P) or P == '':
        return True
    else:
        return False

def exit(): #關閉
    window.destroy() 

def enter():
    if entry.get() != '':
        get_text = entry.get() #取得輸入欄數值
        if get_text == '12345':
            tk.messagebox.showinfo('智慧門鎖', '密碼輸入正確！\n門鎖已開啟') #正確
            localtime = time.localtime()
            result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime) #時間
            with open("success.txt","a",encoding="utf8") as file: #紀錄開門資訊
                file.write("名稱：VIP  時間："+result+"\n")
            exit()
        else:
            tk.messagebox.showinfo('智慧門鎖', '密碼輸入錯誤！\n請再重新嘗試') #錯誤



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
button = tk.Button(window,text = '離開',width = 5,command = exit)
button.place(relx=0.282, rely=0.87)
button = tk.Button(window,text = '清除',width = 5,command = lambda:entry.delete(0,"end"))
button.place(relx=0.433, rely=0.87)
button = tk.Button(window,text = '輸入',width = 5,command = enter) 
button.place(relx=0.584, rely=0.87)

window.mainloop() #執行視窗
