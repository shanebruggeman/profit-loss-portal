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
			accountsList = db.session.query(Account).filter(Account.user_id == session['user_id']).all()

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
	return render_template('plreport.html')

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
	flash('You were just logged out!')
	return redirect(url_for('home'))

@application.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		if  request.form['name'] != None and request.form['email'] != None and request.form['password'] != None and request.form['password'] == request.form['confirm_password']:

			req_name = request.form['name']
			req_email = request.form['email'] 
			req_password = request.form['password']

			new_user = User(req_email, req_password, req_name)
			db.session.add(new_user)
			db.session.commit()

			return redirect(url_for('home'))
		else:
			session['logged_in'] = True
			flash('You were just logged in!')
			return redirect(url_for('home'))

	return render_template("register.html")

@application.route('/adminpage', methods=['GET', 'POST'])
def adminpage():
	accountsList = db.session.query(Account).all()
	return render_template("adminpage.html")

if __name__ == '__main__':
	application.run(debug=True)