from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from functools import wraps
from db_create import db, application
from models import *

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('login'))
	return wrap

@application.route('/', methods=['GET','POST'])
@login_required
def home():
	if request.method == 'POST':
		report_type = request.form['report_type']
		acct = request.form['account']
		dt = request.form['date_type']
		if (report_type == 'trader_conf'):
			return redirect(url_for('trconfreport', account=acct, date=dt))
		else:
			return redirect(url_for('plreport', account=acct, date=dt))
	else:	
		if 'logged_in' in session:
			logged_user = db.session.query(User).filter(User.user_id == session['user_id']).first()
			accountsList = logged_user.accounts

			return render_template("index.html", accounts=accountsList)
		else:
			return redirect(url_for('login'))

@application.route('/index')
def main_page():
	return redirect(url_for('home'))

@application.route('/about')
def about():
	return render_template("about.html")

@application.route('/plreport/<account>/<date>')
@login_required
def plreport(account, date):
	current_time = datetime.utcnow()
	if date == "today":
		minutes_to_sub = datetime.today().minute
		hours_to_sub = datetime.today().hour
		begin_today = current_time - timedelta(minutes=minutes_to_sub)
		begin_today = begin_today - timedelta(hours=hours_to_sub)
		time_period = "Period between " + begin_today + " and "+current_time

		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < begin_today).all()

	if date == "yesterday":
		one_day_ago = current_time - timedelta(days=1)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < one_day_ago).all()
		time_period = "Period between " + one_day_ago + " and " + current_time ##needs to be corrected

	if date == "this_month":
		day_of_the_month = datetime.today().day
		x_days_ago = current_time - timedelta(days=day_of_the_month)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < x_days_ago).all()
		time_period = "Period between " + str(x_days_ago) + " and " + str(current_time)

	if date == "prev_month":
		day_of_the_month = datetime.today().day
		last_month_end = current_time - timedelta(days=day_of_the_month)
		last_month_begin = last_month_end - timedelta(days=30)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_month_begin, Transaction.trade > last_month_end).all() 
		time_period = "Period between " + last_month_begin + " and " + last_month_end

	if date == "this_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		sub_days = current_time - timedelta(days=day_of_the_month)
		sub_months = sub_days - timedelta(days=30*month_of_the_year)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < sub_months).all()
		time_period = "Period between " + sub_months + " and " + current_time

	if date == "last_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		sub_days = current_time - timedelta(days=day_of_the_month)
		last_year_end = sub_days - timedelta(days= 30*month_of_the_year)
		last_year_begin = last_year_end - timedelta(weeks=52)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade < last_year_begin, Transaction.trade > last_year_end).all()
		time_period = "Period between " + last_year_begin + " and " + last_year_end

	stock_dict = {}
	stock_names = []
	num_trades = len(transactionList)
	grand_total = 0

	for item in transactionList:
		initSymb = item.sec_sym.partition(' ')[0]
		if initSymb in stock_dict:
			pass
		else:
			stock_names.append(initSymb)
			itemTotal = 0;
			for itemz in transactionList:
				symb = itemz.sec_sym.partition(' ')[0]
				if symb == initSymb:
					commish = itemz.commission
					units = itemz.units
					broker_fee = commish*units
					SEC_fee = 0
					if itemz.buy_sell == "s":
						SEC_fee = units*itemz.price
					# print symb +" and "+ initSymb
					itemTotal += SEC_fee + broker_fee; ##Need to add exchange fee
					grand_total +=itemTotal
			stock_dict[initSymb] = itemTotal

	# print(stock_dict)

	return render_template('plreport.html', totalProfit=grand_total, numTrades= num_trades, list=stock_names, dict=stock_dict, period = time_period)

@application.route('/trconfreport/<account>/<date>')
@login_required
def trconfreport(account, date):
	print account
	print date
	transactionList = db.session.query(Transaction).filter(Transaction.account_id == account).all()

	return render_template("traderconfreport.html", list=transactionList)

@application.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		user = db.session.query(User).filter(User.email == request.form['email'], User.password == request.form['password']).first()
		if user:
			session['logged_in'] = True
			session['user_id'] = user.user_id
			session['admin'] = user.admin
			return redirect(url_for('home'))
		else:
			error = 'Invalid Credentials. Please try again.'
	return render_template("login.html", error=error)

@application.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('user_id', None)
	session.pop('admin', None)
	flash('You were just logged out!')
	return redirect(url_for('home'))

@application.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		if  request.form['name'] != None and request.form['email'] != None and request.form['password'] != None and request.form['password'] == request.form['confirm_password']:

			req_name = request.form['name']
			req_email = request.form['email'] 
			req_password = request.form['password']

			new_user = User(req_email, req_password, req_name, False)
			db.session.add(new_user)
			db.session.commit()

			return redirect(url_for('home'))
		else:
			session['logged_in'] = True
			flash('You were just logged in!')
			return redirect(url_for('home'))

	return render_template("register.html")

@application.route('/adminpage', methods=['GET', 'POST'])
@login_required
def adminpage():
	if request.method == 'GET':
		accountsList = db.session.query(Account).all()
		allUsers = db.session.query(User).all()
		nonAdmins = db.session.query(User).filter(User.admin == False).all()
		return render_template("adminpage.html", accounts=accountsList, 
			allUsers=allUsers, nonAdmins=nonAdmins)
	else:
		if request.form['button'] == "Set as Admins":
			new_admins = request.form.getlist('new_admins')
			print new_admins
			for new_id in new_admins:
				db.session.query(User).filter(User.user_id == new_id).update({User.admin: True})
				db.session.commit()
			return redirect(url_for('home'))
		elif request.form['button'] == "Associate Accounts":
			user_assoc = request.form['user_adding_to']
			accounts_adding = request.form.getlist('accounts_adding')
			for acct_id in accounts_adding:
				acct_obj = db.session.query(Account).filter(Account.account_id == acct_id).first()
				selected_user = db.session.query(User).filter(User.user_id == user_assoc).first()
				if acct_obj not in selected_user.accounts:
					selected_user.accounts.append(acct_obj)
					db.session.commit()
			return redirect(url_for('home'))
		elif request.form['button'] == "Create Account":
			acct_name = request.form['new_account_name']
			acct_initials = request.form['new_account_initials']
			new_acct = Account(acct_name, acct_initials)
			db.session.add(new_acct)
			db.session.commit()
			return redirect(url_for('home'))

@app.route('/_get_transactions')
def get_transactions(account, stock_sym):
	transactionList = db.session.query(Transaction).filter(Transaction.account_id == account).all()

if __name__ == '__main__':
	application.run(debug=True)