from flask import Flask, jsonify, flash, redirect, render_template, request, session, abort
import os
import pymysql as MySQLdb
import json
from datetime import datetime
from waitress import serve

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Smart Meter Login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():    
    data1 = request.form.to_dict()    
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    dat = {'status': '0', 'error': 'null'}
    cursor = db.cursor()
    cursor.execute("select meterId,password,new_user from login")
    data = cursor.fetchall()
    meter_id = int(data1['meter_id'])
    password = str(data1['user_pass'])
    # new_user=int(data[])
    if(meter_id, password, 1)in data:
        dat['status'] = '1'
        dat['error'] = 'Login Successful'
        session['meter_id'] = meter_id
        db.close()
        return jsonify(result=dat)
    elif(meter_id, password, 0) in data:
        dat['status'] = '2'
        dat['error'] = 'Login Successful'
        session['meter_id'] = meter_id
        db.close()
        return jsonify(result=dat)
    else:
        dat['status'] = '0'
        dat['error'] = 'Invalid Login Details'
        db.close()
        return jsonify(result=dat)


@app.route('/getMonthDetails', methods=["POST", "GET"])
def getMonthDetails():
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    meter_id = session['meter_id']
    cursor.execute("select `units`,`month_date`,`rooms`,`max_limit`,`cost`,`pred_units`,`pred_cost` from month_wise,login where login.meterId=month_wise.meterId and month_wise.meterId = '%d' order by month_date desc" % (meter_id))
    data = cursor.fetchall()
    to_send = []
    for row in data:
        date = row[1]
        date = date.strftime('20%y-%m-%d')
        to_send.append({'units': row[0], 'month': date, 'rooms': row[2], 'max_units': row[3],
                        'cost': row[4], 'predicted_units': row[5], 'predicted_cost': row[6]})

    month_val=to_send[0]['month']
    cursor.execute("select `units_date` from date_wise,login where (Month('%s') = Month(date)) and login.meterId=date_wise.meterId and date_wise.meterId = %d" % (month_val, meter_id))
    date_list=cursor.fetchall()

    date_sum=0
    for i in date_list:
        date_sum+=i[0]

    cursor.execute("SELECT room_name,use_percentage,max_limit from room_calculations where meterId=%d"%(meter_id))
    room_data=cursor.fetchall()
    room_name=[]
    room_percentage=[]
    room_maxlimit=[]
    room_units=[]
    
    for i in range(len(room_data)):
        room_name.append(room_data[i][0])
        room_percentage.append(room_data[i][1])
        room_maxlimit.append(room_data[i][2])
    
    for h in room_percentage:
        units_forappliance= (h/100)*date_sum
        room_units.append(units_forappliance)
    
    length_1=len(room_percentage)

    for i in range(length_1):
        if room_units[i]>room_maxlimit[i]:
            notify_3=room_name[i]+" maximum limit has exceeded.There might be a leakage or overusage"
            cursor.execute("INSERT INTO notification_message (meterId,message,status) values(%d,'%s',%d)"%(meter_id,notify_3,0))  

            # cursor.execute("SELECT room_name,appliance_type,units_per_day,room_app_percentage FROM room_appliance where meterId=%d ORDER BY id"%(meter_id))
            # data=cursor.fetchall()
            # appliance_details=[]
            # for j in range(len(data)):
            #     e=[]
            #     e.append(data[j][0])
            #     e.append(data[j][1])
            #     e.append(data[j][2]*30)
            #     e.append(data[j][3])
            #     appliance_details.append(e)
            
    # if to_send[0]['max_units']<=date_sum:
    #     roomwise_units=[]
    #     for i in range(len(room_name)):
    #         room_current=date_sum*(room_percentage[i]/100)
    #         roomwise_units.append(room_current)
            
        # notify="the max value has exceeded"
        # cursor.execute("INSERT INTO notification_message (meterId,message,status) values(%d,'%s',%d)"%(meter_id,notify,0))    
    return jsonify(result=to_send)


@app.route('/getDateDetails', methods=["POST", "GET"])
def getDateDetails():
    db = MySQLdb.connect("localhost", "root", "", "e_meter")    
    cursor = db.cursor()
    post = request.get_json()
    month = post.get('month')
    month_val = str(month)
    meter_id = session['meter_id']
    cursor.execute(
        "select `date`,`units_date`,`max_units_date` from date_wise,login where (Month('%s') = Month(date)) and login.meterId=date_wise.meterId and date_wise.meterId = %d" % (month_val, meter_id))
    data = cursor.fetchall()
    to_send = []
    for row in data:
        date = row[0]
        date = date.strftime('20%y-%m-%d')
        to_send.append({'date': date, 'units': row[1], 'max_units': row[2]})
    return jsonify(result=to_send)


@app.route('/getRoomDetails', methods=["POST", "GET"])
def getRoomDetails():
    post = request.get_json()
    month = post.get('month')
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    meter_id = session['meter_id']
    month_val = str(month)
    cursor.execute("select `name`,`current_units`,`predicted_units`,`max_pred_units` from room_wise,login where login.meterId=room_wise.meterId and room_wise.meterId = %d and room_wise.month_date= '%s'" % (meter_id, month_val))
    data = cursor.fetchall()

    #data=(('Bedroom1', 0, 143.0, 150.0), ('Bedroom2', 0, 102.0, 110.0), ('Hall', 0, 188.0, 190.0), ('Misc', 0, 116.0, 120.0))
    to_send = []
    
    cursor.execute("SELECT room_name,use_percentage,max_limit from room_calculations where meterId=%d"%(meter_id))
    room_data=cursor.fetchall()
    room_name=[]
    room_percentage=[]
    room_maxlimit=[]
    
    for i in range(len(room_data)):
        room_name.append(room_data[i][0])
        room_percentage.append(room_data[i][1])
        room_maxlimit.append(room_data[i][2])

    cursor.execute(
        "select `units_date` from date_wise,login where (Month('%s') = Month(date)) and login.meterId=date_wise.meterId and date_wise.meterId = %d" % (month_val, meter_id))
    date_list=cursor.fetchall()

    date_sum=0
    for i in date_list:
        date_sum+=i[0]

    room_units=[]
    for i in room_percentage:
        k=date_sum*(i/100)
        room_units.append(k)        

    for row in data:
        to_send.append({'name': row[0], 'current_units': row[1],
                        'predicted_units': row[2], 'max_pred_units': row[3]})

    for i in range(len(room_name)):
        to_send[i]['current_units']=room_units[i]
    # print(to_send)
    return jsonify(result=to_send)


@app.route('/changePassword', methods=["POST", "GET"])
def changePassword():
    post = request.get_json()
    current = str(post.get('current'))
    meter_id = session['meter_id']
    new = str(post.get('new'))
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute(
        "select `meterId`,`password` from login where login.meterId = %d " % (meter_id))
    data = cursor.fetchall()
    to_send = {'status': '0', 'error': 'null'}
    db_current_pass = data[0][1]
    if(current != db_current_pass):
        to_send["status"] = "0"
        to_send["error"] = "Current Password doesn't match!"
        return jsonify(result=to_send)
    else:
        cursor.execute(
            "update `login` set `password`='%s' where meterId=%d" % (new, meter_id))
        to_send["status"] = "1"
        to_send["error"] = "Password Changed Successfully!"
        return jsonify(result=to_send)


@app.route('/previousMonths', methods=["POST", "GET"])
def previousMonths():
    post = request.get_json()
    month1 = int(post.get('month1'))
    month2 = int(post.get('month2'))
    month3 = int(post.get('month3'))
    month4 = int(post.get('month4'))
    month5 = int(post.get('month5'))
    month6 = int(post.get('month6'))
    month_val1 = str(post.get('month_val1'))
    month_val2 = str(post.get('month_val2'))
    month_val3 = str(post.get('month_val3'))
    month_val4 = str(post.get('month_val4'))
    month_val5 = str(post.get('month_val5'))
    month_val6 = str(post.get('month_val6'))
    
    current_month=int(month_val1[0:2])+1
    current_month= month_val1[3:7]+"-"+str(current_month)+"-"+"01"

    month_val1 = month_val1[3:7]+"-"+month_val1[0:2]+"-"+"01"
    month_val2 = month_val2[3:7]+"-"+month_val2[0:2]+"-"+"01"
    month_val3 = month_val3[3:7]+"-"+month_val3[0:2]+"-"+"01"
    month_val4 = month_val4[3:7]+"-"+month_val4[0:2]+"-"+"01"
    month_val5 = month_val5[3:7]+"-"+month_val5[0:2]+"-"+"01"
    month_val6 = month_val6[3:7]+"-"+month_val6[0:2]+"-"+"01"    

    meter_id = session['meter_id']
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    to_send = {'status': '0', 'error': 'null'}

    # cursor.execute("SELECT room_name FROM room_appliance where meterId=%d"%(meter_id))
    # meter_data=cursor.fetchall()
    # if(len(meter_data)!=0):
    #     to_send["status"] = "1"
    #     to_send["error"] = "Data Updated Successfully!"
    #     return jsonify(result=to_send)
    # previous_month table
    cursor.execute("INSERT INTO previous_months (meterId, month, units) VALUES(%d, '%s', '%s')" % (
        meter_id, month_val1, month1))
    cursor.execute("INSERT INTO previous_months (meterId, month, units) VALUES(%d, '%s', '%s')" % (
        meter_id, month_val2, month2))
    cursor.execute("INSERT INTO previous_months (meterId, month, units) VALUES(%d, '%s', '%s')" % (
        meter_id, month_val3, month3))
    cursor.execute("INSERT INTO previous_months (meterId, month, units) VALUES(%d, '%s', '%s')" % (
        meter_id, month_val4, month4))
    cursor.execute("INSERT INTO previous_months (meterId, month, units) VALUES(%d, '%s', '%s')" % (
        meter_id, month_val5, month5))
    cursor.execute("INSERT INTO previous_months (meterId, month, units) VALUES(%d, '%s', '%s')" % (
        meter_id, month_val6, month6))
    # month_wise table
    month1_cost = calculate_cost(int(month1))
    month2_cost = calculate_cost(int(month2))
    month3_cost = calculate_cost(int(month3))
    month4_cost = calculate_cost(int(month4))
    month5_cost = calculate_cost(int(month5))
    month6_cost = calculate_cost(int(month6))

    cursor.execute(
        "Select room_name from room_calculations where meterId=%d" % (meter_id))
    rooms = cursor.fetchall()
    no_of_rooms = len(rooms)

    cursor.execute(
        "Select max_limit from room_calculations where meterId=%d" % (meter_id))
    max_limit_list=cursor.fetchall()

    max_limit=0

    for i in range(no_of_rooms):       
        max_limit+=max_limit_list[i][0]

    #month_wise table previous month
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, month_val6, month6, no_of_rooms, max_limit, month6_cost, 0, 0))
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, month_val5, month5, no_of_rooms, max_limit, month5_cost, 0, 0))
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, month_val4, month4, no_of_rooms, max_limit, month4_cost, 0, 0))
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, month_val3, month3, no_of_rooms, max_limit, month3_cost, 0, 0))  
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, month_val2, month2, no_of_rooms, max_limit, month2_cost, 0, 0))
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, month_val1, month1, no_of_rooms, max_limit, month1_cost, 0, 0))
    
    #month_wise table previous month

    to_send["status"] = "1"
    to_send["error"] = "Data Updated Successfully!"
    previous_month = [month1, month2, month3, month4, month5, month6]
    predicted_value=previous_month_prediction(previous_month)
    predicted_cost=calculate_cost(predicted_value)
    #month_wise table next month
    cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
        meter_id, current_month, 0, no_of_rooms, max_limit, 0, predicted_value, predicted_cost))
    #month_wise table next month
    return jsonify(result=to_send)


def previous_month_prediction(previous_month):
    predicted_value = 0
    # prediction code
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    consumed = previous_month
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
    return predicted_value
    # predicted_cost = calculate_cost(n)
    # # query to upload the predicted value and cost
    # db = MySQLdb.connect("localhost", "root", "", "e_meter")
    # cursor = db.cursor()
    # cursor.execute(
    #     "SELECT `id`,`meterId`,`month_date` FROM month_wise ORDER BY id DESC LIMIT 1;")
    # data = cursor.fetchall()
    # cursor.execute("INSERT INTO month_wise (meterId,month_date,units,rooms,max_limit,cost,pred_units,pred_cost)values(%d,'%s',%d,%d,%d,%d,%d,%d)" % (
    #     meter_id, month_val6+"-01", month6, no_of_rooms, max_limit, month6_cost, 0, 0))

def calculate_cost(predicted_value):
    # cost calculation code
    if(predicted_value < 500):
        cost = predicted_value*1.5
    elif(predicted_value > 500):
        cost = predicted_value*3.0
    return cost

@app.route('/showModify', methods=["POST", "GET"])
def showModify():
    return render_template("ChangeApplianceDetails.html")
@app.route('/roomWiseCalculation', methods=["POST", "GET"])
def roomWiseCalculation():
    sum1 = 0
    unit_app = 0.0
    sum_arr = []
    post = request.get_json()
    d = dict(post.get('room_details'))
    # print(d)

    room_name = []
    for j in d.values():
        room_name.append(j["name"])

    for i in d.values():
        flag = 0
        sum1 = 0
        for j in i.values():
            if(flag == 0):
                flag = 1
                continue
            if(j["type"] == "fan"):
                unit_app = int(j["hours"])/16.40
                #print(str(unit_app)+"  fan")
                sum1 = sum1+unit_app
            if(j["type"] == "light"):
                unit_app = int(j["hours"])/11.40
                #print(str(unit_app)+"  light")
                sum1 = sum1+unit_app
            if(j["type"] == "Air conditioner"):
                unit_app = float(j["hours"])/0.68
                #print(str(unit_app)+"  AC")
                sum1 = sum1+unit_app
            if(j["type"] == "washing machine"):
                unit_app = float(j["hours"])/3
                # print(str(unit_app)+"wm")
                sum1 = sum1+unit_app
            if(j["type"] == "iron box"):
                unit_app = float(j["hours"])/1.25
                #print(str(unit_app)+"  ir box")
                sum1 = sum1+unit_app
            if(j["type"] == "heater"):
                unit_app = float(j["hours"])/0.68
                #print(str(unit_app)+"  heater")
                sum1 = sum1+unit_app
            if(j["type"] == "television"):
                unit_app = float(j["hours"])/10
                #print(str(unit_app)+"  heater")
                sum1 = sum1+unit_app
            if(j["type"] == "refrigerator"):
                unit_app = float(j["hours"])/10
                #print(str(unit_app)+"  heater")
                sum1 = sum1+unit_app
            if(j["type"] == "Computer"):
                unit_app = float(j["hours"])/8.25
                #print(str(unit_app)+"  heater")
                sum1 = sum1+unit_app
            if(j["type"] == "motor"):
                unit_app = float(j["hours"])/1.25
                #print(str(unit_app)+"  heater")
                sum1 = sum1+unit_app

        sum_arr.append(sum1)
    s = sum(sum_arr)
    max_limit = s*30
    max_limit_room = []
    for i in sum_arr:
        max_limit_room.append(i*30)
    room_percentage = []
    for i in sum_arr:
        room_percentage.append((i/s)*100)
        #print((i/s)*100, "%")
    to_send = {'status': '0', 'error': 'null'}
    to_send["status"] = "1"
    to_send["error"] = "Data Updated Successfully!"

    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()

    rooms = len(room_name)
    meter_id = session['meter_id']

    ########Maathanum#############

    # cursor.execute("Select meterId from room_calculations")
    # data=cursor.fetchall()
    
    for i in range(rooms):
        cursor.execute("insert into room_calculations(meterId,room_name,`use_percentage`,max_limit)values(%d,'%s',%f,%f);" % (meter_id, room_name[i], room_percentage[i],max_limit_room[i]))

    #room_appliance query
    room_details=[]
    for i in range(1,len(d)+1):
        room_name=d['room'+str(i)]['name']	
        for j in range(1,len(d['room'+str(i)])):
            app_details=[]
            app_type=d['room'+str(i)]['appliance'+str(j)]['type']
            app_hours=d['room'+str(i)]['appliance'+str(j)]['hours']
            app_details.append(room_name)
            app_details.append(app_type)
            app_details.append(app_hours)
            if(app_type=="fan"):
                unit_app = int(app_hours)/16.40
            if(app_type=="light"):
                unit_app = int(app_hours)/11.40
            if(app_type=="Air conditioner"):
                unit_app = int(app_hours)/0.68
            if(app_type=="washing machine"):
                unit_app = int(app_hours)/3
            if(app_type=="iron box"):
                unit_app = float(app_hours)/1.25
            if(app_type=="heater"):
                unit_app = float(app_hours)/0.68
            if(app_type=="television"):
                unit_app = int(app_hours)/10
            if(app_type=="refrigerator"):
                unit_app = int(app_hours)/10
            if(app_type=="Computer"):
                unit_app = int(app_hours)/8.25
            if(app_type=="motor"):
                unit_app = int(app_hours)/1.25
            
            unit_app_month=unit_app*30
            unit_app_percent=(unit_app_month/max_limit_room[i-1])*100
            app_details.append(unit_app)
            app_details.append(unit_app_percent)
            room_details.append(app_details)    

    for i in range(len(room_details)):
        cursor.execute("INSERT INTO room_appliance (meterId,room_name,appliance_type,hours,units_per_day,room_app_percentage) values(%d,'%s','%s',%f,%f,%f)"%(meter_id,room_details[i][0],room_details[i][1],float(room_details[i][2]),room_details[i][3],room_details[i][4]))
        print(room_details[i])        
        # print("INSERT INTO room_appliance (meterId,room_name,appliance_type,hours,units_per_day,room_app_percentage) values(%d,'%s','%s',%f,%f,%f)"%(meter_id,room_details[i][0],room_details[i][1],float(room_details[i][2]),room_details[i][3],room_details[i][4]))
    #room_appliance query
    return jsonify(result=to_send)

@app.route('/getNotificationCount', methods=["POST", "GET"])
def getChangeNotification():
    meter_id=session['meter_id']
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute("SELECT message from notification_message where meterId=%d and status=0"%(meter_id))
    data=cursor.fetchall()    
    #cursor.execute("UPDATE notification_message SET status=1 where meterId=%d and status=0"%(meter_id))    
    message=[]    
    for i in data:
        message.append({"message":i[0]})
    return jsonify(result=message)


@app.route('/getNotification', methods=["POST", "GET"])
def getNotification():
    meter_id=session['meter_id']
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute("SELECT message from notification_message where meterId=%d"%(meter_id))
    data=cursor.fetchall()
    cursor.execute("UPDATE notification_message SET status=1 where meterId=%d and status=0"%(meter_id))
    message=[]
    for i in data:
        message.append({"message":i[0]})
    return jsonify(result=message)

@app.route('/getRecommendationCount', methods=["POST", "GET"])
def getRecommendationCount():
    cnow = datetime.datetime.now()
    cmonth=str(cnow.date())        
    count=[{"count":1}]
    return jsonify(result=count)


@app.route('/getRecommendation', methods=["POST", "GET"])
def getRecommendation():
    meter_id=session['meter_id']
    db = MySQLdb.connect("localhost", "root", "", "e_meter")
    cursor = db.cursor()
    cursor.execute("SELECT room_name,appliance_type,reduction_units,hours from recommendation_message where meterId=%d ORDER BY id"%(meter_id))
    data=cursor.fetchall()    
    message=[]    
    for i in range(len(data)):
	    message.append({'room_name':str(data[i][0]),'appliance_type':str(data[i][1]),'reduction_units':str(data[i][2]),'hours':str(data[i][3])})
    return jsonify(result=message)

@app.route('/load_user_login')
def load_user_login():
    return render_template('UserApplianceDetails.html')


@app.route('/load_user_details')
def load_user_details():
    return render_template('Smart Meter UserLogin.html')


@app.route('/change_password')
def change_password():
    return render_template('ChangePassword.html')


@app.route('/previous_usage')
def previous_usage():
    return render_template('MonthlyUsageDetails.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    #serve(app, host='0.0.0.0', port=8080)
    app.run(threaded=True,debug=True)