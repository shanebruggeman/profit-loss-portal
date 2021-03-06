from __future__ import division
import os
import sys
import random
from parser import maketake_utility
from parser import parse_maketake

sys.path.append('./')
sys.path.append('./parser')
sys.path.append('./db_scripts')
from flask import render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
from functools import wraps
from viewmethods import *
import sys

sys.path.append("db_scripts")
import db_scripts.db_insert as db_insert

UPLOAD_FOLDER = os.getcwd() + '/file_uploads'
MAKETAKE_UPLOAD_FOLDER = os.getcwd() + '/maketake_uploads'

ALLOWED_EXTENSIONS = set(['txt'])
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['MAKETAKE_UPLOAD_FOLDER'] = MAKETAKE_UPLOAD_FOLDER

SEC_FEE_RATE = .0000184  # per dollar of sale as of 2015

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


@application.route('/', methods=['GET', 'POST'])
@login_required
def home():
	if request.method == 'POST':
		report_type = request.form['report_type']
		acct = request.form['account']
		dt = request.form['date_type']
		if report_type == 'trader_conf':
			return redirect(url_for('trconfreport', account=acct, date=dt))
		else:
			return redirect(url_for('newplreport', account=acct, date=dt))

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


@application.route('/newplreport/<account>/<date>')
@login_required
def newplreport(account, date):

	current_account = db.session.query(Account).filter(Account.account_id == account).first()
	current_account_name = current_account.name

	trans_and_time_period = get_transactions_for_date(account, date)
	transactionList = trans_and_time_period['trans']
	time_period = trans_and_time_period['period']

	stock_dict = {}
	bold_dict = {}
	stock_names = []
	num_trades = len(transactionList)

	for item in transactionList:
		print item
		exch = db.session.query(Exchange).filter(Exchange.exchange_id == item.exchange_id).first()
		print "1"
		#print find_maketake
		print current_account.account_id
		maketake_text = maketake_utility.find_maketake(current_account.account_id, item)
		print "2"
		#print maketake_text
		maketake_parser = parse_maketake.MakeTakeParser()
		print "3"
		optionrowholder = maketake_parser.parse_maketake(maketake_text)
		print "4"
		if item.buy_sell == 'Sell':
			isAddingLiquidity = False
		else:
			isAddingLiquidity = True
		exch_fee = optionrowholder.lookup(exch.symbol, isAddingLiquidity)
		print exch_fee
		sec_fee = item.units * SEC_FEE_RATE * item.price * 100
		print sec_fee
		if exch_fee != False:
			if item.buy_sell == 'Sell':
				print "sell"
				print current_account.commission * item.units
				comm =  current_account.commission * item.units
				item.commission = round(comm + sec_fee, 2) + int(float(exch_fee)) # plus exchange fee
			else:
				print "buy"
				comm =  current_account.commission * item.units

				item.commission = round(comm, 2) + int(float(exch_fee)) # plus exchange fee
		else:
			if item.buy_sell == 'Sell':
				item.commission = round((current_account.commission * item.units) + sec_fee, 2) # plus exchange fee
			else:
				item.commission = round(current_account.commission * item.units, 2) # plus exchange fee
		# exchange fee calc ^^^^
		print item.commission
		initSymb = item.sec_sym.partition(' ')[0]
		if initSymb in stock_dict:
			if item.sec_sym in stock_dict[initSymb]:
				# item.sec_sym might not be the correct field
				# need way to tell what option a transaction was made on
				exch = db.session.query(Exchange).filter(Exchange.exchange_id == item.exchange_id).first()
				item.exchange = exch.symbol
				stock_dict[initSymb][item.sec_sym].append(item)

			else:
				stock_dict[initSymb][item.sec_sym] = []
				exch = db.session.query(Exchange).filter(Exchange.exchange_id == item.exchange_id).first()
				item.exchange = exch.symbol
				stock_dict[initSymb][item.sec_sym].append(item)
		else:
			stock_dict[initSymb] = {}
			stock_dict[initSymb][item.sec_sym] = []
			exch = db.session.query(Exchange).filter(Exchange.exchange_id == item.exchange_id).first()
			item.exchange = exch.symbol
			stock_dict[initSymb][item.sec_sym].append(item)

	# create dictionary of transactions in a closing position
	option_profit_dict = {}
	option_unreal_dict = {}
	option_fees_dict = {}
	symbol_profit_dict = {}
	symbol_unreal_dict = {}
	symbol_fees_dict = {}
	for symbol in stock_dict:
		symbol_profit_dict[symbol] = 0
		symbol_unreal_dict[symbol] = 0
		symbol_fees_dict[symbol] = 0
		for option in stock_dict[symbol]:
			current_quantity = 0
			bold_dict[option] = []
			trans_to_bold = []
			option_profit_dict[option] = 0
			option_unreal_dict[option] = 0
			option_fees_dict[option] = 0
			for trans in stock_dict[symbol][option]:
				if trans.isPosition == "regular":
					option_fees_dict[option] += trans.commission
					if (trans.buy_sell == "Buy"):
						recent_buy_price = trans.price
						current_quantity = current_quantity + trans.units
					else:
						real_profits = 100 * (trans.price - recent_buy_price) * trans.units
						option_profit_dict[option] += real_profits
						trans.real = real_profits
						current_quantity = current_quantity - trans.units
				elif trans.isPosition == 'close':
					rand_multiplier = (random.randint(80,120))/100 #random multiplier from 8-120 percent
					print rand_multiplier
					market_price = recent_buy_price * rand_multiplier
					trans.mark = market_price 
					trans.unreal = 100 * (recent_buy_price - market_price) * trans.units
					option_unreal_dict[option] += trans.unreal
				if current_quantity == 0:
					del trans_to_bold[:]
				else:
					trans_to_bold.append(trans.transaction_id)

			symbol_profit_dict[symbol] += option_profit_dict[option]
			symbol_unreal_dict[symbol] += option_unreal_dict[option]
			symbol_fees_dict[symbol] += option_fees_dict[option]


			bold_dict[option] = trans_to_bold
	return render_template('newplreport.html',accountname = current_account_name, stockdict=stock_dict, period=time_period, bolddict=bold_dict, optionprofitdict=option_profit_dict, symbolprofitdict=symbol_profit_dict, optionfeesdict=option_fees_dict, symbolfeesdict=symbol_fees_dict, optionunrealdict=option_unreal_dict, symbolunrealdict=symbol_unreal_dict)


@application.route('/trconfreport/<account>/<date>')
@login_required
def trconfreport(account, date):
	print account
	print date
	transactionList = db.session.query(Transaction).filter(Transaction.account_id == account).all()

	return render_template("traderconfreport.html", list=transactionList, account_id=account)


@application.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		user = db.session.query(User).filter(User.email == request.form['email'],
											 User.password == request.form['password']).first()
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


@application.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		if request.form['name'] is not None and request.form['email'] is not None and \
				request.form['password'] is not None and request.form['password'] == request.form['confirm_password']:

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
			make_admin(request.form.getlist('new_admins'))
			return redirect(url_for('home'))
		elif request.form['button'] == "Associate Accounts":
			user_assoc = request.form['user_adding_to']
			accounts_adding = request.form.getlist('accounts_adding')
			associate_accounts_to_user(user_assoc, accounts_adding)
			return redirect(url_for('home'))


@application.route('/_get_transactions')
def get_transactions():
	account = request.args.get('account', 0, type=int)
	stock_sym = request.args.get('stock_sym', 0).lower()

	return jsonify(get_transactions_for_chart(account, stock_sym))


@application.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'GET':
		accountsList = get_accounts_for_user(session['user_id'])
		return render_template('upload.html', accounts=accountsList)
	else:
		file = request.files['file']
		acct = request.form['account']
		print 'Account ID uploading to: ' + acct
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)

		# save the file and then perform parsing on its stored data
		file_location = UPLOAD_FOLDER + "/" + filename
		file.save(file_location)
		db_insert.main(acct, file_location)

		return render_template('upload.html', filename=filename)
	else:
		return render_template('upload.html', )


@application.route('/maketake-upload', methods=['GET', 'POST'])
def maketake_upload():
	if request.method == 'GET':
		accountsList = get_accounts_for_user(session['user_id'])
		return render_template('maketake-upload.html', accounts=accountsList)
	else:
		file = request.files['file']
		acct = request.form['account']
		fromDate = request.form['fromDate']
		toDate = request.form['toDate']
		print 'Account ID uploading to: ' + acct
		print 'From date: ' + fromDate
		print 'To date: ' + toDate
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)

		print 'Uploading Maketake File'

		# rename any conflicting maketakes
		maketake_utility.rename_maketakes(acct, fromDate, toDate)

		# match the maketake name scheme
		from_date_obj = maketake_utility.make_date("".join(str(fromDate).split('-')))
		to_date_obj = maketake_utility.make_date("".join(str(toDate).split('-')))

		filename = maketake_utility.encode_file_date(acct, from_date_obj, to_date_obj if to_date_obj != '' else None)
		print 'added filename (route level) is ' + filename

		# save uploaded maketake
		file.save(MAKETAKE_UPLOAD_FOLDER + "/" + filename + '.txt')

		# redirect back to original page
		return render_template('maketake-upload.html', filename=filename)
	else:
		return render_template('maketake-upload.html', )


@application.route('/editaccount', methods=['GET', 'POST'])
def editaccount():
	if request.method == 'GET':
		accountsList = db.session.query(Account).order_by(Account.initials).all()
		return render_template('editaccount.html', accounts=accountsList)
	else:
		if request.form['button'] == "Create Account":
			acct_name = request.form['new_account_name']
			acct_initials = request.form['new_account_initials']
			acct_comm = request.form['new_account_commission']
			new_acct = Account(acct_name, acct_initials, acct_comm)
			db.session.add(new_acct)
			db.session.commit()
			return redirect(url_for('editaccount'))
		elif request.form['button'] == "Change Commission":
			acct_id = request.form['account_commission_id']
			commission = request.form['account_commission_value']
			update_commission(acct_id, commission)
			print "we got here"
			return redirect(url_for('editaccount'))


@application.errorhandler(404)
def page_not_found(e):
	return render_template('pagenotfound.html')


if __name__ == '__main__':
	if len(sys.argv) > 1:
		if sys.argv[1] == '-nonlocal':
			application.run(host='0.0.0.0')
		else:
			application.run(debug=True)
	else:
		application.run(debug=True)
