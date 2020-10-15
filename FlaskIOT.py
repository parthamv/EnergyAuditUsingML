from flask import Flask, jsonify, flash, redirect, render_template, request, session, abort
import os
import pymysql as MySQLdb
import json
from datetime import datetime
from waitress import serve
import math

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics

import datetime
import random
import time

app = Flask(__name__)

minute = 0
hour = 0
summationHour = 0
summationDay = 0
summationMinute = 0
cnow = datetime.now()
c_month = 0
c_month = cnow.month()

@app.route('/sendDataToSQL')
def sendDataToSQL():
    now = datetime.datetime.now()
    month = str(now.year) + '-'+str(now.month)
    day = month+'-'+str(now.day)
    hour = day+' '+str(now.hour)
    minute = str(hour+':'+str(now.minute)+':00')
    node_id = request.args.get('node_id')
    voltage = request.args.get('voltage')
    current1 = request.args.get('current')
    current=consumed=random.randrange(10000,30000)/1000000
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute(
        "select meterId from node_meterid where node_id='%s'" % (node_id))
    data = cursor.fetchall()
    meter_id = data[0][0]
    cursor.execute("INSERT INTO minute_wise (meterId,date_time, voltage, current) VALUES(%d, '%s', '%s','%s')" % (
        meter_id, minute, voltage, current))
    minute += 1
    summationMinute += current
    if(minute == 60):
        cursor.execute("INSERT INTO hour_wise (meterId,date_time,current) VALUES(%d,'%s','%s')" % (
            meter_id, summationMinute, minute))
        hour += 1
        minute = 0        
        summationHour += summationMinute
        summationMinute = 0
        if(hour == 24):
            cursor.execute("INSERT INTO day_wise (meterId,current,datetime) VALUES(%d,'%s','%s')" % (
                meter_id, summationHour, day))
            hour = 0            
            summationDay += summationHour
            summationHour = 0
            if(c_month != now.month()):
                # cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
                #     meterId, month+"-01", summationDay, 0, 0, 0, 0, 0))
                current_cost=cost_calculation_predicted(summationDay)
                cursor.execute("UPDATE month_wise SET units=%d, cost=%d"%(summationDay,current_cost))
                c_month = now.month()
                summationDay = 0
                prediction(meter_id,month+"-01")
    return 'Data Sent'


def prediction(meter_id,month):
    predicted_value = 0
    # month_wise_list=query to retrive monthwise values
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute("select units from month_wise where meterId=%d"%(meter_id))
    data = cursor.fetchall()
    consumed = []
    for i in data:
        consumed.append(i[0])
    # print(consumed)
    # the prediction code #predicted_value=
    k = len(consumed)
    if(k % 2 == 1):
        x = np.array(consumed[0:int(k/2)]).reshape(-1, 1)
        y = np.array(consumed[int(k/2):k-1]).reshape(-1, 1)
    else:
        x = np.array(consumed[0:int(k/2)]).reshape(-1, 1)
        y = np.array(consumed[int(k/2):k]).reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=k-(k-1), random_state=4)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)  # training the algorithm
    y_pred = regressor.predict(X_test)
    predicted_value = float(y_pred)
    predicted_cost = cost_calculation_predicted(predicted_value)
    cursor.execute(
        "SELECT room_name FROM room_calculations     WHERE meterId=%d" % (meter_id))
    rooms = cursor.fetchall()
    no_of_rooms = len(rooms)

    cursor.execute(
        "SELECT max_limit FROM room_calculations WHERE meterId=%d" % (meter_id))
    max_limit_list=cursor.fetchall()

    max_limit=0

    for i in range(no_of_rooms):       
        max_limit+=max_limit_list[i][0]

    if max_limit < predicted_value:
        notify2="You have high probablility of exceeding the maximum usage which might be due to over usage or leakage"
        cursor.execute("INSERT INTO notification_message (meterId,message,status) values(%d,'%s',%d)"%(meter_id,notify2,0))

    if(predicted_value>500):
        reduction=predicted_value-500
        recommendation_message(meter_id,reduction,month)
    else:
        recommendation_message(meter_id,100,month)

    # UPDATE query to update the current month prediction and calculation
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, month, 0, no_of_rooms, max_limit, 0, predicted_value, predicted_cost))
    
    room_wise_calculation_predicted(meter_id,predicted_value,month)
    return 0

def recommendation_message(meter_id,reduction,month):             
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute("SELECT room_name,appliance_type,units_per_day,room_app_percentage FROM room_appliance where meterId=%d ORDER BY id"%(meter_id))
    data=cursor.fetchall()
    appliance_details=[]
    app_room_contribute=[]

    cursor.execute("SELECT room_name,use_percentage,max_limit from room_calculations where meterId=%d ORDER BY id"%(meter_id))
    room_data=cursor.fetchall()
    room_name=[]
    room_percentage=[]
    room_maxlimit=[]
    room_units=[]

    for i in range(len(room_data)):
        room_name.append(room_data[i][0])
        room_percentage.append(room_data[i][1])
        room_maxlimit.append(room_data[i][2])    

    room_reduction=[]
    for i in range(len(room_percentage)):
        e=[]
        temp1=(room_percentage[i]/100)*reduction
        e.append(room_name[i])
        e.append(temp1)
        total+=temp1
        room_reduction.append(e)    

    cursor.execute("SELECT room_name,appliance_type,units_per_day,room_app_percentage FROM room_appliance where meterId=%d ORDER BY id"%(meter_id))
    data=cursor.fetchall()
    appliance_details=[]
    app_room_contribute=[]
    units=[]
    for j in range(len(data)):
        e=[]
        e.append(data[j][0])
        e.append(data[j][1])
        e.append(data[j][2]*30)
        units.append(data[j][2]*30)
        app_room_contribute.append(data[j][2]*30)
        e.append(data[j][3])
        appliance_details.append(e)

    ##print("Appliance Details: ",appliance_details)
    ##print("Units: ",units)

    units_room=[]
    for k in range(len(data)):
        e=[]
        e.append(data[k][0])
        e.append(data[k][1])
        e.append(data[k][2]*30)
        units_room.append(e)

    ##for l in range(len(units_room)):
    ##    print("Units room: ",units_room[l])

    sum_appliances=sum(units)
    app_percent=[]

    for i in range(len(units_room)):
        e=[]
        temp=(units_room[i][-1]/sum_appliances)*100
        e.append(units_room[i][0])
        e.append(units_room[i][1])
        e.append(temp)
        app_percent.append(e)
    recommend_list=[]    

    for i in range(len(app_percent)):
        e=[]
        temp=reduction*(app_percent[i][-1]/100)
        e.append(app_percent[i][0])
        e.append(app_percent[i][1])
        e.append(temp)
        recommend_list.append(e)    

    for i in range(len(recommend_list)):
        units=recommend_list[i][-1]
        app_type=recommend_list[i][1]
        if(app_type=="light"):
            hours=units/11.40
        if(app_type=="television"):
            hours=units/10        
        if(app_type=="fan"):
            hours=units/16.40        
        if(app_type=="Air conditioner"):
            hours=units/0.68        
        if(app_type=="washing machine"):
            hours=units/3        
        if(app_type=="heater"):
            hours=units/0.68
        if(app_type=="Computer"):
            hours=units/8.25
        if(app_type=="refrigirator"):
            hours=units/10        
        if(app_type=="motor"):
            hours=units/1.25        
        if(app_type=="iron box"):
            hours=units/1.25
        recommend_list[i].append(hours)
        temp=math.modf(hours)
        hours_str=''
        if(temp[1]==0):
            h=temp[0]*60
            hours_str=str(int(h))+"mins"
        else:
            h=temp[0]*60
            hours_str=str(int(temp[1]))+"hours "+str(int(h))+"mins"
        recommend_list[i].append(hours_str)   
    for i in range(len(recommend_list)):
        cursor.execute("INSERT INTO recommendation_message (meterId,room_name,appliance_type,reduction_units,time_float,hours) values(%d,'%s','%s',%f,%f,'%s')"%(meter_id,recommend_list[i][0],recommend_list[i][1],recommend_list[i][2],recommend_list[i][3],recommend_list[i][4]))

def cost_calculation_predicted(predicted_value):
    # calculate cost
    cost = 0
    if(predicted_value < 500):
        cost = predicted_value*1.5
    elif(predicted_value > 500):
        cost = predicted_value*3.0
    return cost


def room_wise_calculation_predicted(meter_id,predicted_value,month):
    # calculate room wise data
    # query to insert data
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute("SELECT room_name,use_percentage,max_limit from room_calculations where meterId=%d"%(meter_id))
    room_data=cursor.fetchall()
    room_name=[]
    room_percentage=[]
    room_maxlimit=[]

    for i in range(len(room_data)):
        room_name.append(room_data[i][0])
        room_percentage.append(room_data[i][1])
        room_maxlimit.append(room_data[i][2])
    
    predicted_units=[]
    for i in room_percentage:
        k=predicted_value*(i/100)
        predicted_units.append(k)

    for i in range(len(room_name)):
        cursor.execute("INSERT INTO room_wise (meterId,month_date,name,current_units,predicted_units,max_pred_units,month) values(%d,'%s','%s',%d,%d,%d,'%s')"%(meter_id,month,room_name[i],0,predicted_units[i],room_maxlimit[i],month))

    return 1

# def room_wise_calculation_predicted(predicted_value):
#     #calculate room wise data
#     pred_arr[]
#     total_rooms=len(sum_arr)
#     for i in perd_arr:
#         k=predicted_value*(i/100)
#         pred_arr.append(k)
#     print(pred_arr)

app.run(host='0.0.0.0', port=8090)
