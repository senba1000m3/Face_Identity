# SQLite 管理程式

# -*- coding: utf-8 -*-
import sqlite3

def disp_menu():
    print("臉部辨識資料編輯")
    print("------------")
    print("1.新增")
    print("2.編輯")
    print("3.刪除")
    print("4.顯示")
    print("5.存檔")    
    print("0.結束")
    print("------------")

# 1. 新增
def append_data():
    while True:
        no = int(input("請輸入臉部編號(id)(-1停止輸入):"))
        if no == -1: break
        name = input("請輸入姓名:")
        sqlstr = "select * from student where stdno={};".format(no)
        cursor = conn.execute(sqlstr)
        if len(cursor.fetchall()) > 0:
            print("您輸入的編號(id)已經有資料了")
        else:
            sqlstr = \
              "insert into student values({},'{}');".format(no,name)
            conn.execute(sqlstr)
            conn.commit()

# 2. 編輯
def edit_data():
    no = input("請輸入要編輯的臉部編號(id):")
    sqlstr = "select * from student where stdno={};".format(no)
    cursor = conn.execute(sqlstr)
    rows = cursor.fetchall()
    if len(rows) > 0:
        print("目前的姓名:",rows[0][1])
        name = input("請輸入姓名：")
        sqlstr = \
          "update student set name='{}' where stdno={};".format(name, no)
        conn.execute(sqlstr)
        conn.commit()
    else:
        print("找不到要編輯的臉部編號(id)")

# 3. 刪除
def del_data():
    no = input("請輸入要刪除的臉部編號(id):")
    sqlstr = "select * from student where stdno={};".format(no)
    cursor = conn.execute(sqlstr)
    rows = cursor.fetchall()
    if len(rows) > 0:
        print("你目前要刪除的是編號(id){}的{}".format(rows[0][0], rows[0][1]))
        answer = input("確定要刪除嗎？(y/n)")
        if answer == 'y' or answer == 'Y':
            sqlstr = "delete from student where stdno={};".format(no)
            conn.execute(sqlstr)
            conn.commit()
            print("已刪除指定的臉部...")
    else:
        print("找不到要刪除的臉部")

# 4. 顯示
def disp_data():
    cursor = conn.execute('select * from student;')
    for row in cursor:
        print("No {}: {}".format(row[0],row[1]))
        
# 5. 存檔
def save_data():
    f=open('names.txt','w')
    cursor = conn.execute('select * from student;')
    for row in cursor:
        f.write(row[1]+'\n')
    f.close    

conn = sqlite3.connect('scores.sqlite')

while True:
    disp_menu()
    choice = int(input("請輸入您的選擇:"))
    if choice == 0 : break
    if choice == 1: 
        append_data()
    elif choice == 2:
        edit_data()
    elif choice == 3:
        del_data()
    elif choice == 4:
        disp_data()
    elif choice == 5:
        save_data()        
    else: break
    x = input("請按Enter鍵回主選單")
