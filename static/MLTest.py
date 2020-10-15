from flask import Flask, jsonify, flash, redirect, render_template, request, session, abort
import os
import pymysql as MySQLdb
import json
from datetime import datetime

import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('Smart Meter Login.html')


@app.route("/output")
def output():    
    db = MySQLdb.connect("localhost", "root", "", "user")    
    cursor = db.cursor()    
    cursor.execute("select id,name,age from userde")    
    data = cursor.fetchall()    
    db.close()
    return jsonify(data)


@app.route('/login', methods=['POST','GET'])
def login():	
	data1=request.form.to_dict()		
	db = MySQLdb.connect("localhost", "root", "", "e_meter")
	dat = {'status': '0', 'error': 'null'}	
	cursor = db.cursor()	
	cursor.execute("select meterId,password from login")	
	data = cursor.fetchall()	
	n = int(data1['meter_id'])
	p = str(data1['user_pass'])	
	if(n, p)in data:			
		dat['status']='1'
		dat['error']='Login Successful'	
		session['meter_id']=n				
		db.close()
		return jsonify(result=dat)
	else:		
		dat['status']='0'
		dat['error']='Invalid Login Details'			
		db.close()
		return jsonify(result=dat)
	
@app.route('/getMonthDetails', methods=["POST","GET"])
def getMonthDetials():
	db = MySQLdb.connect("localhost", "root", "", "e_meter")
	cursor = db.cursor()
	meter_id=session['meter_id']	
	cursor.execute("select `units`,`month_date`,`rooms`,`max_limit`,`cost`,`pred_units`,`pred_cost` from month_wise,login where login.meterId=month_wise.meterId and month_wise.meterId = '%d'"%(meter_id))
	data=cursor.fetchall()
	to_send=[]
	for row in data:
		date=row[1]
		date=date.strftime('20%y-%m-%d')
		to_send.append({'units': row[0], 'month': date,'rooms':row[2],'max_units':row[3],'cost':row[4],'predicted_units':row[5],'predicted_cost':row[6]})	
	return jsonify(result=to_send)

@app.route('/getDateDetails', methods=["POST","GET"])
def getDateDetails():
	db = MySQLdb.connect("localhost", "root", "", "e_meter")
	cursor = db.cursor()
	meter_id=session['meter_id']	
	cursor.execute("select `date`,`units_date`,`max_units_date` from date_wise,login where login.meterId=date_wise.meterId and date_wise.meterId = %d"%(meter_id))
	data=cursor.fetchall()
	to_send=[]
	for row in data:
		date=row[0]
		date=date.strftime('20%y-%m-%d')		
		to_send.append({'date': date, 'units':row[1],'max_units':row[2]})			
	return jsonify(result=to_send)

@app.route('/getRoomDetails', methods=["POST","GET"])
def getRoomDetails():
	data1=request.form.to_dict()	
	db = MySQLdb.connect("localhost", "root", "", "e_meter")
	cursor = db.cursor()
	meter_id=session['meter_id']	
	month_val=str(data1['month'])	
	cursor.execute("select `name`,`current_units`,`predicted_units`,`max_pred_units` from room_wise,login where login.meterId=room_wise.meterId and room_wise.meterId = %d and room_wise.month_date= '%s'"%(meter_id,month_val))
	data=cursor.fetchall()
	to_send=[]
	for row in data:			
		to_send.append({'name': row[0], 'current_units':row[1],'predicted_units':row[2],'max_pred_units':row[3]})		
	return jsonify(result=to_send)

@app.route('/load_user_login')
def load_user_login():
	return render_template('Smart Meter UserLogin.html')

@app.route('/load_user_details')
def load_user_details():
	return render_template('UserApplianceDetails.html')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run()
