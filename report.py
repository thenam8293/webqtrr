# -*- coding: utf8 -*-

from __future__ import division

import datetime as dt
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine, inspect, or_, and_, update, func

from config import Config
from model import app, db, Event, Task, Event_log, Department, Userr, ID_auto, Admin_depatment, Profile, ID_auto

list_day_off = [dt.date(2017,5,1),dt.date(2017,5,2),dt.date(2017,4,6),dt.date(2017,9,2),dt.date(2017,9,3),dt.date(2017,9,4)]

# list_mail_name = [r1[0] for r1 in sql("select mail_name from profile")]
list_mail_name = db.session.query(Profile.mail_name).all()

# list_department = [r1[0] for r1 in sql("select distinct phong from profile")]
list_department = [r.phong for r in db.session.query(Profile.phong).distinct().all()]

list_department_section = [r.phong + '|' + r.bophan for r in db.session.query(Profile.phong, Profile.bophan).filter(Profile.bophan != '').all()]
# list_department_section = [r1[0] + '|' + r1[1] for r1 in sql("select distinct phong,bophan from profile where bophan != ''")]
required_field = ['task_id','event_id','executer','department','type_department','start_time','end_time','type','type_strategy']
list_work_type_qtrr = [u"Thẩm định,phê duyệt,phân luồng", u"Vận hành Hội đồng, Ủy ban", u"Giám sát,nhận diện, cảnh báo", u"Cải tiến hệ thống, mô hình, quy trình", u"Xây dựng kiểm soát Budget",u"Xây dựng, quy định, chính sách, quy trình", u"Mua bán, xử lý nợ", u"Tư vấn,giải đáp", u"Hành chính, văn phòng", u"Phát triển nhân lực", u"Tham gia dự án", u"Báo cáo, dữ liệu", u"Khác"]
list_work_type_tcb =[u"Vận hành", u"Dữ liệu",u"Nhân sự",u"Quy trình, chính sách",u"Văn hóa"]

def str_to_dt(x):
    try:
        return dt.datetime.strptime(x,'%H:%M %d/%m/%Y')
    except:
        return dt.datetime.strptime(x,'%d/%m/%Y')

def dt_to_str_nguoc(x):
    # Transfer datatime to string
    return str(x.date())[-2:] + '/'+str(x.date())[-5:-3] + '/' +  str(x.date())[:-6]

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

def calculate(x,start_time,end_time):
    if x in list_mail_name:
        # Prepare
        # - user name and mail name
        mail_name = x
        # username = sql("select username from profile where mail_name = ?",[x])[0][0]
        username = db.session.query(Profile.username).filter_by(mail_name = x).all()[0].username
        # - department and work type
        # department = sql("select phong from profile where username = ?",[username])[0][0]
        department = db.session.query(Profile.phong).filter_by(username = x).all()[0].phong

        # list_work_type_department = [r[0] for r in sql("select type_department from department where department = ?  order by type_department",[department])]
        list_work_type_department = [r.type_department for r in db.session.query(Department.type_department).filter_by(department = department).all()]

        # - config start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day off personal
        try:
            # list_day_off_personal = list_day_off + [str_to_dt(r).date() for r in sql("select ngay_nghi from profile where username = ?",[username])[0][0].split(',')]

            list_day_off_personal = list_day_off + [str_to_dt(r.ngay_nghi).date() for r in db.session.query(Profile.ngay_nghi).filter_by(username = username)[0].ngay_nghi.split(',')]
        except:
            list_day_off_personal = list_day_off

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off_personal]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = [list(r) for r in sql("select {} from event where executer = ?".format(','.join(required_field)),[username])]
        event_data = db.session.query(Event).filter_by

        # -- convert str to datetime, filter by time and add event duration
        for i,r in enumerate(event_data):
            r[required_field.index('start_time')] = str_to_dt(r[required_field.index('start_time')])
            r[required_field.index('end_time')] = str_to_dt(r[required_field.index('end_time')])
        event_data = [r for r in event_data if start_time <= r[required_field.index('start_time')] < end_time]
        for i,r in enumerate(event_data):
            event_data[i].append((r[required_field.index('end_time')] - r[required_field.index('start_time')]).total_seconds()/3600)
        
        # calculate index
        # - number of worked time
        worked_time = sum([r[-1] for r in event_data])

        # - number of executer
        number_executer = 1

        # - number of task
        number_task = len(set([r[required_field.index('task_id')] for r in event_data]))

        # - number of worked time group by day in range time
        worked_time_in_range = [sum([r[-1] for r in event_data if r[required_field.index('start_time')].date() == r1]) for r1 in list_day_in_range]

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
            distribute_department = [sum([r[-1] for r in [r1 for r1 in event_data if r1[required_field.index("type_department")] == r2]])*100/worked_time for r2 in list_work_type_department]
            distribute_qtrr = [sum([r[-1]/len(r[required_field.index('type')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type")].split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r[-1]/len(r[required_field.index('type_strategy')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type_strategy")].split(';')]])*100/worked_time for r2 in list_work_type_tcb]

            # -- optimize list (remove object 0, round 1 and add up to 100%)
            distribute_department_op, list_work_type_department_op = list_optimize(distribute_department, list_work_type_department)
            distribute_qtrr_op, list_work_type_qtrr_op = list_optimize(distribute_qtrr, list_work_type_qtrr)
            distribute_tcb_op, list_work_type_tcb_op = list_optimize(distribute_tcb, list_work_type_tcb)
        else:
            distribute_department_op,distribute_qtrr_op,distribute_tcb_op = ['']*3
            list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op = list_work_type_department, list_work_type_qtrr, list_work_type_tcb

        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per, number_executer, worked_time_per_user] 

    elif x in list_department:
        # Prepare
        # - list user name active and mail name
        temp = sql("select username, mail_name from profile where phong = ? and status != 'disable'  order by username",[x])
        list_username_department = [r[0] for r in temp]
        list_mail_name_department = [r[1] for r in temp]

        # - work type department
        list_work_type_department = [r[0] for r in sql("select type_department from department where department = ?  order by type_department",[x])]

        # - start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = [list(r) for r in sql("select {} from event where department = ? and executer in ({})".format(','.join(required_field),','.join(['?']*len(list_username_department))),[x] + list_username_department)]
        
        # - convert str to datetime, filter by time and add event duration
        for i,r in enumerate(event_data):
            r[required_field.index('start_time')] = str_to_dt(r[required_field.index('start_time')])
            r[required_field.index('end_time')] = str_to_dt(r[required_field.index('end_time')])
        event_data = [r for r in event_data if start_time <= r[required_field.index('start_time')] < end_time]
        for i,r in enumerate(event_data):
            event_data[i].append((r[required_field.index('end_time')] - r[required_field.index('start_time')]).total_seconds()/3600)

        # calculate index
        # - number of worked time
        worked_time = sum([r[-1] for r in event_data])

        # - number of task
        number_task = len(set([r[required_field.index('task_id')] for r in event_data]))

        # - worked time percentage of department and per user
        worked_time_per_user = []
        for i,username in enumerate(list_username_department):
            try:
                list_day_off_personal = list_day_off + [str_to_dt(r).date() for r in sql("select ngay_nghi from profile where username = ?",[username])[0][0].split(',')]
            except:
                list_day_off_personal = list_day_off
            list_day_in_range_user = [r for r in list_day_in_range if r not in list_day_off_personal]

            worked_time_user = sum([r[-1] for r in event_data if r[required_field.index('executer')] == username])
            number_work_day = len([r for r in list_day_in_range_user if r.weekday() == 5])/2 + len([r for r in list_day_in_range_user if r.weekday() != 5])
            
            if number_work_day:
                worked_time_per = str(round(worked_time_user/number_work_day/8*100,2)) + '%'
            else:
                worked_time_per = ''
                
            worked_time_per_user.append([list_mail_name_department[i],worked_time_user,number_work_day*8,worked_time_per])
        worked_time_per_department = str(round(worked_time/sum([r[2] for r in worked_time_per_user])*100,2)) + '%'

        # - number of executer
        number_executer = len(worked_time_per_user)

        # - number of work day
        number_work_day = round(sum([r[2] for r in worked_time_per_user])/number_executer/8,2)

        # - number of worked time group by day in range time
        worked_time_in_range = [round(sum([r[-1] for r in event_data if r[required_field.index('start_time')].date() == r1])/number_executer,2) for r1 in list_day_in_range]

        # - distribute in work type
        if worked_time:
            distribute_department = [sum([r[-1] for r in [r1 for r1 in event_data if r1[required_field.index("type_department")] == r2]])*100/worked_time for r2 in list_work_type_department]
            distribute_qtrr = [sum([r[-1]/len(r[required_field.index('type')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type")].split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r[-1]/len(r[required_field.index('type_strategy')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type_strategy")].split(';')]])*100/worked_time for r2 in list_work_type_tcb]
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
        temp = sql("select username, mail_name from profile where phong = ? and bophan = ? and status != 'disable'  order by username",[x.split('|')[0],x.split('|')[1]])
        list_username_section = [r[0] for r in temp]
        list_mail_name_section = [r[1] for r in temp]

        # - work type department
        list_work_type_department = [r[0] for r in sql("select type_department from department where department = ?  order by type_department",[x.split('|')[0]])]

        # - start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = [list(r) for r in sql("select {} from event where executer in ({})".format(','.join(required_field),','.join(["'" + r + "'" for r in list_username_section])))]
        
        # - convert str to datetime, filter by time and add event duration
        for i,r in enumerate(event_data):
            r[required_field.index('start_time')] = str_to_dt(r[required_field.index('start_time')])
            r[required_field.index('end_time')] = str_to_dt(r[required_field.index('end_time')])
        event_data = [r for r in event_data if start_time <= r[required_field.index('start_time')] < end_time]
        for i,r in enumerate(event_data):
            event_data[i].append((r[required_field.index('end_time')] - r[required_field.index('start_time')]).total_seconds()/3600)

        # calculate index
        # - number of worked time
        worked_time = sum([r[-1] for r in event_data])

        # - number of task
        number_task = len(set([r[required_field.index('task_id')] for r in event_data]))

        # - worked time percentage section and per user
        worked_time_per_user = []
        for i,username in enumerate(list_username_section):
            try:
                list_day_off_personal = list_day_off + [str_to_dt(r).date() for r in sql("select ngay_nghi from profile where username = ?",[username])[0][0].split(',')]
            except:
                list_day_off_personal = list_day_off
            list_day_in_range_user = [r for r in list_day_in_range if r not in list_day_off_personal]

            worked_time_user = sum([r[-1] for r in event_data if r[required_field.index('executer')] == username])
            number_work_day = len([r for r in list_day_in_range_user if r.weekday() == 5])/2 + len([r for r in list_day_in_range_user if r.weekday() != 5])

            if number_work_day:
                worked_time_per = str(round(worked_time_user/number_work_day/8*100,2)) + '%'
            else:
                worked_time_per = ''
                
            worked_time_per_user.append([list_mail_name_section[i],worked_time_user,number_work_day*8,worked_time_per])
        worked_time_per_section = str(round(worked_time/sum([r[2] for r in worked_time_per_user])*100,2)) + '%'

        # - number of executer
        number_executer = len(worked_time_per_user)

        # - number of work day
        number_work_day = round(sum([r[2] for r in worked_time_per_user])/number_executer/8,2)

        # - number of worked time group by day in range time
        worked_time_in_range = [round(sum([r[-1] for r in event_data if r[required_field.index('start_time')].date() == r1])/number_executer,2) for r1 in list_day_in_range]

        # - distribute in work type
        if worked_time:
            distribute_department = [sum([r[-1] for r in [r1 for r1 in event_data if r1[required_field.index("type_department")] == r2]])*100/worked_time for r2 in list_work_type_department]
            distribute_qtrr = [sum([r[-1]/len(r[required_field.index('type')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type")].split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r[-1]/len(r[required_field.index('type_strategy')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type_strategy")].split(';')]])*100/worked_time for r2 in list_work_type_tcb]
            # -- optimize list (remove object 0, round 2 and add up to 100%)
            distribute_department_op, list_work_type_department_op = list_optimize(distribute_department, list_work_type_department)
            distribute_qtrr_op, list_work_type_qtrr_op = list_optimize(distribute_qtrr, list_work_type_qtrr)
            distribute_tcb_op, list_work_type_tcb_op = list_optimize(distribute_tcb, list_work_type_tcb)
        else:
            distribute_department_op,distribute_qtrr_op,distribute_tcb_op = ['']*3
            list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op = list_work_type_department, list_work_type_qtrr, list_work_type_tcb

        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per_section, number_executer, worked_time_per_user]

    elif x == u'Khối QTRR':
        # Prepare
        # - list user name active and mail name
        temp = sql("select username, mail_name from profile where status != 'disable'  order by username")
        list_username_qtrr = [r[0] for r in temp]
        list_mail_name_qtrr = [r[1] for r in temp]

        # - start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = [list(r) for r in sql("select {} from event".format(','.join(required_field)))]
        
        # - convert str to datetime, filter by time and add event duration
        for i,r in enumerate(event_data):
            r[required_field.index('start_time')] = str_to_dt(r[required_field.index('start_time')])
            r[required_field.index('end_time')] = str_to_dt(r[required_field.index('end_time')])
        event_data = [r for r in event_data if start_time <= r[required_field.index('start_time')] < end_time]
        for i,r in enumerate(event_data):
            event_data[i].append((r[required_field.index('end_time')] - r[required_field.index('start_time')]).total_seconds()/3600)

        # calculate index
        # - number of worked time
        worked_time = sum([r[-1] for r in event_data])

        # - number of task
        number_task = len(set([r[required_field.index('task_id')] for r in event_data]))

        # - worked time percentage and per user
        worked_time_per_user = []
        for i,username in enumerate(list_username_qtrr):
            try:
                list_day_off_personal = list_day_off + [str_to_dt(r).date() for r in sql("select ngay_nghi from profile where username = ?",[username])[0][0].split(',')]
            except:
                list_day_off_personal = list_day_off
            list_day_in_range_user = [r for r in list_day_in_range if r not in list_day_off_personal]
            
            worked_time_user = sum([r[-1] for r in event_data if r[required_field.index('executer')] == username])
            number_work_day = len([r for r in list_day_in_range_user if r.weekday() == 5])/2 + len([r for r in list_day_in_range_user if r.weekday() != 5])

            if number_work_day:
                worked_time_per = str(round(worked_time_user/number_work_day/8*100,2)) + '%'
            else:
                worked_time_per = ''
                
            worked_time_per_user.append([list_mail_name_qtrr[i],worked_time_user,number_work_day*8,worked_time_per])
        worked_time_per_qtrr = str(round(worked_time/sum([r[2] for r in worked_time_per_user])*100,2)) + '%'

        # - number of executer
        number_executer = len(worked_time_per_user)

        # - number of work day
        number_work_day = round(sum([r[2] for r in worked_time_per_user])/number_executer/8,2)

        # - number of worked time group by day in range time
        worked_time_in_range = [round(sum([r[-1] for r in event_data if r[required_field.index('start_time')].date() == r1])/number_executer,2) for r1 in list_day_in_range]

        # - distribute in work type
        if worked_time:
            distribute_qtrr = [sum([r[-1]/len(r[required_field.index('type')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type")].split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r[-1]/len(r[required_field.index('type_strategy')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type_strategy")].split(';')]])*100/worked_time for r2 in list_work_type_tcb]
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

def calculate_intro(x):
    # Prepare
    # - user name and mail name
    mail_name = x
    username = sql("select username from profile where mail_name = ?",[x])[0][0]

    # - config start time and end time
    start_time = dt.datetime(2017,4,2)
    end_time = dt.datetime.now()

    # - list day off personal
    try:
        list_day_off_personal = list_day_off + [str_to_dt(r).date() for r in sql("select ngay_nghi from profile where username = ?",[username])[0][0].split(',')]
    except:
        list_day_off_personal = list_day_off

    # - list day in range
    list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
    list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off_personal]


    # - event data
    event_data = [list(r) for r in sql("select {} from event where executer = ?".format(','.join(required_field)),[username])]
    
    # -- convert str to datetime, filter by time and add event duration
    for i,r in enumerate(event_data):
        r[required_field.index('start_time')] = str_to_dt(r[required_field.index('start_time')])
        r[required_field.index('end_time')] = str_to_dt(r[required_field.index('end_time')])
    event_data = [r for r in event_data if start_time <= r[required_field.index('start_time')] < end_time]
    for i,r in enumerate(event_data):
        event_data[i].append((r[required_field.index('end_time')] - r[required_field.index('start_time')]).total_seconds()/3600)
    
    # calculate index
    # - number of worked time
    worked_time = sum([r[-1] for r in event_data])

    # - number of work day standard
    number_work_day = len([r for r in list_day_in_range if r.weekday() == 5])/2 + len([r for r in list_day_in_range if r.weekday() != 5])

    # - number of worked time group by day in range time
    worked_time_in_range = [sum([r[-1] for r in event_data if r[required_field.index('start_time')].date() == r1]) for r1 in list_day_in_range]

    # - list day not yet report
    list_day_not_report = [list_day_in_range[i] for i,r in enumerate(worked_time_in_range) if r == 0]

    return [worked_time, number_work_day, list_day_not_report]

def calculate_division_report(x,start_time,end_time):
    if x in list_department:
        # Prepare
        # - list user name active and mail name
        temp = sql("select username, mail_name from profile where phong = ? and status != 'disable'  order by username",[x])
        list_username_department = [r[0] for r in temp]
        list_mail_name_department = [r[1] for r in temp]

        # - work type department
        list_work_type_department = [r[0] for r in sql("select type_department from department where department = ?  order by type_department",[x])]

        # - start time and end time
        start_time, end_time = time_config(start_time, end_time)

        # - list day in range
        list_day_in_range = [start_time + dt.timedelta(days = i) for i in range((end_time - start_time).days + 1)]
        list_day_in_range = [r.date() for r in list_day_in_range if r.weekday() != 6 and r.date() not in list_day_off]
        list_day_in_range_str = [str(r)[-5:] for r in list_day_in_range]

        # - event data
        event_data = [list(r) for r in sql("select {} from event where department = ? and executer in ({})".format(','.join(required_field),','.join(['?']*len(list_username_department))),[x] + list_username_department)]
        
        # - convert str to datetime, filter by time and add event duration
        for i,r in enumerate(event_data):
            r[required_field.index('start_time')] = str_to_dt(r[required_field.index('start_time')])
            r[required_field.index('end_time')] = str_to_dt(r[required_field.index('end_time')])
        event_data = [r for r in event_data if start_time <= r[required_field.index('start_time')] < end_time]
        for i,r in enumerate(event_data):
            event_data[i].append((r[required_field.index('end_time')] - r[required_field.index('start_time')]).total_seconds()/3600)

        # calculate index
        # - number of worked time
        worked_time = sum([r[-1] for r in event_data])

        # - number of task
        number_task = len(set([r[required_field.index('task_id')] for r in event_data]))

        # - worked time percentage of department and per user
        worked_time_per_user = []
        for i,username in enumerate(list_username_department):
            try:
                list_day_off_personal = list_day_off + [str_to_dt(r).date() for r in sql("select ngay_nghi from profile where username = ?",[username])[0][0].split(',')]
            except:
                list_day_off_personal = list_day_off
            list_day_in_range_user = [r for r in list_day_in_range if r not in list_day_off_personal]

            worked_time_user = sum([r[-1] for r in event_data if r[required_field.index('executer')] == username])
            number_work_day = len([r for r in list_day_in_range_user if r.weekday() == 5])/2 + len([r for r in list_day_in_range_user if r.weekday() != 5])
            
            if number_work_day:
                worked_time_per = str(round(worked_time_user/number_work_day/8*100,2)) + '%'
            else:
                worked_time_per = ''
                
            worked_time_per_user.append([list_mail_name_department[i],worked_time_user,number_work_day*8,worked_time_per])
        worked_time_per_department = str(round(worked_time/sum([r[2] for r in worked_time_per_user])*100,2)) + '%'

        # - number of executer
        number_executer = len(worked_time_per_user)

        # - number of work day
        number_work_day = round(sum([r[2] for r in worked_time_per_user])/number_executer/8,2)

        # - number of worked time group by day in range time
        worked_time_in_range = [round(sum([r[-1] for r in event_data if r[required_field.index('start_time')].date() == r1])/number_executer,2) for r1 in list_day_in_range]

        # - distribute in work type
        if worked_time:
            distribute_department = [sum([r[-1] for r in [r1 for r1 in event_data if r1[required_field.index("type_department")] == r2]])*100/worked_time for r2 in list_work_type_department]
            distribute_qtrr = [sum([r[-1]/len(r[required_field.index('type')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type")].split(';')]])*100/worked_time for r2 in list_work_type_qtrr]
            distribute_tcb = [sum([r[-1]/len(r[required_field.index('type_strategy')].split(';')) for r in [r1 for r1 in event_data if r2 in r1[required_field.index("type_strategy")].split(';')]])*100/worked_time for r2 in list_work_type_tcb]
            # -- optimize list (remove object 0, round 2 and add up to 100%)
            distribute_department_op, list_work_type_department_op = list_optimize(distribute_department, list_work_type_department)
            distribute_qtrr_op, list_work_type_qtrr_op = list_optimize(distribute_qtrr, list_work_type_qtrr)
            distribute_tcb_op, list_work_type_tcb_op = list_optimize(distribute_tcb, list_work_type_tcb)
        else:
            distribute_department_op,distribute_qtrr_op,distribute_tcb_op = ['']*3
            list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op = list_work_type_department, list_work_type_qtrr, list_work_type_tcb

        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per_department, number_executer, worked_time_per_user]

    elif x == u'Khối QTRR':
        month = dt_to_str_nguoc(start_time)
        
        data_khoi = sql("SELECT * FROM REPORT_ALL_DIVISION WHERE MONTH = ?",[month])
        # try:
        worked_time = float(data_khoi[0][0])
        number_task = int(data_khoi[0][1])
        list_day_in_range_str = data_khoi[0][2].split("; ")
        worked_time_in_range = data_khoi[0][3].split("; ")
        number_work_day = int(data_khoi[0][4])
        distribute_tcb_op = data_khoi[0][5].split("; ")
        print distribute_tcb_op
        list_work_type_qtrr_op = data_khoi[0][6].split(";")
        number_executer = int(data_khoi[0][7])
        list_work_type_department_op = []
        distribute_qtrr_op = []
        list_work_type_tcb_op = []
        worked_time_per_department = []
        worked_time_per_user = []
        # except:
        #     worked_time = number_task  = worked_time_per_user = 0
        #     number_work_day = 24
        #     number_executer = 1
        #     list_day_in_range_str = worked_time_in_range = distribute_qtrr_op = distribute_tcb_op = list_work_type_department_op = list_work_type_qtrr_op = list_work_type_tcb_op = worked_time_per_department = []


        distribute_department_op = sql("SELECT * FROM REPORT_ALL_TRUNG_TAM WHERE MONTH = ?",[month])


        return [worked_time, number_task, list_day_in_range_str, worked_time_in_range, number_work_day, distribute_department_op, distribute_qtrr_op, distribute_tcb_op, list_work_type_department_op, list_work_type_qtrr_op, list_work_type_tcb_op, worked_time_per_department, number_executer, worked_time_per_user]
    else:
        pass
# import cProfile
# cProfile.run('sql("select username from profile where mail_name = ?",[x])[0][0]')
# x = 'PHU QTRR. NGUYEN QUANG'
# x = u'Quản trị dữ liệu và phân tích và giám sát hoạt động tín dụng|Thư ký hội đồng tín dụng'
# # x = u'DUONG QTRR. BUI NHAT'
# start_time_test = dt.datetime(2017,10,1)
# end_time_test = dt.datetime(2017,10,31)
# cProfile.run('calculate(x,start_time_test,end_time_test)')
# print calculate(x,start_time_test,end_time_test)

