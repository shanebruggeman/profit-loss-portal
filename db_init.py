from app import db
from models import *
import datetime

db.create_all()
db.session.commit()

example_user = User("user@gmail.com","password","user")
db.session.add(example_user)
db.session.commit()

example_account = Account(example_user.user_id, "Windy City Ventures", "WVC")
db.session.add(example_account)
db.session.commit()
example_account2 = Account(example_user.user_id, "Donnie Waters LLC", "DWLLC")
db.session.add(example_account)
db.session.commit()
example_account3 = Account(example_user.user_id, "Chicago Options Trading", "COT")
db.session.add(example_account)
db.session.add(example_account2)
db.session.add(example_account3)
db.session.commit()

example_exchange = Exchange("ex_exchange")
db.session.add(example_exchange)
db.session.commit()

date=datetime.datetime(2014,10,14)
example_transaction=Transaction(example_account.account_id, example_exchange.exchange_id, 1.00, 4, "ASHR PUT 16OCT15 25 (C)", date, date, date, "P91-009KQGF", "B")
db.session.add(example_transaction)
example_transaction2=Transaction(example_account.account_id, example_exchange.exchange_id, 3.00, 6, "CBI CALL 15SEP15 25 (C)", date, date, date, "P91-455FJSK", "S")
db.session.add(example_transaction2)
example_transaction3=Transaction(example_account.account_id, example_exchange.exchange_id, 2.00, 2, "DANG PUT 18SEP15 6 (C)", date, date, date, "P91-098FKSJ", "B")
db.session.add(example_transaction3)
db.session.commit()
