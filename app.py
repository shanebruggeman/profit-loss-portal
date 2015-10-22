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

		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > begin_today).all()
	if date == "yesterday":
		one_day_ago = current_time - timedelta(days=1)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > one_day_ago ).all()

	if date == "this_month":
		day_of_the_month = datetime.today().day
		x_days_ago = current_time - timedelta(days=day_of_the_month)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > x_days_ago).all()

	if date == "prev_month":
		day_of_the_month = datetime.today().day
		last_month_end = current_time - timedelta(days=day_of_the_month)
		last_month_begin = last_month_end - timedelta(days=30)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.entry > last_month_begin, Transaction.trade < last_month_end).all() 
	
	if date == "this_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		sub_days = current_time - timedelta(days=day_of_the_month)
		sub_months = sub_days - timedelta(days=30*month_of_the_year)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.settle > sub_months).all()
	
	if date == "last_year":
		day_of_the_month = datetime.today().day
		month_of_the_year = datetime.today().month
		sub_days = current_time - timedelta(days=day_of_the_month)
		last_year_end = sub_days - timedelta(days= 30*month_of_the_year)
		last_year_begin = last_year_end - timedelta(weeks=52)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > last_year_begin, Transaction.trade < last_year_end).all()
	print transactionList
	print db.session.query(Transaction).filter(Transaction.account_id == account).all()
	return render_template('plreport.html', list=transactionList)

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

if __name__ == '__main__':
	application.run(debug=True)