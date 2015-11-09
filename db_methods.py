from app import db
from models import *

def insert(obj):
	db.session.add(obj)
	db.session.commit()

def delete_user_by_email(email):
	User.query.filter(User.email == email).delete()
        db.session.commit()

def delete_user_by_id(user_id):
	User.query.filter(User.user_id == user_id).delete()
	db.session.commit()

def delete_account_by_id(acc_id):
	Account.query.filter(Account.account_id == acc_id).delete()
	db.session.commit()

def delete_exchange_by_id(ex_id):
	Exchange.query.filter(Exchange.exchange_id == ex_id).delete()
	db.session.commit()

def delete_transaction_by_id(trans_id):
	Transaction.query.filter(Transaction.transaction_id == trans_id).delete()
	db.session.commit()
