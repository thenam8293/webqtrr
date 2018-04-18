# -*- coding: utf8 -*-

import pypyodbc
import sqlite3

def sql(query,var=''):
    connection = pypyodbc.connect('Driver={SQL Server};Server=10.62.24.161\SQLEXPRESS;Database=WEB_CONG_VIEC;uid=aos;pwd=aos159753')
    cursor = connection.cursor()
    cursor.execute(query,var)
    if query.lower().startswith('select') and not query.lower().startswith('select * into'):
        x = cursor.fetchall()
        cursor.close()
        return x
    else:
        cursor.commit()
        cursor.close()

###
def sqlite(query,var=''):
    connection = sqlite3.connect(r'static/DB/qtrr_db.db')
    cursor = connection.cursor()
    # connection.text_factory = str
    cursor.execute(query,var)
    if query.lower()[:6] == 'select':
        x = cursor.fetchall()
        connection.close()
        return x
    elif query.lower()[:6] == 'create':
        connection.close()
    else:
        connection.commit()
        connection.close()

task_field = ['task_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'executer_name', 'start_time', 'end_time', 'last_update', 'department', 'type_department', 'border_color']
event_field = ['task_id', 'event_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'executer_name', 'start_time', 'end_time', 'complete ', 'department', 'type_department', 'border_color']

# event = sql("select {} from event where department = ?".format(",".join(event_field)), ['Quản trị dữ liệu và phân tích và giám sát hoạt động tín dụng'])
# department = sql("select * from department")
id_auto_create = sql("select distinct username from Userr")


for r in id_auto_create:
    print (r)
    user_pwd = sql("select * from Userr where username = ?",r)[0]
    print(user_pwd)
    sqlite("insert into Userr values({})".format(",".join(["?"]*len(user_pwd))), user_pwd)