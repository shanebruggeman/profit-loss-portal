from flask import Flask, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from db_create import db, application
from models import *

def get_accounts_for_user(user_id):
	logged_user = db.session.query(User).filter(User.user_id == user_id).first()
	return logged_user.accounts

def get_transactions_for_date(account, date):
	current_time = datetime.utcnow() - timedelta(hours=4)
	transactionList = []
	if date == "today":
		minutes_to_sub = datetime.today().minute
		hours_to_sub = datetime.today().hour
		begin_today = current_time - timedelta(minutes=minutes_to_sub)
		begin_today = begin_today - timedelta(hours=hours_to_sub)
		time_period = "Period between " + str(begin_today) + " and " + str(current_time)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < begin_today).all()

	elif date == "yesterday":
		one_day_ago = current_time - timedelta(days=1)
		time_period = "Period between " + str(one_day_ago) + " and " + str(current_time) ##needs to be corrected
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < one_day_ago).all()
		
	elif date == "this_month":
		day_of_the_month = datetime.today().day
		x_days_ago = current_time - timedelta(days=day_of_the_month)
		time_period = "Period between " + str(x_days_ago) + " and " + str(current_time)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < x_days_ago).all()
		
	elif date == "prev_month":
		day_of_the_month = datetime.today().day
		last_month_end = current_time - timedelta(days=day_of_the_month)
		last_month_begin = last_month_end - timedelta(days=30)
		time_period = "Period between " + str(last_month_begin) + " and " + str(last_month_end)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_month_begin, Transaction.trade > last_month_end).all() 
		
	elif date == "this_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		sub_days = current_time - timedelta(days=day_of_the_month)
		sub_months = sub_days - timedelta(days=30*month_of_the_year)
		time_period = "Period between " + str(sub_months) + " and " + str(current_time)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < sub_months).all()
		
	if date == "last_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		sub_days = current_time - timedelta(days=day_of_the_month)
		last_year_end = sub_days - timedelta(days= 30*month_of_the_year)
		last_year_begin = last_year_end - timedelta(weeks=52)
		time_period = "Period between " + str(last_year_begin) + " and " + str(last_year_end)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_year_begin, Transaction.trade > last_year_end).all()
		
	return transactionList