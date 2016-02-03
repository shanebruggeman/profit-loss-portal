from flask import Flask, jsonify, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from db_create import db, application
from models import *
import calendar

def get_accounts_for_user(user_id):
	logged_user = db.session.query(User).filter(User.user_id == user_id).first()
	return logged_user.accounts

def get_transactions_for_date(account, date):
	current_time = datetime.utcnow() - timedelta(hours=5)
	transactionList = []
	positionList = []
	return_dict = {}
	if date == "today":
		minutes_to_sub = datetime.today().minute
		hours_to_sub = datetime.today().hour
		begin_today = current_time - timedelta(minutes=minutes_to_sub)
		begin_today = begin_today - timedelta(hours=hours_to_sub)
		time_period = "Period between " + str(begin_today).split(".")[0] + " and " + str(current_time).split(".")[0]
		positionList = StockPosition.query.filter(StockPosition.account_id == account, StockPosition.date < begin_today).all()
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < begin_today).all()

	elif date == "yesterday":
		one_day_ago = current_time - timedelta(days=1)
		time_period = "Period between " + str(one_day_ago).split(".")[0] + " and " + str(current_time).split(".")[0] ##needs to be corrected
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < one_day_ago).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date > one_day_ago).all()

	elif date == "this_month":
		day_of_the_month = datetime.today().day
		x_days_ago = current_time - timedelta(days=day_of_the_month-1)
		time_period = "Period between " + str(x_days_ago).split(".")[0] + " and " + str(current_time).split(".")[0]
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < x_days_ago).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date > x_days_ago).all()

	elif date == "prev_month":
		day_of_the_month = datetime.today().day
		last_month_end = current_time - timedelta(days=day_of_the_month)
		if datetime.today().month==1:
			last_month_num = datetime.today().month+11
			last_year_num = datetime.today().year - 1
		last_month_begin = last_month_end - timedelta(days=calendar.monthrange(last_year_num, last_month_num)[1] -1)
		time_period = "Period between " + str(last_month_begin).split(".")[0] + " and " + str(last_month_end).split(".")[0]
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_month_begin, Transaction.trade > last_month_end).all() 
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date < last_month_begin, StockPosition.date > last_month_end).all()

	elif date == "this_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		days_to_sub = 0;
		for i in range(1,month_of_the_year):
			days_to_sub+= calendar.monthrange(datetime.today().year, i)[1]
		days_to_sub = days_to_sub - 1
		sub_days = current_time - timedelta(days=day_of_the_month)
		sub_months = sub_days - timedelta(days=days_to_sub)
		time_period = "Period between " + str(sub_months).split(".")[0] + " and " + str(current_time).split(".")[0]
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < sub_months).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date < sub_months).all()

	if date == "last_year":
		##Eff this ill do it tomorrow
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		days_to_sub = 0;
		days_to_sub_this_year = 0;
		for i in range(1, 13):
			days_to_sub+= calendar.monthrange(datetime.today().year-1, i)[1]

		if month_of_the_year == 1:
			days_to_sub_this_year = datetime.today().day
		else:
			for j in range(1, month_of_the_year):
				days_to_sub_this_year+= calendar.monthrange(datetime.today().year, i)[1]
		days_to_sub = days_to_sub - 1
		sub_days = current_time - timedelta(days=days_to_sub_this_year)
		last_year_end = sub_days
		last_year_begin = last_year_end - timedelta(days_to_sub)
		time_period = "Period between " + str(last_year_begin).split(".")[0] + " and " + str(last_year_end).split(".")[0]
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_year_begin, Transaction.trade > last_year_end).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date < last_year_begin, StockPosition.date > last_year_end).all()

	for position in positionList:
		transactionList.extend(position.all_transactions)

	print positionList
	print transactionList

	return_dict['trans'] = transactionList
	return_dict['period'] = time_period

	return return_dict

def make_admin(new_admins):
	for new_id in new_admins:
		db.session.query(User).filter(User.user_id == new_id).update({User.admin: True})
		db.session.commit()

def associate_accounts_to_user(user_assoc, accounts_adding):
	for acct_id in accounts_adding:
		acct_obj = db.session.query(Account).filter(Account.account_id == acct_id).first()
		selected_user = db.session.query(User).filter(User.user_id == user_assoc).first()
		if acct_obj not in selected_user.accounts:
			selected_user.accounts.append(acct_obj)
			db.session.commit()

def get_transactions_for_chart(account, stock_sym):
	transactionList = db.session.query(Transaction).filter(Transaction.account_id == account).order_by(Transaction.settle).all()

	valueList = []
	labelList = []
	return_dict = {}

	for item in transactionList:
		initSymb = item.sec_sym.partition(' ')[0].lower()
		if (initSymb == stock_sym):
			price_x_unit = item.price * item.units
			valueList.append(price_x_unit)
			labelList.append(item.settle.strftime('%d %b %Y'))

	return_dict['values'] = valueList
	return_dict['labels'] = labelList

	return return_dict

def update_commission(acct_id, commission):
	db.session.query(Account).filter(Account.account_id == acct_id).update({Account.commission: commission})
	db.session.commit()