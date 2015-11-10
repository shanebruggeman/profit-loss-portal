from db_create import db

watches = db.Table('watches',
	db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
	db.Column('account_id', db.Integer, db.ForeignKey('accounts.account_id'))
)

class Account(db.Model):
	
	__tablename__ = "accounts"
#############################
	#ADD COMMISSION FIELD
#############################

	account_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	initials = db.Column(db.String, nullable=False)
	commission = db.Column(db.Float, nullable=False)

	def __init__(self, name, initials, commission):
		self.name = name
		self.initials = initials
		self.commission = commission

	def __repr__(self):
		return 'Account name: <{}> initials: <{}> id: <{}> commission: <{}>'.format(self.name, self.initials, self.account_id, self.commission)

	def __str__(self):
		return repr(self)

class User(db.Model):

	__tablename__ = "users"

	user_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)
	admin = db.Column(db.Boolean, nullable=False)
	accounts = db.relationship('Account', secondary=watches,
	 backref=db.backref('users', lazy='dynamic'))

	def __init__(self, email, password, name, admin):
		self.email = email
		self.password = password
		self.name = name
		self.admin = admin

	def __repr__(self):
		return 'User <{}> with id {}. Is admin? {}'.format(self.name, self.user_id, self.admin)

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
	commission = db.Column(db.Float, nullable=False)

	def __repr__(self):
		return 'Transaction <{}> with id <{}>'.format(self.sec_sym, self.transaction_id)

	def __str__(self):
		return repr(self)

	def __init__(self, account_id, exchange_id, price, units, sec_sym, settle, entry, trade, ticket_number, buy_sell, commission):
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
		self.commission=commission

class Exchange(db.Model):

	__tablename__ = "exchanges"

	exchange_id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String, nullable=False)

	def __repr__(self):
		return 'Exchange: <{}> id: <{}>'.format(self.symbol, self.exchange_id)

	def __str__(self):
		return repr(self)


	def __init__(self, symbol):
		self.symbol=symbol
