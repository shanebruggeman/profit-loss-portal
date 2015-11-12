import os
from flask import Flask, render_template, jsonify, redirect, url_for, request, session, flash, g
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from datetime import datetime, date, timedelta
from functools import wraps
from db_create import db, application
from models import *
from viewmethods import *

UPLOAD_FOLDER = 'C:\\Users\\watersdr\\Documents\\GitHub\\profit-loss-portal\\file_uploads'
ALLOWED_EXTENSIONS = set(['txt'])
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('login'))
	return wrap

def admin_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'admin' in session:
			return f(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('home'))
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
			accountsList = get_accounts_for_user(session['user_id'])
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
	
	trans_and_time_period = get_transactions_for_date(account, date)

	transactionList = trans_and_time_period['trans']
	time_period = trans_and_time_period['period']

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

	return render_template('plreport.html', transList = transactionList, totalProfit=grand_total, numTrades= num_trades, list=stock_names, dict=stock_dict, period = time_period)

@application.route('/trconfreport/<account>/<date>')
@login_required
def trconfreport(account, date):
	print account
	print date
	transactionList = db.session.query(Transaction).filter(Transaction.account_id == account).all()

	return render_template("traderconfreport.html", list=transactionList, account_id=account)

@application.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		user = db.session.query(User).filter(User.email == request.form['email'], User.password == request.form['password']).first()
		if user:
			session['logged_in'] = True
			session['user_id'] = user.user_id
			if user.admin:
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

			return redirect(url_for('login'))
		else:
			session['logged_in'] = True
			flash('You were just logged in!')
			return redirect(url_for('home'))

	return render_template("register.html")

@application.route('/adminpage', methods=['GET', 'POST'])
@admin_required
@login_required
def adminpage():
	if request.method == 'GET':
		accountsList = db.session.query(Account).all()
		allUsers = db.session.query(User).filter(User.name != 'test').all()
		nonAdmins = db.session.query(User).filter(User.admin == False, User.name != 'test').all()
		return render_template("adminpage.html", accounts=accountsList, 
			allUsers=allUsers, nonAdmins=nonAdmins)
	else:
		if request.form['button'] == "Set as Admins":
			make_admins(request.form.getlist('new_admins'))
			return redirect(url_for('home'))
		elif request.form['button'] == "Associate Accounts":
			user_assoc = request.form['user_adding_to']
			accounts_adding = request.form.getlist('accounts_adding')
			associate_accounts_to_user(user_assoc, accounts_adding)
			return redirect(url_for('home'))
		elif request.form['button'] == "Create Account":
			acct_name = request.form['new_account_name']
			acct_initials = request.form['new_account_initials']
			new_acct = Account(acct_name, acct_initials)
			db.session.add(new_acct)
			db.session.commit()
			return redirect(url_for('home'))
		elif request.form['button'] == "Change Commission":
			acct_id = request.form['account_commission_id']
			commission = request.form['account_commission_value']
			update_commission(acct_id, commission)
			print "we got here"
			return redirect(url_for('home'))

@application.route('/_get_transactions')
def get_transactions():
	account = request.args.get('account', 0, type=int)
	stock_sym = request.args.get('stock_sym', 0).lower()

	return jsonify(get_transactions_for_chart(account, stock_sym))

@application.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'GET':
		return render_template('upload.html')
	else:
		file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(application.config['UPLOAD_FOLDER'] + "\\" + filename)
            return render_template('upload.html', filename=filename)
        else:
        	return render_template('upload.html', )

@application.errorhandler(404)
def page_not_found(e):
	return render_template('pagenotfound.html')

if __name__ == '__main__':
	application.run(debug=True)