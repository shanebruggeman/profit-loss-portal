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
	current_seconds = datetime.today().second
	current_minutes = datetime.today().minute
	current_hours = datetime.today().hour
	current_MDY = str(current_time.month)+"/"+str(current_time.day)+"/"+str(current_time.year)
	transactionList = []
	positionList = []
	return_dict = {}
	if date == "today":
		
		begin_today = current_time - timedelta(minutes=current_minutes) - timedelta(hours = current_hours-1) - timedelta(seconds=current_seconds)
		begin_MDY = str(begin_today.month)+"/"+str(begin_today.day)+"/"+str(begin_today.year) ##End date in m/d/y format
		time_period = "Period between " + begin_MDY + " and " + current_MDY
		positionList = StockPosition.query.filter(StockPosition.account_id == account, StockPosition.date < begin_today).all()
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < begin_today).all()

	elif date == "yesterday":
		one_day_ago = current_time - timedelta(days=1) - timedelta(minutes = current_minutes) - timedelta(hours=current_hours-1) - timedelta(seconds=current_seconds)
		end_MDY = str(one_day_ago.month) + "/" + str(one_day_ago.day) + "/" + str(one_day_ago.year)
		time_period = "Period between " + end_MDY + " and " + current_MDY ##needs to be corrected
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < one_day_ago).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date > one_day_ago).all()

	elif date == "this_month":
		day_of_the_month = datetime.today().day
		x_days_ago = current_time - timedelta(days=day_of_the_month-1) - timedelta(minutes=current_minutes) - timedelta(hours=current_hours-1) - timedelta(seconds=current_seconds)
		month_MDY = str(x_days_ago.month) + "/" + str(x_days_ago.day) + "/" + str(x_days_ago.year)
		time_period = "Period between " + month_MDY + " and " + current_MDY
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < x_days_ago).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date > x_days_ago).all()

	elif date == "prev_month":
		day_of_the_month = datetime.today().day
		last_month_end = current_time - timedelta(days=day_of_the_month)
		last_month_end_DMY = str(last_month_end.month) + "/" + str(last_month_end.day) + "/" + str(last_month_end.year)
		if datetime.today().month==1:
			last_month_num = datetime.today().month+11
			last_year_num = datetime.today().year - 1
		else:
			last_month_num = datetime.today().month-1
			last_year_num = datetime.today().year
		last_month_begin = last_month_end - timedelta(days=calendar.monthrange(last_year_num, last_month_num)[1] -1)
		last_month_begin_DMY = str(last_month_begin.month) + "/" + str(last_month_begin.day) + "/" + str(last_month_begin.year)
		time_period = "Period between " + last_month_begin_DMY + " and " + last_month_end_DMY
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_month_begin, Transaction.trade > last_month_end).all() 
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date < last_month_begin, StockPosition.date > last_month_end).all()

	elif date == "this_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		days_to_sub = 0;
		for i in range(1,month_of_the_year):
			days_to_sub+= calendar.monthrange(datetime.today().year, i)[1]
		days_to_sub = days_to_sub - 1
		sub_months = current_time - timedelta(days=day_of_the_month) - timedelta(days=days_to_sub) - timedelta(minutes = current_minutes) - timedelta(hours = current_hours-1) - timedelta(seconds=current_seconds)
		year_begin_DMY = str(sub_months.month) + "/" + str(sub_months.day) + "/" + str(sub_months.year)
		time_period = "Period between " + year_begin_DMY + " and " + current_MDY
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < sub_months).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date < sub_months).all()

	if date == "last_year":
		
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
		days_to_sub = days_to_sub-2
		sub_days = current_time - timedelta(days=days_to_sub_this_year) - timedelta(days=datetime.today().day-2) - timedelta(minutes = current_minutes) - timedelta(hours = current_hours-1) - timedelta(seconds=current_seconds)
		last_year_end = sub_days
		last_year_end_DMY = str(last_year_end.month) + "/" + str(last_year_end.day) + "/" + str(last_year_end.year)
		last_year_begin = last_year_end - timedelta(days_to_sub+1)
		last_year_begin_DMY = str(last_year_begin.month) + "/" + str(last_year_begin.day) + "/" + str(last_year_begin.year)
		time_period = "Period between " + last_year_begin_DMY + " and " + last_year_end_DMY
		# transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_year_begin, Transaction.trade > last_year_end).all()
		positionList = db.session.query(StockPosition).filter(StockPosition.account_id == account, StockPosition.date < last_year_begin, StockPosition.date > last_year_end).all()

	for position in positionList:
		transactionList.extend(position.all_transactions)

	# print positionList
	# print transactionList

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