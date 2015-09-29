from db_create import db

class User(db.Model):

	__tablename__ = "users"

	user_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	username = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)

	def __init__(self, username, password, name):
		self.username = username
		self.password = password
		self.name = name

	def __repr__(self):
		return 'User <{}> with id {}'.format(self.name, self.user_id)

	def __str__(self):
		return repr(self)


class Account(db.Model):
	
	__tablename__ = "accounts"

	account_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete='CASCADE')) # may need re-evaluated
	name = db.Column(db.String, nullable=False)

	def __init__(self, user_id, name):
		self.user_id = user_id
		self.name = name

	def __repr__(self):
		return 'Account <{}>'.format(self.name)

	def __str__(self):
		return repr(self)

class Transaction(db.Model):

	__tablename__ = "transactions"

	transaction_id = db.Column(db.Integer, primary_key=True)
	account_id = db.Column(db.Integer, db.ForeignKey("accounts.account_id", ondelete='CASCADE')) # may need re-evaluated
	exchange_id = db.Column(db.Integer, db.ForeignKey("exchanges.exchange_id", ondelete='CASCADE')) # may need re-evaluated

	price = db.Column(db.Float, nullable=False)
	units = db.Column(db.Integer, nullable=False)
	sec_sym = db.Column(db.String, nullable=False)
	settle = db.Column(db.DateTime, nullable=False) # check time zone
	entry = db.Column(db.DateTime, nullable=False) # check time zone
	trade = db.Column(db.DateTime, nullable=False) # check time zone
	ticket_number = db.Column(db.String, nullable=False)
	buy_sell = db.Column(db.String, nullable=False)

	def __repr__(self):
		return 'Transaction <{}>'.format(self.sec_sym)

	def __str__(self):
		return repr(self)

	def __init__(self, account_id, exchange_id, price, units, sec_sym, settle, entry, trade, ticket_number, buy_sell):
		self.account_id=account_id
		self.exchange_id=exchange_id
		self.price=price
		self.units=units
		self.sec_sym=sec_sym
		self.settle=settle
		self.entry=entry
		self.trade=trade
		self.ticket_number=ticket_number
		self.buy_sell=buy_sell	

class Exchange(db.Model):

	__tablename__ = "exchanges"

	exchange_id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String, nullable=False)

	def __repr__(self):
		return 'Exchange <{}>'.format(self.symbol)

	def __str__(self):
		return repr(self)


	def __init__(self, symbol):
		self.symbol=symbol