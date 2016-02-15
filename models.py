from db_create import db

watches = db.Table('watches',
	db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
	db.Column('account_id', db.Integer, db.ForeignKey('accounts.account_id'))
)

position_watches = db.Table('position_watches',
	db.Column('position_id', db.Integer, db.ForeignKey('stock_positions.stock_position_id', ondelete='cascade', onupdate='cascade')),
	db.Column('transaction_id', db.Integer, db.ForeignKey('transactions.transaction_id', ondelete='cascade', onupdate='cascade')))

class Account(db.Model):
	__tablename__ = "accounts"
	account_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	initials = db.Column(db.String, nullable=False)
	commission = db.Column(db.Float, nullable=False)

	def __init__(self, name, initials, commission):
		self.name = name
		self.initials = initials
		self.commission = commission

	def __repr__(self):
		return '<Account id="{}" initials="{}" name="{}">'.format(self.account_id, self.initials, self.name)

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
		return '<User id="{}" name="{}" AdminStatus="{}"'.format(self.user_id, self.name, self.admin)

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
	isPosition = db.Column(db.String, nullable=False)

	# make an identical transaction not linked to the originals
	def clone(self):
		copy = Transaction(self.account_id, self.exchange_id, self.price, self.units, self.sec_sym, self.settle, self.entry, self.trade, self.ticket_number, self.buy_sell, self.commission, self.isPosition)
		copy.transaction_id = None
		return copy

	def mimic(self, other_transaction):
		self.exchange_id = other_transaction.account_id;
		self.price = other_transaction.price;
		self.units = other_transaction.units;
		self.sec_sym = other_transaction.sec_sym;
		self.settle = other_transaction.settle;
		self.entry = other_transaction.entry;
		self.trade = other_transaction.trade;
		self.ticket_number = other_transaction.ticket_number;
		self.buy_sell = other_transaction.buy_sell;
		self.commission = other_transaction.commission;
		self.isPosition = other_transaction.isPosition;

	def mimic_except_date(self, other_transaction):
		self.exchange_id = other_transaction.account_id;
		self.price = other_transaction.price;
		self.units = other_transaction.units;
		self.sec_sym = other_transaction.sec_sym;
		self.ticket_number = other_transaction.ticket_number;
		self.buy_sell = other_transaction.buy_sell;
		self.commission = other_transaction.commission;
		self.isPosition = other_transaction.isPosition;

	def getSymbol(self):
		return self.sec_sym

	def __repr__(self):
		return '<Transaction id="{}" symbol="{}" buy_sell={} isPosition={} units="{}" price="{}" commission="{}" date="{}">'.format(self.transaction_id, self.sec_sym, self.buy_sell, self.isPosition, self.units, self.price, self.commission, self.settle.date())

	def __str__(self):
		return repr(self)

	def __init__(self, account_id, exchange_id, price, units, sec_sym, settle, entry, trade, ticket_number, buy_sell, commission, isPosition):
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
		self.isPosition=isPosition

class Exchange(db.Model):

	__tablename__ = "exchanges"

	exchange_id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String, nullable=False)

	def __repr__(self):
		return '<Exchange id="{}" symbol="{}">'.format(self.exchange_id, self.symbol)

	def __str__(self):
		return repr(self)

	def __init__(self, symbol):
		self.symbol=symbol

class StockPosition(db.Model):
	__tablename__ = "stock_positions"

	stock_position_id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String, nullable=False)
	date = db.Column(db.DateTime, nullable=False) # check time zone

	account_id = db.Column(db.Integer, db.ForeignKey("accounts.account_id", ondelete='CASCADE')) # may need re-evaluated

	all_transactions = db.relationship('Transaction', secondary=position_watches,
	 backref=db.backref('stock_positions', lazy='dynamic'))

	def get_open(self):
		open_transactions = filter(lambda transaction: transaction.isPosition == 'open', self.all_transactions)

		if len(open_transactions) > 1:
			print self
			raise 'More than one open transaction on the position'
		else:
			return open_transactions[0]

	def get_close(self):
		close_transactions = filter(lambda transaction: transaction.isPosition == 'close', self.all_transactions)
		if len(close_transactions) > 1:
			print self
			raise 'More than one closing transaction on the position'
		else:
			return close_transactions[0]

	def remove(self, removed):
		db.session.delete(removed)
		db.session.commit()

	def __repr__(self):
		# return '<StockPosition id={} date={} stock={}>'.format(self.stock_position_id, self.date, self.symbol)
		rep = '<StockPosition id={} date={} stock={}>'.format(self.stock_position_id, self.date, self.symbol)
		for transaction in self.all_transactions:
			rep = rep + '\n\t' + str(transaction)
		return rep

	def __str(self):
		return repr(self)

	def __init__(self, symbol, date, owner):
		self.symbol = symbol
		self.date = date
		self.account_id = owner
