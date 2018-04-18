from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Sequence, VARCHAR,NVARCHAR, DateTime, update
app = Flask(__name__,static_url_path='/static')

db = SQLAlchemy(app)

# EVENT
class Event(db.Model):
    __tablename__ = "event"
    task_id = db.Column('task_id', String, nullable = False)
    event_id = db.Column('event_id', String, nullable = False, primary_key = True)
    name = db.Column('name', String, nullable = False)
    type = db.Column('type', String, nullable = False)
    type_strategy = db.Column('type_strategy', String, nullable = False)
    content = db.Column('content', String, nullable = False)
    status = db.Column('status', String, nullable = False)
    percentage = db.Column('percentage', String, nullable = False)
    executer = db.Column('executer', String, nullable = False)
    executer_name = db.Column('executer_name', String, nullable = False)
    start_time = db.Column('start_time', String, nullable = False)
    end_time = db.Column('end_time', String, nullable = False)
    complete = db.Column('complete', String, nullable = False)
    department = db.Column('department', String, nullable = False)
    type_department = db.Column('type_department', String, nullable = False)
    border_color = db.Column('border_color', String, nullable = False)

    def __init__(self, task_id, event_id, name, type, type_strategy, content, status, percentage, executer, executer_name, start_time, end_time, complete, department, type_department, border_color):
        self.task_id = task_id
        self.event_id = event_id
        self.name = name
        self.type = type
        self.type_strategy = type_strategy
        self.content = content
        self.status = status
        self.percentage = percentage
        self.executer = executer
        self.executer_name = executer_name
        self.start_time = start_time
        self.end_time = end_time
        self.complete = complete
        self.department = department
        self.type_department = type_department
        self.border_color = border_color

        def __repr__(self):
            return str([self.task_id, self.event_id, self.name, self.type, self.type_strategy, self.content, self.status, self.percentage, self.executer, self.executer_name, self.start_time, self.end_time, self.complete, self.department, self.type_department, self.border_color])


# Task
class Task(db.Model):
    __tablename__ = "task"
    task_id = db.Column('task_id', String, nullable = False, primary_key = True)
    name = db.Column('name', String, nullable = False)
    type = db.Column('type', String, nullable = False)
    type_strategy = db.Column('type_strategy', String, nullable = False)
    content = db.Column('content', String, nullable = False)
    status = db.Column('status', String, nullable = False)
    percentage = db.Column('percentage', String, nullable = False)
    executer = db.Column('executer', String, nullable = False)
    executer_name = db.Column('executer_name', String, nullable = False)
    start_time = db.Column('start_time', String, nullable = False)
    end_time = db.Column('end_time', String, nullable = False)
    last_update = db.Column('last_update', String, nullable = False)
    department = db.Column('department', String, nullable = False)
    type_department = db.Column('type_department', String, nullable = False)
    border_color = db.Column('border_color', String, nullable = False)

    def __init__(self, task_id, name, type, type_strategy, content, status, percentage, executer, executer_name, start_time, end_time, last_update, department, type_department, border_color):
        self.task_id = task_id
        self.name = name
        self.type = type
        self.type_strategy = type_strategy
        self.content = content
        self.status = status
        self.percentage = percentage
        self.executer = executer
        self.executer_name = executer_name
        self.start_time = start_time
        self.end_time = end_time
        self.last_update = last_update
        self.department = department
        self.type_department = type_department
        self.border_color = border_color

        def __repr__(self):
            return str([self.task_id, self.name, self.type, self.type_strategy, self.content, self.status, self.percentage, self.executer, self.executer_name, self.start_time, self.end_time, self.last_update, self.department, self.type_department, self.border_color])


#Event_log
class Event_log(db.Model):
    __tablename__ = "event_log"
    task_id = db.Column('task_id', String, nullable = False, primary_key = True)
    event_id = db.Column('event_id', String, nullable = False, primary_key = True)
    Mien = db.Column('Mien', String, nullable = False, primary_key = True)
    username = db.Column('username', String, nullable = False, primary_key = True)
    time = db.Column('time', String, nullable = False, primary_key = True)
    action = db.Column('action', String, nullable = False, primary_key = True)

    def __init__(self, task_id, event_id, Mien, username, time, action):
        self.task_id = task_id
        self.event_id = event_id
        self.Mien = Mien
        self.username = username
        self.time = time
        self.action = action

    def __repr__(self):
        return str([self.task_id, self.event_id, self.Mien, self.username, self.time, self.action])


# Department
class Department(db.Model):
    __tablename__ = "department"
    department = db.Column('department', String, nullable = False, primary_key = True)
    type_department = db.Column('type_department', String, nullable = False, primary_key = True)
    type_ = db.Column('type_', String, nullable = False, primary_key = True)
    type_strategy = db.Column('type_strategy', String, nullable = False, primary_key = True)

    def __init__(self, department, type_department, type_, type_strategy):
        self.department = department
        self.type_department = type_department
        self.type_ = type_
        self.type_strategy = type_strategy
    def __repr__(self):
        return str([self.department, self.type_department, self.type_, self.type_strategy])


# User
class Userr(db.Model):
    __tablename__ = "Userr"
    username = db.Column('username', String, nullable = False, primary_key = True)
    password = db.Column('password', String, nullable = False)
    role = db.Column('role', String, nullable = False)
    userid = db.Column('userid', String, nullable = False)

    def __init__(self, username, password, role, userid):
        self.username = username
        self.password = password
        self.role = role
        self.userid = userid

    def __repr__(self):
        return str([self.username, self.password, self.role, self.userid])


# ID_auto
class ID_auto(db.Model):
    __tablename__ = "ID_auto_create"

    task_id = db.Column('task_id', String, nullable = False, primary_key = True)
    event_id = db.Column('event_id', String, nullable = False, primary_key = True)

    def __init__(self, task_id, event_id):

        self.task_id = task_id
        self.event_id = event_id

    def __repr__(self):
        return str([self.task_id, self.event_id])


# Admin_depatment
class Admin_depatment(db.Model):
    __tablename__ = "admin_depatment"
    admin = db.Column('admin', String, nullable = False, primary_key = True)

    def __init__(self, admin):
        self.admin = admin

    def __repr__(self):
        return str([self.admin])


# Profile
class Profile(db.Model):
    __tablename__ = "Profile"
    username = db.Column('username', String, nullable = False, primary_key = True)
    hoten = db.Column('hoten', String, nullable = False)
    maNV = db.Column('maNV', String, nullable = False)
    ngaysinh = db.Column('ngaysinh', String, nullable = False)
    CMND = db.Column('CMND', String, nullable = False)
    ngayvaolam = db.Column('ngayvaolam', String, nullable = False)
    mail = db.Column('mail', String, nullable = False)
    phone = db.Column('phone', String, nullable = False)
    mobile = db.Column('mobile', String, nullable = False)
    phong = db.Column('phong', String, nullable = False)
    diachi = db.Column('diachi', String, nullable = False)
    bophan = db.Column('bophan', String, nullable = False)
    chucdanh = db.Column('chucdanh', String, nullable = False)
    phong_viettat = db.Column('phong_viettat', String, nullable = False)
    time_begin = db.Column('time_begin', String, nullable = False)
    time_finish = db.Column('time_finish', String, nullable = False)
    name = db.Column('name', String, nullable = False)
    n_0 = db.Column('n_0', String, nullable = False)
    n_1 = db.Column('n_1', String, nullable = False)
    n_2 = db.Column('n_2', String, nullable = False)
    n_3 = db.Column('n_3', String, nullable = False)
    name_n_0 = db.Column('name_n_0', String, nullable = False)
    name_n_1 = db.Column('name_n_1', String, nullable = False)
    name_n_2 = db.Column('name_n_2', String, nullable = False)
    name_n_3 = db.Column('name_n_3', String, nullable = False)
    hash_1 = db.Column('hash_1', String, nullable = False)
    hash_2 = db.Column('hash_2', String, nullable = False)
    hash_3 = db.Column('hash_3', String, nullable = False)
    mail_name = db.Column('mail_name', String, nullable = False)
    name_test = db.Column('name_test', String, nullable = False)
    status = db.Column('status', String, nullable = False)

    def __init__(self, username, hoten, maNV, ngaysinh, CMND, ngayvaolam, mail, phone, mobile, phong, diachi, bophan, chucdanh, phong_viettat, time_begin, time_finish, name, n_0, n_1, n_2, n_3, name_n_0, name_n_1, name_n_2, name_n_3, hash_1, hash_2, hash_3, mail_name, name_test, status):
        self.username = username
        self.hoten = hoten
        self.maNV = maNV
        self.ngaysinh = ngaysinh
        self.CMND = CMND
        self.ngayvaolam = ngayvaolam
        self.mail = mail
        self.phone = phone
        self.mobile = mobile
        self.phong = phong
        self.diachi = diachi
        self.bophan = bophan
        self.chucdanh = chucdanh
        self.phong_viettat = phong_viettat
        self.time_begin = time_begin
        self.time_finish = time_finish
        self.name = name
        self.n_0 = n_0
        self.n_1 = n_1
        self.n_2 = n_2
        self.n_3 = n_3
        self.name_n_0 = name_n_0
        self.name_n_1 = name_n_1
        self.name_n_2 = name_n_2
        self.name_n_3 = name_n_3
        self.hash_1 = hash_1
        self.hash_2 = hash_2
        self.hash_3 = hash_3
        self.mail_name = mail_name
        self.name_test = name_test
        self.status = status

    def __repr__(self):
        return str([self.username, self.hoten, self.maNV, self.ngaysinh, self.CMND, self.ngayvaolam, self.mail, self.phone, self.mobile, self.phong, self.diachi, self.bophan, self.chucdanh, self.phong_viettat, self.time_begin, self.time_finish, self.name, self.n_0, self.n_1, self.n_2, self.n_3, self.name_n_0, self.name_n_1, self.name_n_2, self.name_n_3, self.hash_1, self.hash_2, self.hash_3, self.mail_name, self.name_test, self.status])

db.create_all()