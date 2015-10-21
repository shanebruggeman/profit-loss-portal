from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask.ext.sqlalchemy import SQLAlchemy
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
			accountsList = db.session.query(User).filter(User.user_id == session['user_id']).first().accounts

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
	current_time - datetime.datetime.utcnow()
	if date == "today":
		minutes_to_sub = datetime.datetime.today().minute
		hours_to_sub = datetime.datetime.today().hour
		begin_today = current_time - datetime.timedelta(minutes=minutes_to_sub)
		begin_today = begin_today - datetime.timedelta(hours=hours_to_sub)

		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > begin_today).all()
	if date == "yesterday":
		one_day_ago = current_time - datetime.timedelta(days=1)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > one_day_ago ).all()

	if date == "this_month":
		day_of_the_month = datetime.datetime.today().day
		x_days_ago = current_time - datetime.timedelta(days=day_of_the_month)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > x_days_ago).all()

	if date == "prev_month":
		day_of_the_month = datetime.datetime.today().day
		last_month_end = current_time - datetime.timedelta(days=day_of_the_month)
		last_month_begin = last_month_end - datetime.timedelta(months=1)
		transactionList = db.session.query(transaction).filter(transaction.account_id == account, Transaction.trade > last_month_begin, transaction.trade < last_month_end).all() 
	
	if date == "this_year":
		day_of_the_month = datetime.datetime.today().day
		month_of_the_year = datetime.datetime.today().month
		sub_days = current_time - datetime.timedelta(days=day_of_the_month)
		sub_months = sub_days - datetime.timedelta(months=month_of_the_year)
		transactionList = db.session.query(transaction).filter(transaction.account_id == account, Transaction.trade > sub_months).all()
	
	if date == "last_year":
		day_of_the_month = datetime.datetime.today().day
		month_of_the_year = datetime.datetime.today().month
		sub_days = current_time - datetime.timedelta(days=day_of_the_month)
		last_year_end = sub_days - datetime.timedelta(months=month_of_the_year)
		last_year_begin = last_year_end - datetime.timedelta(years=1)
		transactionList = db.session.query(Transaction).filter(Transaction.account_id == account, Transaction.trade > last_year_begin, Transaction.trade < last_year_end).all()
	return render_template('plreport.html', list=transactionList)

@application.route('/trconfreport/<account>/<date>')
@login_required
def trconfreport(account, date):

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
		usersList = db.session.query(User).filter(User.admin == False).all()
		return render_template("adminpage.html", accounts=accountsList, users=usersList)
	else:
		if request.form['button'] == "Set as Admins":
			new_admins = request.form.getlist('new_admins')
			print new_admins
			for new_id in new_admins:
				db.session.query(User).filter(User.user_id == new_id).update({User.admin: True})
				db.session.commit()
		return url_for('adminpage')
		

if __name__ == '__main__':
	application.run(debug=True)