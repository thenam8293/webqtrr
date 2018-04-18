# -*- coding: utf8 -*-

from __future__ import division
import os
from os import environ
import sys
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine, inspect, or_, and_, update, func

from config import Config
from model import app, db, Event, Task, Event_log, Department, Userr, ID_auto, Admin_depatment, Profile, ID_auto

from flask import Flask


from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, session, flash,jsonify
from functools import wraps

import uuid
import hashlib
import datetime as dt
import random
from operator import itemgetter
import ast



app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=900)

start_date_demo = dt.datetime(2017,4,2)
special_day = dt.datetime(1993,9,19)
time_begin_default = '07:00'
time_finish_default = '21:00'
work_hour_default = 14
min_unit_default = 15

task_field = ['task_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'executer_name', 'start_time','end_time', 'last_update', 'department', 'type_department', 'border_color']
event_field = ['task_id','event_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'executer_name', 'start_time', 'end_time', 'complete', 'department', 'type_department', 'border_color']

department_field = ["department","type_department","type","type_strategy"]
list_type = ["Thẩm định,phê duyệt,phân luồng", "Vận hành Hội đồng, Ủy ban", "Giám sát,nhận diện, cảnh báo", "Cải tiến hệ thống, mô hình, quy trình", "Xây dựng kiểm soát Budget","Xây dựng, quy định, chính sách, quy trình", "Mua bán, xử lý nợ", "Tư vấn,giải đáp", "Hành chính, văn phòng", "Phát triển nhân lực", "Tham gia dự án", "Báo cáo, dữ liệ", "Khác"]
list_type_strategy = ["Vận hành", "Dữ liệu", "Nhân sự", "Quy trình, chính sách", "Văn hóa"]
sub_mail = 'Hệ thống quản lý công việc - Khối QTRR'
list_department = ['Khối QTRR', 'Quản trị dữ liệu và phân tích và giám sát hoạt động tín dụng', 'QTRR phân khúc khách hàng doanh nghiệp', 'Quản lý và giám sát tài sản đảm bảo', 'Quản lý thu hồi nợ', 'Quản trị rủi ro thị trường', 'PFSR', 'Quản trị danh mục - phân tích rủi ro và công cụ mô hình', 'Chiến lược rủi ro', 'QTRR khách hàng doanh nghiệp lớn và định chế tài chính', 'Phê duyệt - nhóm chuyên gia phê duyệt', "Rủi ro hoạt động"]
list_department_viettat = ['Khối QTRR', 'AOS', 'BBR', 'Collateral', 'Collection', 'Market Risk', 'PFSR', 'Portfolio', 'Strategy', 'WBR','Approver','Operation Risk']

def hash_user(user):
    return hashlib.md5(user.encode('utf-8')).hexdigest()
def hash_2(user):
    return hashlib.sha1(user.encode('utf-8')).hexdigest()
def hash_3(user):
    return hashlib.sha256(user.encode('utf-8')).hexdigest()
def dt_to_str(x):
    return '{} {}/{}/{}'.format(str(x)[11:16],str(x)[8:10],str(x)[5:7],str(x)[:4])
def dt_to_str_nguoc(x):
    # Transfer datatime to string
    return str(x.date())[-2:] + '/'+str(x.date())[-5:-3] + '/' +  str(x.date())[:-6]
def d_to_str(x):
    return '{}/{}/{}'.format(str(x)[8:10],str(x)[5:7],str(x)[:4])
def dt_to_str2(x):
    # Use for day-picker
    if x.weekday() == 6:
        return u'Chủ Nhật*{}/{}'.format(str(x)[8:10],str(x)[5:7])
    else:
        return u'Thứ {}*{}/{}'.format(str(x.weekday()+2),str(x)[8:10],str(x)[5:7])
def str_to_dt(x):
    try:
        return dt.datetime.strptime(x,'%H:%M %d/%m/%Y')
    except:
        return dt.datetime.strptime(x,'%d/%m/%Y')
def list_optimize(list_number,list_label):
    # remove 0 in list, round 1 and config to add up to 100% then sorted
    list_label = [r for i,r in enumerate(list_label) if list_number[i] != 0]
    list_number = [round(r,1) for r in list_number if r != 0]
    index_max_number = list_number.index(max(list_number))
    list_number[index_max_number] = 100 - sum([r for i,r in enumerate(list_number) if i != index_max_number])

    list_label = [r[1] for r in sorted(zip(list_number,list_label), reverse = True)]
    list_number = sorted(list_number, reverse = True)
    return list_number, list_label

def time_config(start_time, end_time):
    if not start_time:
        start_time = dt.datetime(2017,4,2)
    if not end_time or end_time > dt.datetime.now():
        end_time = dt.datetime.now()
    end_time = dt.datetime.combine(end_time.date(),dt.time(23,59,59))
    return (start_time, end_time)

def khung_gio(x,y):
    return ['07:00','21:00',15,14]
def index_to_time(x):
    a = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57'] 
    b = [dt.time(7, 0), dt.time(7, 15), dt.time(7, 30), dt.time(7, 45), dt.time(8, 0), dt.time(8, 15), dt.time(8, 30), dt.time(8, 45), dt.time(9, 0), dt.time(9, 15), dt.time(9, 30), dt.time(9, 45), dt.time(10, 0), dt.time(10, 15), dt.time(10, 30), dt.time(10, 45), dt.time(11, 0), dt.time(11, 15), dt.time(11, 30), dt.time(11, 45), dt.time(12, 0), dt.time(12, 15), dt.time(12, 30), dt.time(12, 45), dt.time(13, 0), dt.time(13, 15), dt.time(13, 30), dt.time(13, 45), dt.time(14, 0), dt.time(14, 15), dt.time(14, 30), dt.time(14, 45), dt.time(15, 0), dt.time(15, 15), dt.time(15, 30), dt.time(15, 45), dt.time(16, 0), dt.time(16, 15), dt.time(16, 30), dt.time(16, 45), dt.time(17, 0), dt.time(17, 15), dt.time(17, 30), dt.time(17, 45), dt.time(18, 0), dt.time(18, 15), dt.time(18, 30), dt.time(18, 45), dt.time(19, 0), dt.time(19, 15), dt.time(19, 30), dt.time(19, 45), dt.time(20, 0), dt.time(20, 15), dt.time(20, 30), dt.time(20, 45), dt.time(21, 0)]

    return dt_to_str(dt.datetime.combine(session['day_selected'].date(),[b[i] for i,r in enumerate(a) if r == x][0]))

def time_dif(x,y,z=''):
    ## Return time different (second) between start time and end time
    # x : start time (datetime)
    # y : end time (datetime)
    # z : user
    if z == '':
        z = session['username']
    list_ngay_dt = [x + dt.timedelta(days=i) for i in range(int((y.date() - x.date()).total_seconds()/(24*3600)) + 1)]
    total_time = 0
    if len(list_ngay_dt) == 1:
        total_time = (y-x).total_seconds()
    elif len(list_ngay_dt) == 2:
        total_time += (str_to_dt(khung_gio(z,list_ngay_dt[0])[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt(khung_gio(z,list_ngay_dt[1])[0] + ' ' + d_to_str(list_ngay_dt[1]))).total_seconds()
    else:
        total_time += (str_to_dt(khung_gio(z,list_ngay_dt[0])[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt(khung_gio(z,list_ngay_dt[-1])[0] + ' ' + d_to_str(list_ngay_dt[-1]))).total_seconds()
        for r in list_ngay_dt[1:-1]:
            total_time += khung_gio(z,r)[3]*3600
    return total_time

# import pypyodbc
# def sql(query,var=''):
#     # connection = pypyodbc.connect('Driver={SQL Server};Server=10.62.24.123\SQL2008;Database=p;uid=phunq;pwd=aos159753')
#     connection = pypyodbc.connect('Driver={SQL Server};Server=10.62.24.161\SQLEXPRESS;Database=WEB_CONG_VIEC;uid=aos;pwd=aos159753')
#     cursor = connection.cursor()
#     cursor.execute(query,var)
#     if query.lower()[:6] == 'select':
#         x = cursor.fetchall()
#         cursor.close()
#         return x
#     else:
#         cursor.commit()
#         cursor.close()

def send_mail(to,cc,sub,body):
    outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    for r in outlook.Session.Accounts:
        if r.SmtpAddress == 'qtrr.AOS@techcombank.com.vn':
            mail._oleobj_.Invoke(*(64209,0,8,0,r))
    mail.To = to + '@techcombank.com.vn'
    mail.CC = cc
    mail.Subject = sub
    mail.HTMLBody = body
    # mail.Display()
    mail.Send()


def send_pass(x):
    new_pass = random.choice([i for i in range(100000,999999)])
    sql("update userr set password = ? where username = ?",[hash_user(str(new_pass)),x])
    send_mail(x,'','New Password','Your new password is {}'.format(new_pass))


def task_id_create():
    p = max([int(r.task_id) for r in db.session.query(ID_auto.task_id).all()])
    # p = sql("select max(convert(int,task_id)) from ID_auto_create")[0][0]
    p1 = str(int(p)+1)
    p2 = p1 + '.0'
    id_new = ID_auto(p1,p2)
    db.session.add(id_new)
    db.session.commit()
    # sql("insert into ID_auto_create(task_id,event_id) values(?,?)",[p1,p2])
    return p1


def event_id_create(x):
    ojb_id = db.session.query(ID_auto).filter_by(task_id = x).all()
    p = str(max([float(r.event_id) for r in ojb_id])).split('.')
    # p = sql("select max(convert(float,event_id)) from ID_auto_create where task_id=?",[x])[0][0].split('.')
    p1 = str(int(p[1])+1)
    p = p[0] + '.' + p1

    for r in ojb_id:
        r.event_id = p
        db.session.commit()
    # sql("update ID_auto_create set event_id=? where task_id=?",[p,x])
    return p


def insert(x1,y1,x2,y2):
    # 2 insert 1
    event_1 = sql("select * from event where event_id = ? and start_time = ?",[x1,y1])[0]
    event_2 = sql("select * from event where event_id = ? and start_time = ?",[x2,y2])[0]
    if str_to_dt(event_1[event_field.index('start_time')]) < str_to_dt(event_2[event_field.index('start_time')]) < str_to_dt(event_1[event_field.index('end_time')]) < str_to_dt(event_2[event_field.index('end_time')]) :
        sql("update event set end_time = ? where event_id = ? and end_time = ?",[event_2[event_field.index('start_time')],x1,event_1[event_field.index('end_time')]])
    if str_to_dt(event_2[event_field.index('start_time')]) < str_to_dt(event_1[event_field.index('start_time')]) < str_to_dt(event_2[event_field.index('end_time')]) < str_to_dt(event_1[event_field.index('end_time')]) :
        sql("update event set start_time = ? where event_id = ? and start_time = ?",[event_2[event_field.index('end_time')],x1,event_1[event_field.index('start_time')]])
    if str_to_dt(event_1[event_field.index('start_time')]) <= str_to_dt(event_2[event_field.index('start_time')]) < str_to_dt(event_2[event_field.index('end_time')]) <= str_to_dt(event_1[event_field.index('end_time')]) and (str_to_dt(event_1[event_field.index('start_time')]) != str_to_dt(event_2[event_field.index('start_time')]) or str_to_dt(event_2[event_field.index('end_time')]) != str_to_dt(event_1[event_field.index('end_time')])):
        sql("delete from event where event_id = ? and start_time = ?",[x1,event_1[event_field.index('start_time')]])
        new_event_1 = list(event_1)
        new_event_2 = list(event_1)
        new_event_1[event_field.index('start_time')] = event_1[event_field.index('start_time')]
        new_event_1[event_field.index('end_time')] = event_2[event_field.index('start_time')]
        new_event_2[event_field.index('start_time')] = event_2[event_field.index('end_time')]
        new_event_2[event_field.index('end_time')] = event_1[event_field.index('end_time')]
        if str_to_dt(event_1[event_field.index('start_time')]) == str_to_dt(event_2[event_field.index('start_time')]) and str_to_dt(event_2[event_field.index('end_time')]) != str_to_dt(event_1[event_field.index('end_time')]):
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_2)
        elif str_to_dt(event_1[event_field.index('start_time')]) != str_to_dt(event_2[event_field.index('start_time')]) and str_to_dt(event_2[event_field.index('end_time')]) == str_to_dt(event_1[event_field.index('end_time')]):
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_1)
        else:
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_1)
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_2)
    if str_to_dt(event_2[event_field.index('start_time')]) <= str_to_dt(event_1[event_field.index('start_time')]) < str_to_dt(event_1[event_field.index('end_time')]) <= str_to_dt(event_2[event_field.index('end_time')]) :
        sql("delete from event where event_id = ? and start_time = ?",[x1,event_1[event_field.index('start_time')]])
        if not sql("select * from event where task_id = ?",[x1.split('.')[0]]):
            sql("delete from task where task_id = ?",[x1.split('.')[0]])


def check_dup(x):
    event_x = sql("select * from event where event_id = ?",[x])
    all_event = sql("select * from event where event_id != ? and executer = ?",[x,event_x[0][event_field.index('executer')]])
    return [[r[event_field.index('event_id')],r[event_field.index('start_time')],r1[event_field.index('event_id')],r1[event_field.index('start_time')]] for r1 in all_event for r in event_x if (str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r1[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) or str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r1[event_field.index('end_time')]) < str_to_dt(r[event_field.index('end_time')]) or str_to_dt(r1[event_field.index('start_time')]) <= str_to_dt(r[event_field.index('start_time')]) <= str_to_dt(r[event_field.index('end_time')]) <= str_to_dt(r1[event_field.index('end_time')]))]


def insert_test(x='p'):
    sql("insert into t1 values (?)",[x])

list_ngay_nghi = [dt.date(2017,5,1),dt.date(2017,5,2),dt.date(2017,4,6),dt.date(2017,9,2),dt.date(2017,9,3),dt.date(2017,9,4),dt.date(2018,2,14),dt.date(2018,2,15),dt.date(2018,2,16),dt.date(2018,2,17),dt.date(2018,2,18),dt.date(2018,2,19),dt.date(2018,2,20)]

ds_user = [r1.username for r1 in db.session.query(Profile.username).all()] 
ds_user_mailname = [r1.mail_name for r1 in db.session.query(Profile.mail_name).all()]
ds_phong = [r1.phong for r1 in db.session.query(Profile.phong).distinct().all()]
ds_phong_bophan = [r1.phong + '|' + r1.bophan for r1 in db.session.query(Profile.phong, Profile.bophan).filter(Profile.bophan != '').distinct().all()]

def layout(x):
    list_assignee = db.session.query(
                                    Profile.username, 
                                    Profile.mail_name, 
                                    Profile.hash_1, 
                                    Profile.hash_2,
                                    Profile.hash_3) \
    .filter(or_(Profile.n_0 == x, Profile.n_1 == x, Profile.n_2 == x, Profile.n_3 == x, 
                Profile.n_0.like("%|{}".format(x)), Profile.n_0.like("%|{}|%".format(x)),
                Profile.n_0.like("{}|%".format(x)), Profile.n_1.like("%|{}".format(x)),
                Profile.n_1.like("%|{}|%".format(x)), Profile.n_1.like("{}|%".format(x)),
                Profile.n_2.like("%|{}".format(x)), Profile.n_2.like("%|{}|%".format(x)),
                Profile.n_2.like("{}|%".format(x)), Profile.n_3.like("%|{}".format(x)),
                Profile.n_3.like("%|{}|%".format(x)), Profile.n_3.like("{}|%".format(x)) 
            )) \
    .all()
    return list_assignee


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:   
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


# LOGIN
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    ds_all_user = db.session.query(Profile.username, Profile.mail_name, Profile.mail, Profile.hoten).all()
    return render_template('login.html', ds_all_user = ds_all_user)


# AUTHENTICATION
@app.route('/authentication', methods=['GET', 'POST'])
def authentication():
    username = request.args['username'].lower()
    password = hash_user(request.args['password'])
    if request.environ['REMOTE_ADDR'] in ['10.62.24.161','10.62.24.79', '127.0.0.1']:
        session['logged_in'] = True
        session['username'] = username.lower()
        result = u"authenticated"
        return jsonify({'result':result})

    if db.session.query(Userr).filter_by(username = username, password = password).all():
        session['logged_in'] = True
        session['username'] = username.lower()
        result = u"authenticated"
        return jsonify({'result':result})
        
    else:
        result = u"Mật khẩu sai. Hãy thử lại."
        return jsonify({'result':result})


#################################################
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    send_pass(request.args['forgot_password'])
    result = u"Mật khẩu mới đã được gửi về email của anh/chị. Nếu không nhận được mật khẩu, thử lại sau 1 phút"
    return jsonify({'result':result})


# INTRO
@app.route('/intro',methods=['GET', 'POST'])
@login_required
def intro():
    session.pop('executer', None)
    session.pop('executer_name', None)
    session.pop('start_time', None)
    session.pop('end_time', None)
    session.pop('time_select', None)
    session.pop('time_end_select', None)
    # Prepare
    task_myself_finish = db.session.query(Task.end_time).filter_by(executer = session['username'], percentage = '100%').all()

    task_myself_notfinish = db.session.query(Task.task_id, Task.name, Task.percentage, Task.end_time).filter_by(executer = session['username']).filter(Task.percentage != '100%').order_by(Task.name.asc()).all()
    # task_myself_finish = sql("select end_time from task where executer = ? and assigner = ? and percentage = '100%'",[session['username'],session['username']])

    # task_myself_notfinish = sql("select task_id,name,percentage,end_time from task where executer = ? and assigner = ? and percentage != '100%' order by name",[session['username'],session['username']])

    task_myself_finish = [r for r in task_myself_finish if str_to_dt(r.end_time) <= dt.datetime.now()]
    task_myself_notfinish = [r for r in task_myself_notfinish if str_to_dt(r.end_time) <= dt.datetime.now()]

    # task_assigned = [r for r in task_assigned if str_to_dt(r[task_field.index('end_time')]) <= dt.datetime.now()]
    if request.form.get('go_task'):
        session['task_id'] = request.form.get('go_task')
        return redirect(url_for('viewtask'))
    last_time = ''
    last_user = ''
    
    return render_template('intro.html',task_myself_finish=task_myself_finish, task_myself_notfinish=task_myself_notfinish)


# STATION
@app.route('/_station')
def station():
    # session['department'],session['mail_name'] = sql("select phong,mail_name from profile where username = ?",[session['username']])[0]
    session['department'],session['mail_name'] = db.session.query(Profile.phong, Profile.mail_name).filter_by(username = session['username']).all()[0]

    session['day_selected'] = dt.datetime.now()

    session['type_department'] = db.session.query(Department.type_department, Department.type_, Department.type_strategy).filter_by(department = session['department']).all()
    # session['type_department'] = sql("select type_department,type,type_strategy from department where department = ?",[session['department']])
    return redirect(url_for('intro'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# MY JOB
@app.route('/myjob',methods=['GET', 'POST'])
@login_required
def nam():
    # Prepare
    ds_gio = ['07:00', '07:15', '07:30', '07:45', '08:00', '08:15', '08:30', '08:45', '09:00', '09:15', '09:30', '09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30', '11:45', '12:00', '12:15', '12:30', '12:45', '13:00', '13:15', '13:30', '13:45', '14:00', '14:15', '14:30', '14:45', '15:00', '15:15', '15:30', '15:45', '16:00', '16:15', '16:30', '16:45', '17:00', '17:15', '17:30', '17:45', '18:00', '18:15', '18:30', '18:45', '19:00', '19:15', '19:30', '19:45', '20:00', '20:15', '20:30', '20:45', '21:00']
    ds_index = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55, 58, 61, 64, 67, 70, 73, 76, 79, 82, 85, 88, 91, 94, 97, 100, 103, 106, 109, 112, 115, 118, 121, 124, 127, 130, 133, 136, 139, 142, 145, 148, 151, 154, 157, 160, 163, 166, 169]
    list_moc_thoi_gian = ['07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']

    # content_base = sql("select * from event where executer = ? and start_time like {}".format("'%"+d_to_str(session['day_selected'])+"'"),[session['username']])
    content_base = db.session.query(Event).filter_by(executer = session['username']).filter(Event.start_time.like("%{}%".format(d_to_str(session['day_selected'])))).all()

    block_base = [[ds_index[ds_gio.index(r.start_time[:5])],ds_index[ds_gio.index(r.end_time[:5])]] for r in content_base]

    old_task = db.session.query(Task.task_id, Task.name, Task.percentage).filter_by(executer = session['username']).filter(Task.percentage != '100%').all()
    # old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])

    day_selected = session['day_selected']
    day_now = dt.datetime.now()

    list_type_department = [r[0] for r in session['type_department']]

    if not content_base:
        content_base = []
        block_base = []
    else:
        content_base = [content_base]
        block_base = [block_base]
    if request.form.get('tracking'):
        session['task_id'] = request.form.get('tracking')
        return redirect(url_for('viewtask'))
    # Function
    if request.form.get('select_day'):
        session['day_selected'] = dt.datetime.strptime(request.form.get('select_day'),'%d/%m/%Y')
        return redirect(url_for('nam'))


    # content_val_input = [[i.task_id, i.event_id, i.name, i.type, i.type_strategy, i.content, i.status, i.percentage, i.executer, i.executer_name, i.start_time, i.end_time, i.complete, i.department, i.type_department, i.border_color] for i in [x for x in [r for r in content_base]]]
    # content_val_input = []
    # for r in content_base:
    #     for i in r:
    #         # for i in x:
    #         content_val_input.append([i.task_id, i.event_id, i.name, i.type, i.type_strategy, i.content, i.status, i.percentage, i.executer, i.executer_name, i.start_time, i.end_time, i.complete, i.department, i.type_department, i.border_color])

    content_val_input = [[[i.task_id, i.event_id, i.name, i.type, i.type_strategy, i.content, i.status, i.percentage, i.executer, i.executer_name, i.start_time, i.end_time, i.complete, i.department, i.type_department, i.border_color] for r in content_base for i in r]]


    return render_template('adminday/nam.html',block_base = block_base, content_base = content_base,list_moc_thoi_gian = list_moc_thoi_gian, day_selected = day_selected, day_now = day_now, list_type_department = list_type_department,old_task = old_task, content_val_input = content_val_input)












list_day_off = [dt.date(2017,5,1),dt.date(2017,5,2),dt.date(2017,4,6),dt.date(2017,9,2),dt.date(2017,9,3),dt.date(2017,9,4)]

# list_mail_name = [r1[0] for r1 in sql("select mail_name from profile")]
list_mail_name = [r.mail_name for r in db.session.query(Profile.mail_name).all()]

# list_department = [r1[0] for r1 in sql("select distinct phong from profile")]
# list_department = [r.phong for r in db.session.query(Profile.phong).distinct().all()]

list_department_section = [r.phong + '|' + r.bophan for r in db.session.query(Profile.phong, Profile.bophan).filter(Profile.bophan != '').all()]
# list_department_section = [r1[0] + '|' + r1[1] for r1 in sql("select distinct phong,bophan from profile where bophan != ''")]
required_field = ['task_id','event_id','executer','department','type_department','start_time','end_time','type','type_strategy']
list_work_type_qtrr = ["Thẩm định,phê duyệt,phân luồng", "Vận hành Hội đồng, Ủy ban", "Giám sát,nhận diện, cảnh báo", "Cải tiến hệ thống, mô hình, quy trình", "Xây dựng kiểm soát Budget", "Xây dựng, quy định, chính sách, quy trình", "Mua bán, xử lý nợ", "Tư vấn,giải đáp", "Hành chính, văn phòng", "Phát triển nhân lực", "Tham gia dự án", "Báo cáo, dữ liệu", "Khác"]
list_work_type_tcb =["Vận hành", "Dữ liệu", "Nhân sự", "Quy trình, chính sách", "Văn hóa"]


#
def calculate(x,start_time,end_time):
    # print(x)
    if x in list_mail_name:        
        # Prepare
        # - user name and mail name
        mail_name = x
        username = db.session.query(Profile.username).filter_by(mail_name = x).all()[0].username

        # - department and work type
        department = db.session.query(Profile.phong).filter_by(username = username).all()[0].phong
        list_work_type_department = [r.type_department for r in db.session.query(Department.type_department).filter_by(department = department).order_by(Department.type_department.asc()).all()]

        # - config start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day off personal
        try:           
            list_day_off_personal = list_day_off + [str_to_dt(r.ngay_nghi).date() for r in db.session.query(Profile.ngay_nghi).filter_by(username = username)[0].ngay_nghi.split(',')]
        except:
            list_day_off_personal = list_day_off

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off_personal]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data       
        event_data = db.session.query(Event).filter_by(executer = username).all()
        # -- convert str to datetime, filter by time and add event duration
        for i,r in enumerate(event_data):
            r.start_time = str_to_dt(r.start_time)
            r.end_time = str_to_dt(r.end_time)

        event_data = [r for r in event_data if start_time <= r.start_time < end_time]
        for i,r in enumerate(event_data):
            r.work_time = (r.end_time - r.start_time).total_seconds()/3600

        
        # calculate index
        # - number of worked time
        worked_time = sum([r.work_time for r in event_data])

        # - number of executer
        number_executer = 1

        # - number of task
        number_task = len(set([r.task_id for r in event_data]))

        # - number of worked time group by day in range time
        worked_time_in_range = [sum([r.work_time for r in event_data if r.start_time.date() == r1]) for r1 in list_day_in_range]

        # - number of work day standard
        number_work_day = len([r for r in list_day_in_range if r.weekday() == 5])/2 + len([r for r in list_day_in_range if r.weekday() != 5])

        # - worked time percentage = worked time/number of work day standard/8
        if number_work_day:
            worked_time_per = str(round(worked_time/number_work_day/8*100,2)) + '%'
        else:
            worked_time_per = ''
        worked_time_per_user = [[mail_name,worked_time,number_work_day*8,worked_time_per]]

        # - distribute in work type
        if worked_time:
            distribute_department = [sum([r.work_time for r in [r1 for r1 in event_data if r1.type_department == r2]])*100/worked_time for r2 in list_work_type_department]

            distribute_qtrr = [sum([r.work_time/len(r.type.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type.split(';')]])*100/worked_time for r2 in list_work_type_qtrr]

            distribute_tcb = [sum([r.work_time/len(r.type_strategy.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type_strategy.split(';')]])*100/worked_time for r2 in list_work_type_tcb]

            # -- optimize list (remove object 0, round 1 and add up to 100%)
            distribute_department_op, list_work_type_department_op = list_optimize(distribute_department, list_work_type_department)
            distribute_qtrr_op, list_work_type_qtrr_op = list_optimize(distribute_qtrr, list_work_type_qtrr)
            distribute_tcb_op, list_work_type_tcb_op = list_optimize(distribute_tcb, list_work_type_tcb)
        else:
            distribute_department_op,distribute_qtrr_op,distribute_tcb_op = ['']*3
            list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op = list_work_type_department, list_work_type_qtrr, list_work_type_tcb

        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per, number_executer, worked_time_per_user] 

    elif x in list_department[1:]:
        # Prepare
        # - list user name active and mail name
        temp = db.session.query(Profile.username, Profile.mail_name).filter_by(phong = x).filter(Profile.status != 'disable').order_by(Profile.username.asc()).all()

        list_username_department = [r[0] for r in temp]
        list_mail_name_department = [r[1] for r in temp]

        # - work type department
        list_work_type_department = [r.type_department for r in db.session.query(Department.type_department).filter_by(department = x).order_by(Department.type_department.asc()).all()]

        # - start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = db.session.query(Event).filter_by(department = x).filter(Event.executer.in_(list_username_department)).all()
        # - convert str to datetime, filter by time and add event duration
        for i,r in enumerate(event_data):
            r.start_time = str_to_dt(r.start_time)
            r.end_time = str_to_dt(r.end_time)
        event_data = [r for r in event_data if start_time <= r.start_time < end_time]
        for i,r in enumerate(event_data):
            r.work_time = (r.end_time - r.start_time).total_seconds()/3600

        # calculate index
        # - number of worked time
        worked_time = sum([r.work_time for r in event_data])

        # - number of task
        number_task = len(set([r.task_id for r in event_data]))

        # - worked time percentage of department and per user
        worked_time_per_user = []

        for i,username in enumerate(list_username_department):
            try:
                list_day_off_personal = list_day_off + [str_to_dt(r.ngay_nghi).date() for r in db.session.query(Profile.ngay_nghi).filter_by(username = username)[0].ngay_nghi.split(',')]
            except:
                list_day_off_personal = list_day_off
            list_day_in_range_user = [r for r in list_day_in_range if r not in list_day_off_personal]

            worked_time_user = sum([r.work_time for r in event_data if r.executer == username])
            number_work_day = len([r for r in list_day_in_range_user if r.weekday() == 5])/2 + len([r for r in list_day_in_range_user if r.weekday() != 5])
            
            if number_work_day:
                worked_time_per = str(round(worked_time_user/number_work_day/8*100,2)) + '%'
            else:
                worked_time_per = ''
                
            worked_time_per_user.append([list_mail_name_department[i],worked_time_user,number_work_day*8,worked_time_per])
        sum_work_time_per_user = sum([r[2] for r in worked_time_per_user])
        if sum_work_time_per_user == 0:
            sum_work_time_per_user = 1
        worked_time_per_department = str(round(worked_time/sum_work_time_per_user*100,2)) + '%'

        # - number of executer
        number_executer = len(worked_time_per_user)
        if number_executer == 0:
            number_executer = 1
        # - number of work day
        number_work_day = round(sum_work_time_per_user/number_executer/8,2)

        # - number of worked time group by day in range time
        worked_time_in_range = [round(sum([r.work_time for r in event_data if r.start_time.date() == r1])/number_executer,2) for r1 in list_day_in_range]

        # - distribute in work type
        if worked_time:
            distribute_department = [sum([r.work_time for r in [r1 for r1 in event_data if r1.type_department == r2]])*100/worked_time for r2 in list_work_type_department]
            distribute_qtrr = [sum([r.work_time/len(r.type.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type.split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r.work_time/len(r.type_strategy.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type_strategy.split(';')]])*100/worked_time for r2 in list_work_type_tcb]
            # -- optimize list (remove object 0, round 2 and add up to 100%)
            distribute_department_op, list_work_type_department_op = list_optimize(distribute_department, list_work_type_department)
            distribute_qtrr_op, list_work_type_qtrr_op = list_optimize(distribute_qtrr, list_work_type_qtrr)
            distribute_tcb_op, list_work_type_tcb_op = list_optimize(distribute_tcb, list_work_type_tcb)
        else:
            distribute_department_op,distribute_qtrr_op,distribute_tcb_op = ['']*3
            list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op = list_work_type_department, list_work_type_qtrr, list_work_type_tcb

        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per_department, number_executer, worked_time_per_user]

    elif x in list_department_section:
        # Prepare
        # - list user name active and mail name
        temp = db.session.query(Profile.username, Profile.mail_name).filter_by(phong = x.split('|')[0], bophan = x.split('|')[1]).filter(Profile.status != 'disable').order_by(Profile.username.asc()).all()

        list_username_section = [r[0] for r in temp]
        list_mail_name_section = [r[1] for r in temp]

        # - work type department       
        list_work_type_department = [r.type_department for r in db.session.query(Department.type_department).filter_by(department = x.split('|')[0]).order_by(Department.type_department.asc()).all()]
        # - start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = db.session.query(Event).filter(Event.executer.in_(list_username_section)).all()
        
        # - convert str to datetime, filter by time and add event duration
        for r in event_data:
            r.start_time = str_to_dt(r.start_time)
            r.end_time = str_to_dt(r.end_time)
        event_data = [r for r in event_data if start_time <= r.start_time < end_time]
        for i,r in enumerate(event_data):
            r.work_time = (r.end_time - r.start_time).total_seconds()/3600

        # calculate index
        # - number of worked time
        worked_time = sum([r.work_time for r in event_data])

        # - number of task
        number_task = len(set([r.task_id for r in event_data]))

        # - worked time percentage section and per user
        worked_time_per_user = []
        for i,username in enumerate(list_username_section):
            try:
                list_day_off_personal = list_day_off + [str_to_dt(r.ngay_nghi).date() for r in db.session.query(Profile.ngay_nghi).filter_by(username = username)[0].ngay_nghi.split(',')]
            except:
                list_day_off_personal = list_day_off
            list_day_in_range_user = [r for r in list_day_in_range if r not in list_day_off_personal]

            worked_time_user = sum([r.work_time for r in event_data if r.executer == username])
            number_work_day = len([r for r in list_day_in_range_user if r.weekday() == 5])/2 + len([r for r in list_day_in_range_user if r.weekday() != 5])

            if number_work_day:
                worked_time_per = str(round(worked_time_user/number_work_day/8*100,2)) + '%'
            else:
                worked_time_per = ''
                
            worked_time_per_user.append([list_mail_name_section[i],worked_time_user,number_work_day*8,worked_time_per])
        sum_work_time_per_user = sum([r[2] for r in worked_time_per_user])
        worked_time_per_section = str(round(worked_time/sum_work_time_per_user*100,2)) + '%'

        # - number of executer
        number_executer = len(worked_time_per_user)

        # - number of work day
        number_work_day = round(sum_work_time_per_user/number_executer/8,2)

        # - number of worked time group by day in range time
        worked_time_in_range = [round(sum([r.work_time for r in event_data if r.start_time.date() == r1])/number_executer,2) for r1 in list_day_in_range]

        # - distribute in work type
        if worked_time:
            distribute_department = [sum([r.work_time for r in [r1 for r1 in event_data if r1.type_department == r2]])*100/worked_time for r2 in list_work_type_department]
            distribute_qtrr = [sum([r.work_time/len(r.type.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type.split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r.work_time/len(r.type_strategy.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type_strategy.split(';')]])*100/worked_time for r2 in list_work_type_tcb]
            # -- optimize list (remove object 0, round 2 and add up to 100%)
            distribute_department_op, list_work_type_department_op = list_optimize(distribute_department, list_work_type_department)
            distribute_qtrr_op, list_work_type_qtrr_op = list_optimize(distribute_qtrr, list_work_type_qtrr)
            distribute_tcb_op, list_work_type_tcb_op = list_optimize(distribute_tcb, list_work_type_tcb)
        else:
            distribute_department_op,distribute_qtrr_op,distribute_tcb_op = ['']*3
            list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op = list_work_type_department, list_work_type_qtrr, list_work_type_tcb

        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per_section, number_executer, worked_time_per_user]

    elif x == 'Khối QTRR': 
        # Prepare
        # - list user name active and mail name
        temp = db.session.query(Profile.username, Profile.mail_name).filter(Profile.status != 'disable').order_by(Profile.username.asc()).all()
        list_username_qtrr = [r[0] for r in temp]
        list_mail_name_qtrr = [r[1] for r in temp]

        # - start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = db.session.query(Event).all()
        
        # - convert str to datetime, filter by time and add event duration
        for r in event_data:
            r.start_time = str_to_dt(r.start_time)
            r.end_time = str_to_dt(r.end_time)
        event_data = [r for r in event_data if start_time <= r.start_time < end_time]
        for i,r in enumerate(event_data):
            r.work_time = (r.end_time - r.start_time).total_seconds()/3600

        # calculate index
        # - number of worked time
        worked_time = sum([r.work_time for r in event_data])

        # - number of task
        number_task = len(set([r.task_id for r in event_data]))

        # - worked time percentage and per user
        worked_time_per_user = []
        for i,username in enumerate(list_username_qtrr):
            try:
                list_day_off_personal = list_day_off + [str_to_dt(r.ngay_nghi).date() for r in db.session.query(Profile.ngay_nghi).filter_by(username = username)[0].ngay_nghi.split(',')]
            except:
                list_day_off_personal = list_day_off
            list_day_in_range_user = [r for r in list_day_in_range if r not in list_day_off_personal]
            
            worked_time_user = sum([r.work_time for r in event_data if r.executer == username])
            number_work_day = len([r for r in list_day_in_range_user if r.weekday() == 5])/2 + len([r for r in list_day_in_range_user if r.weekday() != 5])

            if number_work_day:
                worked_time_per = str(round(worked_time_user/number_work_day/8*100,2)) + '%'
            else:
                worked_time_per = ''
                
            worked_time_per_user.append([list_mail_name_qtrr[i],worked_time_user,number_work_day*8,worked_time_per])
        sum_work_time_per_user = sum([r[2] for r in worked_time_per_user])
        worked_time_per_qtrr = str(round(worked_time/sum_work_time_per_user*100,2)) + '%'

        # - number of executer
        number_executer = len(worked_time_per_user)

        # - number of work day
        number_work_day = round(sum_work_time_per_user/number_executer/8,2)

        # - number of worked time group by day in range time
        worked_time_in_range = [round(sum([r.work_time for r in event_data if r.start_time.date() == r1])/number_executer,2) for r1 in list_day_in_range]

        # - distribute in work type
        if worked_time:
            distribute_qtrr = [sum([r.work_time/len(r.type.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type.split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r.work_time/len(r.type_strategy.split(';')) for r in [r1 for r1 in event_data if r2 in r1.type_strategy.split(';')]])*100/worked_time for r2 in list_work_type_tcb]
            # -- optimize list (remove object 0, round 2 and add up to 100%)
            distribute_department_op, list_work_type_department_op = ('','')
            distribute_qtrr_op, list_work_type_qtrr_op = list_optimize(distribute_qtrr, list_work_type_qtrr)
            distribute_tcb_op, list_work_type_tcb_op = list_optimize(distribute_tcb, list_work_type_tcb)
        else:
            distribute_department_op,distribute_qtrr_op,distribute_tcb_op = ['']*3
            list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op = list_work_type_department, list_work_type_qtrr, list_work_type_tcb

        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per_qtrr, number_executer, worked_time_per_user]
    else:  
        pass



# REPORT
@app.route('/task_report',methods=['GET', 'POST'])
# @login_required
def task_report():
    session['username'] = 'badung.le'
    session['mail_name'] = 'DUNG QTRR. LE BA'
    list_assignee = layout(session['username'])

    ds_n_0 = [r1 for r in db.session.query(Profile.n_0).distinct().all() for r1 in r.n_0.split('|')]
    ds_n_1 = [r1 for r in db.session.query(Profile.n_1).distinct().all() for r1 in r.n_1.split('|')]
    ds_n_2 = [r1 for r in db.session.query(Profile.n_2).distinct().all() for r1 in r.n_2.split('|')]
    ds_n_3 = [r1 for r in db.session.query(Profile.n_3).distinct().all() for r1 in r.n_3.split('|')]

    phong = db.session.query(Profile.phong).filter_by(username = session['username']).all()[0]

    if phong.phong == 'Ban giám đốc':
        phong.phong = 'Khối QTRR'


    if session['username'] in ds_n_0:
        ds_filter = [session['mail_name']] + ['Khối QTRR'] + [r.phong_viettat for r in db.session.query(Profile.phong_viettat).filter(func.length(Profile.phong) > 3).distinct().all()] + ds_user_mailname

        list_assignee = db.session.query(
                                    Profile.username, 
                                    Profile.mail_name, 
                                    Profile.hash_1, 
                                    Profile.hash_2,
                                    Profile.hash_3) \
                        .filter(or_(Profile.n_0 == session['username'], Profile.n_1 == session['username'], Profile.n_2 == session['username'], Profile.n_3 == session['username'], 
                                    Profile.n_0.like("%|{}".format(session['username'])), Profile.n_0.like("%|{}|%".format(session['username'])),
                                    Profile.n_0.like("{}|%".format(session['username'])), Profile.n_1.like("%|{}".format(session['username'])),
                                    Profile.n_1.like("%|{}|%".format(session['username'])), Profile.n_1.like("{}|%".format(session['username'])),
                                    Profile.n_2.like("%|{}".format(session['username'])), Profile.n_2.like("%|{}|%".format(session['username'])),
                                    Profile.n_2.like("{}|%".format(session['username'])), Profile.n_3.like("%|{}".format(session['username'])),
                                    Profile.n_3.like("%|{}|%".format(session['username'])), Profile.n_3.like("{}|%".format(session['username'])) 
                                )) \
                        .all()

    elif session['username'] in ds_n_1:
        ds_filter = [session['mail_name']] + [r.phong_viettat for r in db.session.query(Profile.phong_viettat).filter(or_(
                Profile.n_1 == session['username'],
                Profile.n_1.like("%|{}|%".format(session['username'])),
                Profile.n_1.like("{}|%".format(session['username'])),
                Profile.n_1.like("%|{}".format(session['username'])) 
            )).distinct().all()] + [r.phong_viettat + '|' + r.bophan for r in db.session.query(Profile.phong_viettat, Profile.bophan).filter(or_(
                Profile.n_1 == session['username'],
                Profile.n_1.like("%|{}|%".format(session['username'])),
                Profile.n_1.like("{}|%".format(session['username'])),
                Profile.n_1.like("%|{}".format(session['username']))
            )).distinct().all()] + [r.mail_name for r in db.session.query(Profile.mail_name).filter(or_(
                Profile.n_1 == session['username'],
                Profile.n_1.like("%|{}|%".format(session['username'])),
                Profile.n_1.like("{}|%".format(session['username'])),
                Profile.n_1.like("%|{}".format(session['username']))
                )).distinct().all()] 

    elif session['username'] in ds_n_2:
        ds_filter = [session['mail_name']] + [r.phong_viettat + '|' + r.bophan for r in db.session.query(Profile.phong_viettat, Profile.bophan).filter(
                Profile.n_2 == session['username']               
            ).distinct().all()] + [r.mail_name for r in db.session.query(Profile.mail_name).filter(
                Profile.n_2 == session['username']               
            ).distinct().all()] 

    elif session['username'] in ds_n_3:
        # ds_filter = [session['mail_name']] + [r[0] for r in sql("select distinct mail_name from profile where n_3 = ?",[session['username']])]

        ds_filter = [session['mail_name']] + [r.mail_name for r in db.session.query(Profile.mail_name).filter(
                Profile.n_3 == session['username']  
            ).distinct().all()] 

    else:
        ds_filter = [session['mail_name']]

    if request.form.get('submit_filter'):
        if "|" in request.form.get('filter_trungtam'):
            filter_value = list_department[list_department_viettat.index(request.form.get('filter_trungtam').split("|")[0])]+"|"+ request.form.get('filter_trungtam').split("|")[1]         
        elif "QTRR." in request.form.get('filter_trungtam'):
            filter_value = request.form.get('filter_trungtam')            
        else:
            filter_value = list_department[list_department_viettat.index(request.form.get('filter_trungtam'))]

        start_time_str = str(request.form.get('start_time'))
        if start_time_str:
            start_time = str_to_dt('{}/{}/{}'.format(start_time_str[-2:],start_time_str[5:7],start_time_str[:4]))
        else:
            start_time = ''
        end_time_str = str(request.form.get('end_time'))
        if end_time_str:
            end_time = str_to_dt('{}/{}/{}'.format(end_time_str[-2:],end_time_str[5:7],end_time_str[:4]))
        else:
            end_time = ''

        print(filter_value)
        # print(calculate('Khối QTRR',start_time,end_time))
        so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user = calculate(filter_value,start_time,end_time)


        filter_trungtam = request.form.get('filter_trungtam')



        return render_template('adminday/task_report.html',so_gio_lam_viec = so_gio_lam_viec,so_cong_viec = so_cong_viec,ds_10_ngay_gan_nhat = ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay = ds_cong_viec_trong_10_ngay,so_ngay_lam_viec = so_ngay_lam_viec,phan_bo_cv_theo_trung_tam = phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty = phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam = ds_cv_theo_trung_tam,ds_cv_theo_cong_ty = ds_cv_theo_cong_ty,ds_cv_theo_toan_hang = ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao = ty_le_tuan_thu_bao_cao,ds_filter = ds_filter,start_time_str=start_time_str,end_time_str=end_time_str,filter_trungtam=filter_trungtam,filter_value=filter_value,so_nguoi_thuc_hien=so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user=ty_le_tuan_thu_bao_cao_theo_user)

    start_time_str = '2018-03-01'
    if start_time_str:
        start_time = str_to_dt('{}/{}/{}'.format(start_time_str[-2:],start_time_str[5:7],start_time_str[:4]))
    else:
        start_time = ''
    end_time_str = '2018-03-31'
    if end_time_str:
        end_time = str_to_dt('{}/{}/{}'.format(end_time_str[-2:],end_time_str[5:7],end_time_str[:4]))
    else:
        end_time = ''

    # print(calculate(session['mail_name'],start_time,end_time))

    so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user = calculate(session['mail_name'],start_time,end_time)

    filter_trungtam = session['mail_name']


    return render_template('adminday/task_report.html',so_gio_lam_viec = so_gio_lam_viec,so_cong_viec = so_cong_viec,ds_10_ngay_gan_nhat = ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay = ds_cong_viec_trong_10_ngay,so_ngay_lam_viec = so_ngay_lam_viec,phan_bo_cv_theo_trung_tam = phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty = phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam = ds_cv_theo_trung_tam,ds_cv_theo_cong_ty = ds_cv_theo_cong_ty,ds_cv_theo_toan_hang = ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao = ty_le_tuan_thu_bao_cao,ds_filter = ds_filter,list_assignee=list_assignee,start_time_str=start_time_str,end_time_str=end_time_str,filter_trungtam=filter_trungtam,ds_n_0=ds_n_0,ds_n_1=ds_n_1,ds_n_2=ds_n_2,so_nguoi_thuc_hien=so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user=ty_le_tuan_thu_bao_cao_theo_user)


# MANAGE DEPARTMENT
@app.route('/department',methods=['GET', 'POST'])
@login_required
def department():
    list_admin_department = [r[0] for r in sql("select * from admin_department")]
    if session['username'] not in list_admin_department:
        return redirect(url_for('nam'))
    list_job_type_department = sql("select type_department,type,type_strategy from department where department = ?",[session["department"]])
    list_user_in_department = sql("select username,hoten,mail_name,n_1,n_2,n_3,status from profile where phong = ? order by username",[session["department"]])
    if session['department'] in ['Chính sách nhận diện và giảm thiểu rủi ro tín dụng cá nhân và tài trợ tiêu dùng', 'QTRR tín dụng cá nhân và tài trợ tiêu dùng']:
        list_user_name = ['','badung.le'] + [r[0] for r in list_user_in_department]
    else:
        list_user_name = [''] + [r[0] for r in list_user_in_department]
    if request.form.get('submit_job_type'):
        sql("delete from department where department = ?",[session['department']])
        for i in range(int(request.form.get('len_row'))):
            sql("insert into department ({}) values ({})".format(','.join(department_field),','.join(['?']*len(department_field))),[session["department"],request.form.get('type_department_'+str(i)),';'.join(request.form.getlist('type_'+str(i))),';'.join(request.form.getlist('type_strategy_'+str(i)))])
        return redirect(url_for('department'))


    if request.form.get('submit_user'):
        list_get_data = [[request.form.get('pp_username_'+str(i)),request.form.get('pp_fullname_'+str(i)),request.form.get('pp_mail_'+str(i)),request.form.get('assigner1_'+str(i)),request.form.get('assigner2_'+str(i)),request.form.get('assigner3_'+str(i)),request.form.get('status_'+str(i))] for i in range(int(request.form.get('len_row_user')))]
        for r in list_get_data:
            if r[0] not in [r1[0] for r1 in list_user_in_department]:
                sql("insert into userr(username,password) values(?,?)",[r[0],hash_user('555656164899633')])
                sql("insert into profile(username,hoten,time_begin,mail_name,n_1,n_2,n_3,phong,hash_1,hash_2,hash_3,n_0,name_n_0,status) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",[r[0],r[1],d_to_str(dt.datetime.now().date()),r[2],r[3],r[4],r[5],session['department'],hash_user(r[0]),hash_2(r[0]),hash_3(r[0]),'badung.le;tuongnq;kenneth','Dung QTRR. Le Ba;Tuong QTRR. Nguyen Quang;Kenneth QTRR. Keeslir',r[-1]])
                if [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[3]]:
                    name_n_1 = [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[3]][0]
                else:
                    name_n_1 = ''
                if [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[4]]:
                    name_n_2 = [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[4]][0]
                else:
                    name_n_2 = ''
                if [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[5]]:
                    name_n_3 = [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[5]][0]
                else:
                    name_n_3 = ''
                sql("update profile set name_n_1=?,name_n_2=?,name_n_3=?,status=? where username = ?",[name_n_1,name_n_2,name_n_3,r[-1],r[0]])
                sql("insert into setting_log values(?,?,?,?,?)",[r[0],'08:00','19:00','30','01/04/2017'])
            if r[0] in [r1[0] for r1 in list_user_in_department]:
                sql("update profile set hoten = ?,mail_name = ?,n_1 = ?,n_2 = ?,n_3 = ?,status = ? where username = ?",[r[1],r[2],r[3],r[4],r[5],r[-1],r[0]])
                if [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[3]]:
                    name_n_1 = [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[3]][0]
                else:
                    name_n_1 = ''
                if [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[4]]:
                    name_n_2 = [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[4]][0]
                else:
                    name_n_2 = ''
                if [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[5]]:
                    name_n_3 = [r1[1] for r1 in sql("select username,mail_name from profile where phong = ?",[session["department"]]) if r1[0] == r[5]][0]
                else:
                    name_n_3 = ''
                sql("update profile set name_n_1=?,name_n_2=?,name_n_3=?,status = ? where username = ?",[name_n_1,name_n_2,name_n_3,r[-1],r[0]])
        for r in list_user_in_department:
            if r[0] not in [r1[0] for r1 in list_get_data]:
                sql("delete from profile where username = ?",[r[0]])
                sql("delete from userr where username = ?",[r[0]])
        return redirect(url_for('department'))
    return render_template('department.html',list_job_type_department=list_job_type_department,list_type=list_type,list_type_strategy=list_type_strategy,list_user_in_department=list_user_in_department,list_user_name=list_user_name)             

             
# SEARCH PROFILE
@app.route('/searchprofile',methods=['GET', 'POST'])
@login_required
def searchprofile():
    b = db.session.query(Profile.hoten).all()

    list_phong = db.session.query(Profile.phong).filter(func.length(Profile.phong) > 3).distinct().all()

    u = [('','','','','','','','','','','','')]
    user = ''
    manv = ''
    donvi = ''
    if request.method == 'POST':
        user = request.form['hoten']
        manv = request.form['maNV']
        donvi = request.form['donvi']
        if user =='' and manv !='' and donvi !='':
            u = db.session.query(Profile).filter_by(maNV = manv, phong = donvi).all()                          
        elif user =='' and donvi =='' and manv !='':
            u = db.session.query(Profile).filter_by(maNV = manv).all()            
        elif user =='' and manv =='' and donvi != '':
            u = db.session.query(Profile).filter_by(phong = donvi).all()            
        elif manv =='' and user !='' and donvi !='':
            u = db.session.query(Profile).filter_by(hoten = user, phong = donvi).all()                          
        elif manv =='' and donvi =='' and user !='':            
            u = db.session.query(Profile).filter_by(hoten = user).all()
        elif donvi =='' and user !='' and manv != '':            
            u = db.session.query(Profile).filter_by(maNV = manv, hoten = user).all()          
        if not u:
            u = [('','','','','','','','','','','','')]
        return render_template(
        'profile/searchprofile.html',
        title=u'Thông tin cá nhân',u=u,user=user,b=b,list_phong=list_phong)      
    return render_template(
        'profile/searchprofile.html',
        title=u'Thông tin cá nhân',u=u,user=user,b=b,list_phong=list_phong)


# VIEW TASK DETAIL
@app.route('/viewtask',methods=['GET', 'POST'])
@login_required
def viewtask():
    session.pop('executer', None)
    session.pop('executer_name', None)
    session.pop('start_time', None)
    session.pop('end_time', None)
    session.pop('time_select', None)
    session.pop('time_end_select', None)
    # Get data

    task_content = db.session.query(Task).filter_by(task_id = session['task_id']).all()[0]
    # task_content = sql("select * from task where task_id = ?",[session['task_id']])[0]

    # event_content = [list(r) for r in sql("select * from event where task_id = ?",[session['task_id']])]
    event_content = db.session.query(Event).filter_by(task_id = session['task_id']).all()


    list_stt = list(set([int(r.event_id.split('.')[1]) for r in event_content]))

    # print(list_stt)
    list_stt.sort()

    for r in event_content:
        # r.append(list_stt.index(int(r[1].split('.')[1])) + 1)
        r.stt = list_stt.index(int(r.event_id.split('.')[1])) + 1

    event_content = sorted(event_content, key=lambda x: int(x.stt),reverse = True)
    # event_content.order_by(Event.stt.desc())

    if request.form.get('go_to_date'): 
        session['day_selected'] = dt.datetime.strptime(request.form.get('go_to_date'),'%d/%m/%Y')
        return redirect(url_for('nam'))
    if len(event_content) == 0:
        assessment_1 = u'Chưa có báo cáo cho công việc này'
    else:
        assessment_1 = u'Có {} báo cáo cho công việc này'.format(max(list_stt))

    if str_to_dt(task_content.end_time) < dt.datetime.now():
        assessment_2 = u'Đã quá hạn {} ngày đối với công việc này'.format(round((dt.datetime.now() -  str_to_dt(task_content.end_time)).total_seconds()/(24*3600),2))
    else:
        assessment_2 = u'Còn lại {} ngày đối với công việc này'.format(round((str_to_dt(task_content.end_time) - dt.datetime.now()).total_seconds()/(24*3600),2))

    if request.form.get('go_task'):
        session['day_selected'] = str_to_dt(request.form.get('go_task'))
        return redirect(url_for('nam'))

    day_now = dt.datetime.now()    
    return render_template('task/viewtask.html',task_content=task_content,event_content = event_content,assessment_1=assessment_1,assessment_2=assessment_2,day_now=day_now)


# EDIT PROFILE
@app.route('/editprofile',methods=['GET', 'POST'])
def editprofile():
    user = session['username']
    # profile_user = sql("select * from profile where username = ?",[user])
    profile_user = db.session.query(Profile).filter_by(username = user).all()[0]
    if request.method == 'POST':
        ngaysinh = request.form['ngaysinh']
        CMND = request.form['CMND']
        phone = request.form['phone']
        mobile = request.form['mobile']
        diachi = request.form['diaChi']        

        # sql("""update Profile set ngaysinh=(?),CMND=(?),phone=(?),mobile=(?),diachi=(?) where username=(?)""",(ngaysinh,CMND,phone,mobile,diachi,user,))
        profile_user.ngaysinh = ngaysinh
        profile_user.CMND = CMND
        profile_user.phone = phone
        profile_user.mobile = mobile
        profile_user.diachi = diachi
        db.session.commit()

        return redirect(url_for('test'))
    return render_template(
                'profile/editprofile.html',
                title=u'Thông tin cá nhân',user=user,profile_user=profile_user)

# TUTORIAL
@app.route('/tutorial',methods=['GET', 'POST'])
@login_required
def tutorial():
    return render_template('adminday/tutorial.html')


# ERROR
@app.route('/error')
def error():
    return render_template('error.html')


########################
#### BO SESSION KHI MOI VAO CHO NHANH
### SET SESSION KHI MOI VAO THI SUA APP.ROUTE 
### list_event_2 <--> list_event
@app.route('/list_event_2')
def station_2():
    session["end_time"] = dt_to_str_nguoc(dt.datetime.now())[:10]
    session["start_time"] = dt_to_str_nguoc(dt.datetime.now()-timedelta(days=7))[:10]
    session['time_end_select'] = dt.datetime.today().strftime('%Y-%m-%d')
    session['time_select'] = (dt.datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')
    return redirect(url_for('list_event'))


#  LIST EVENT
@app.route('/list_event',methods=['GET', 'POST'])
@login_required
def list_event():
    list_assignee = layout(session['username'])
    report_content_field = ['executer','executer_name','name','type_department','type_strategy','content','percentage','start_time','end_time','task_id']
    if len(list_assignee) == 0:
        return redirect(url_for("intro"))
    list_content = ''

    if "executer" in session and "start_time" in session and "end_time" in session:
        start_time_dt = str_to_dt(session['start_time'])
        end_time_dt = str_to_dt(session['end_time'])
        # list_content = sql("""select {} from event where executer = ?""".format(",".join(report_content_field)),[session["executer"]])
        list_content = db.session.query(Event).filter_by(executer = session["executer"]).all()


        list_content = [r for r in list_content if start_time_dt <= str_to_dt(r.start_time) < end_time_dt + dt.timedelta(days=1)]

    else:
        if "executer" in session and "start_time" not in session and "end_time" not in session:
            # list_content = sql("""select {} from event where executer = ?""".format(",".join(report_content_field)),[session["executer"]])
            list_content = db.session.query(Event).filter_by(executer = session["executer"]).all()

        if "executer" not in session and "start_time" in session and "end_time" in session:

            list_content = db.session.query(Event).filter(Event.executer.in_([r[0] for r in list_assignee])).all()

            # list_content = sql("select {} from event where executer in ({})".format(",".join(report_content_field),",".join(['?']*len(list_assignee))),[r[0] for r in list_assignee])


            list_content = [r for r in list_content if str_to_dt(session['start_time']) <= str_to_dt(r.start_time) and str_to_dt(session['end_time']) + dt.timedelta(days=1)>= str_to_dt(r.end_time)]


    if request.form.get("view_content"):
        if request.form.get("executer"):
            session["executer_name"] = request.form.get("executer")
            try:
                session["executer"] = [r[0] for r in list_assignee if r[1] == request.form.get("executer")][0]
            except:
                pass
        else:
            session.pop('executer', None)
            session.pop('executer_name', None)
        try:
            int(session["executer"])
            session['task_id'] = session["executer"]
            return redirect(url_for('viewtask'))
        except:
            pass
        if request.form.get("start_time") != '':
            session["time_select"] = request.form.get("start_time")
            session["time_end_select"] = request.form.get("end_time")
            convert_date = request.form.get("start_time").split("-")
            convert_date_end = request.form.get("end_time").split("-")

            session["start_time"] = convert_date[2]+"/"+convert_date[1]+"/"+convert_date[0]
            session["end_time"] = convert_date_end[2]+"/"+convert_date_end[1]+"/"+convert_date_end[0]
            # session["start_time"] = request.form.get("start_time")
        else:
            session.pop('start_time', None)
            session.pop('end_time', None)
            session.pop('time_select', None)
            session.pop('time_end_select', None)
        return redirect(url_for("list_event"))

    if request.form.get("go_viewtask"):
        session['task_id'] = request.form.get("go_viewtask")
        return redirect(url_for("viewtask"))
    return render_template('list_event.html',list_assignee=list_assignee,list_content=list_content)  


# PROFILE
@app.route('/profile',methods=['GET', 'POST'])
def test():
    user = session['username']
    # profile_user = db.session.query(Profile).filter_by(username = user).all()[0]
    u = db.session.query(Profile).filter_by(username = user).all()[0]
    return render_template('test.html',title= 'Thông tin cá nhân',u=u,user=user)


# CHANGE PASS
@app.route('/changepass',methods=['GET', 'POST'])
@login_required
def changepass():

    if request.method == "POST":
        pwd = request.form.get('pwd')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        pwd_user = db.session.query(Userr).filter_by(username = session['username']).all()[0]


        pwd_user.password = hash_user(pwd1)
        db.session.commit()
        # sql('update userr set password = ? where username = ?',[hash_user(pwd1),session['username']])
        return redirect(url_for('test'))
    return render_template(
        'profile/changepass.html')


# ADD NEW TASK
@app.route('/ajax_add_new_task', methods=['POST'])
def ajax_add_new_task():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])
    new_id = task_id_create()
    name = request.form['Task_name_rp']
    type_department = request.form['type_department']
    job_type = [r[1] for r in session['type_department'] if r[0] == type_department][0]
    type_strategy = [r[2] for r in session['type_department'] if r[0] == type_department][0]
    content = request.form['Description_rp']
    status = 'In progress'
    percentage = request.form['Percentage']
    border_color = '#901e1d'
    executer = assigner = session['username']
    executer_name = assigner_name = session['mail_name']

    start = index_to_time(request.form['time_start'])
    last_update = end = index_to_time(request.form['time_end'])

    rating = ''
    complete = percentage
    supporter,supporter_name, customer, disable = ['']*4
    # Insert task
    new_task = Task(new_id, name, job_type,type_strategy, content, status, percentage, executer, executer_name, start,end, last_update, session['department'], type_department, border_color)
    db.session.add(new_task)
    db.session.commit()
    # sql("insert into task({}) values({})".format(','.join(task_field),','.join(['?']*len(task_field))),[new_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter, executer_name, assigner_name,supporter_name, customer, disable, start,end,last_update,rating,session['department'],type_department,border_color])

    # Insert event
    event_id = event_id_create(new_id)
    new_event = Event(new_id, event_id, name, job_type, type_strategy, content, status, percentage, executer, executer_name, start, end, complete, session['department'], type_department, border_color)
    db.session.add(new_event)
    db.session.commit()
    # sql("insert into event({}) values({})".format(','.join(event_field),','.join(['?']*len(event_field))),[new_id, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter, executer_name, assigner_name,supporter_name, customer, disable, start,end,complete,session['department'],type_department,border_color])
    # Insert event_log
    new_log = Event_log(new_id, event_id, 'B', session['username'], dt_to_str(dt.datetime.now()), 'new task')    
    db.session.add(new_log)
    db.session.commit()

    # sql("insert into event_log values(?,?,?,?,?,?)",[new_id,event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'new task'])
    # Update block_base, content_base, old_task
    if block_base:
        block_base = [block_base[0] + [[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [content_base[0] + [[new_id, event_id, name, job_type, type_strategy, content, status, percentage, executer, executer_name, start,end,complete,session['department'],type_department,border_color]]]
    else:
        block_base = [[[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [[[new_id, event_id, name, job_type, type_strategy, content, status, percentage, executer,  executer_name, start, end, complete, session['department'], type_department, border_color]]]

    # Other var
    old_task = db.session.query(Task.task_id, Task.name, Task.percentage).filter_by(executer = session['username']).filter(Task.percentage != '100%').all()
    # old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])
    list_type_department = [r[0] for r in session['type_department']]

    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,list_type_department=list_type_department,old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})


# DEL EVENT
@app.route('/ajax_del_event', methods=['POST'])
def ajax_del_event():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])

    db.session.query(Event).filter_by(event_id = request.form['delete_event']).delete()
    db.session.commit()
    # sql("delete from event where event_id = ? ",[request.form['delete_event']])
    # Update Task and Event
    check_event = db.session.query(Event.event_id, Event.percentage).filter_by(task_id = request.form['delete_event'].split('.')[0]).all()
    if check_event:
        list_event = [int(r.event_id.split('.')[1]) for r in check_event]
        last_event = check_event[list_event.index(max(list_event))]
    else:
        db.session.query(Task).filter_by(task_id = request.form['delete_event'].split('.')[0]).first().percentage = ''
        db.session.commit()

    # if sql("select event_id, percentage from event where task_id = ?",[request.form['delete_event'].split('.')[0]]):
    #     list_event = [int(r[0].split('.')[1]) for r in sql("select event_id, percentage from event where task_id = ?",[request.form['delete_event'].split('.')[0]])]
    #     last_event = sql("select event_id, percentage from event where task_id = ?",[request.form['delete_event'].split('.')[0]])[list_event.index(max(list_event))]
    #     sql("update task set percentage = ? where task_id = ? ",[last_event[1],last_event[0].split('.')[0]])
    #     sql("update event set complete = ? where task_id = ? ",[last_event[1],last_event[0].split('.')[0]])
    # else:
    #     sql("update task set percentage = ? where task_id = ? ",['',request.form['delete_event'].split('.')[0]])

    new_log = Event_log('',request.form['delete_event'],'B',session['username'],dt_to_str(dt.datetime.now()),'delete event')    
    db.session.add(new_log)
    db.session.commit()


    # sql("insert into event_log values(?,?,?,?,?,?)",['',request.form['delete_event'],'B',session['username'],dt_to_str(dt.datetime.now()),'delete event'])
    if not check_event:
        db.session.query(Task).filter_by(task_id = request.form['delete_event'].split('.')[0]).delete()
        db.session.commit()
        # sql("delete from task where task_id=?",[request.form['delete_event'].split('.')[0]])

    block_base = [[r for i,r in enumerate(block_base[0]) if content_base[0][i][1] != request.form['delete_event']]]
    content_base = [[r for r in content_base[0] if r[1] != request.form['delete_event']]]

    old_task = db.session.query(Task.task_id, Task.name, Task.percentage).filter_by(executer = session['username']).filter(Task.percentage != '100%').all()
    list_type_department = [r[0] for r in session['type_department']]
    work_hour = 14
    if block_base == [[]]:
        block_base = []
        content_base = []
    else:
        pass

    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,
        list_type_department=list_type_department, work_hour=work_hour, old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})


# EDIT EVENT
@app.route('/ajax_edit_event', methods=['POST'])
def ajax_edit_event():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])

    old_event_id = request.form['edit_event']
    old_id = old_event_id.split('.')[0]
    name_edit = request.form['Task_name']
    type_department = request.form['type_department']
    job_type = [r[1] for r in session['type_department'] if r[0] == type_department][0]
    type_strategy = [r[2] for r in session['type_department'] if r[0] == type_department][0]
    content = request.form['Content']
    status = ''
    percentage = request.form['Percentage']
    executer_name = session['mail_name']
    # border_color = request.form.get('get_color_value' + old_event_id)

    # Update Event
    event_update = db.session.query(Event).filter_by(event_id = old_event_id).all()[0]
    event_update.name  = name_edit
    event_update.content  = content
    event_update.type_department  = type_department
    event_update.percentage  = percentage
    db.session.commit()

    # sql("update event set name=?,content = ?,type_department=?,percentage  = ? where event_id = ?",[ name_edit,content,type_department,percentage,old_event_id])

    # Update Task and Event
    task_update = db.session.query(Task).filter_by(task_id = old_id).all()[0]
    task_update.percentage = percentage
    task_update.type_department = type_department
    task_update.type = job_type
    task_update.type_strategy = type_strategy
    db.session.commit()

    # sql("update task set percentage = ?,type_department = ?, type = ?, type_strategy = ? where task_id = ?",[percentage,type_department, job_type, type_strategy,old_id])
    event_percent_update = db.session.query(Event).filter_by(task_id = old_id).update({Event.complete : percentage, Event.type_department : type_department, Event.type : job_type, Event.type_strategy : type_strategy})
    db.session.commit()

    # sql("update event set complete = ?,type_department = ?, type = ?, type_strategy = ? where task_id = ?",[sql("select percentage from task where task_id = ?",[old_id])[0][0],type_department, job_type, type_strategy,old_id])

    new_log = Event_log(old_id,old_event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'edit task')    
    db.session.add(new_log)
    db.session.commit()

    # sql("insert into event_log values(?,?,?,?,?,?)",[old_id,old_event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'edit task'])

    content_base = [[list(r) for r in content_base[0]]]
    for i,r in enumerate(content_base[0]):
        if r[1] == request.form['edit_event']:
            r[event_field.index('name')] = name_edit
            r[event_field.index('content')] = content
            r[event_field.index('percentage')] = percentage
            r[event_field.index('complete')] = percentage
            r[event_field.index('type_department')] = type_department
            r[event_field.index('type')] = job_type
            r[event_field.index('type_strategy')] = type_strategy

        if r[0] == old_id:
            r[event_field.index('name')] = name_edit
            r[event_field.index('complete')] = percentage
            r[event_field.index('type_department')] = type_department
            r[event_field.index('type')] = job_type
            r[event_field.index('type_strategy')] = type_strategy

    # old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])
    old_task = db.session.query(Task.task_id, Task.name, Task.percentage).filter_by(executer = session['username']).filter(Task.percentage != '100%').all()
    list_type_department = [r[0] for r in session['type_department']]
    work_hour = 14

    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,list_type_department=list_type_department, work_hour=work_hour, old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})


# ADD OLD TASK
@app.route('/ajax_add_old_task', methods=['POST'])
def ajax_add_old_task():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])

    # result_task = sql("select * from task where executer = ? and percentage != '100%'",[session['username']])
    result_task = db.session.query(Task).filter_by(executer = session['username']).filter(Task.percentage != '100%').all()
    # Insert Database
    id_cong_viec_cu = request.form['select_cong_viec']
    
    event_id = event_id_create(id_cong_viec_cu)
    name = [r.name for r in result_task if r.task_id == id_cong_viec_cu][0]

    type_department = [r.type_department for r in result_task if r.task_id == id_cong_viec_cu][0]
    job_type = [r.type for r in result_task if r.task_id == id_cong_viec_cu][0]
    type_strategy = [r.type_strategy for r in result_task if r.task_id == id_cong_viec_cu][0]
    content = request.form['Content']
    status = ''
    percentage = request.form['Percentage']
    border_color = '#901e1d'
    executer = [r.executer for r in result_task if r.task_id == id_cong_viec_cu][0]
    executer_name = [r.executer_name for r in result_task if r.task_id == id_cong_viec_cu][0]
    start = index_to_time(request.form['time_start'])
    

    end = index_to_time(request.form['time_end'])
    last_update = index_to_time(request.form['time_end'])

    complete = percentage
    department = [r.department for r in result_task if r.task_id == id_cong_viec_cu][0]
    type_department = [r.type_department for r in result_task if r.task_id == id_cong_viec_cu][0]
        
    # Insert Event

    new_event = Event(id_cong_viec_cu, event_id, name, job_type, type_strategy, content, status, percentage, executer, executer_name, start, end, complete, department, type_department, border_color)
    db.session.add(new_event)
    db.session.commit()

    # sql("insert into event({}) values({})".format(','.join(event_field),','.join(['?']*len(event_field))),[id_cong_viec_cu, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter,  executer_name, assigner_name,supporter_name, customer, disable,start, end,complete,department,type_department,border_color])

    # Update Task and Event
    old_task = db.session.query(Task).filter_by(task_id = id_cong_viec_cu).all()
    for r in old_task:
        r.last_update = last_update
        r.percentage = percentage
        r.end_time = end        
        db.session.commit()

    # sql("update task set last_update = ?, percentage = ? where task_id = ?",[last_update,percentage,id_cong_viec_cu])

    all_event = db.session.query(Event).filter_by(task_id = id_cong_viec_cu).all()
    for r in all_event:
        r.complete = percentage

        db.session.commit()

    # sql("update event set complete = ? where task_id = ?",[sql("select percentage from task where task_id = ?",[id_cong_viec_cu])[0][0],id_cong_viec_cu])
    

    # sql("update task set end_time = ? where task_id = ?",[end,id_cong_viec_cu])

    new_log = Event_log(id_cong_viec_cu,event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'old task')    
    db.session.add(new_log)
    db.session.commit()

    # sql("insert into event_log values(?,?,?,?,?,?)",[id_cong_viec_cu,event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'old task'])

    # Update block_base, content_base
    if block_base:
        block_base = [block_base[0] + [[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [content_base[0] + [[id_cong_viec_cu, event_id, name, job_type, type_strategy, content, status, percentage, executer, executer_name, start, end, complete, department, type_department, border_color]]]
    else:
        block_base = [[[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [[[id_cong_viec_cu, event_id, name, job_type, type_strategy, content, status, percentage, executer, executer_name, start, end, complete, department, type_department, border_color]]]

    list_type_department = [r[0] for r in session['type_department']]
    work_hour = 14
    old_task = db.session.query(Task.task_id, Task.name, Task.percentage).filter_by(executer = session['username']).filter(Task.percentage != '100%').all()
    # old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])
    
    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,list_type_department=list_type_department, work_hour=work_hour, old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})




print('WEB CV QTRR')

# if __name__ == '__main__':
#     app.debug = True
#     http = WSGIServer(('10.62.24.161', 5000), app.wsgi_app)
#     http.serve_forever()


# from os import environ
# # from web_cong_viec import app

if __name__ == '__main__':
    app.debug = True
    # HOST = environ.get('server_host', '10.62.24.161')
##    NAME = environ.get('server_name','phu.co.tcb.vn:5555')
    HOST = environ.get('server_host', 'localhost')
    try:
        # PORT = int(environ.get('8080', '3000'))
        PORT = int(environ.get('server_port', '5599'))
    except ValueError:
        PORT = 5599
    app.run(HOST, PORT, threaded = True)


