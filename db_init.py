from app import db
from models import *
import datetime

# db.reflect()
# db.drop_all()
# Kept getting an error on the drop statement
# Stack Overflow said this fixes it and it worked so hooray
db.engine.execute("drop schema if exists public cascade")
db.engine.execute("create schema public")
db.create_all()
db.session.commit()

example_user = User("user@gmail.com","password","user", True)
db.session.add(example_user)
db.session.commit()

print example_user.user_id

example_account = Account("Windy City Ventures", "WVC")
example_account2 = Account("Donnie Waters LLC", "DWLLC")
example_account3 = Account("Chicago Options Trading", "COT")


db.session.add(example_account)
db.session.add(example_account2)
db.session.add(example_account3)
db.session.commit()

example_user.accounts.append(example_account)
db.session.commit()

example_exchange = Exchange("ex_exchange")
db.session.add(example_exchange)
db.session.commit()


date=datetime.datetime(2014,10,14)
example_transaction=Transaction(example_account.account_id, example_exchange.exchange_id, 1.00, 4, "ASHR PUT 16OCT15 25 (C)", date, date, date, "P91-009KQGF", "B", 4.50)
example_transaction2=Transaction(example_account2.account_id, example_exchange.exchange_id, 3.00, 6, "CBI CALL 15SEP15 25 (C)", date, date, date, "P91-455FJSK", "S", 5.00)
example_transaction3=Transaction(example_account3.account_id, example_exchange.exchange_id, 2.00, 2, "DANG PUT 18SEP15 6 (C)", date, date, date, "P91-098FKSJ", "B", 6.75)
example_transaction4=Transaction(example_account.account_id, example_exchange.exchange_id, 1.00, 4, "BLAH PUT 16OCT15 25 (C)", date, date, date, "P91-009KQGF", "B", 10.00)
example_transaction5=Transaction(example_account2.account_id, example_exchange.exchange_id, 3.00, 6, "TEST CALL 15SEP15 25 (C)", date, date, date, "P91-455FJSK", "S", 2.00)
example_transaction6=Transaction(example_account3.account_id, example_exchange.exchange_id, 2.00, 2, "HELLO PUT 18SEP15 6 (C)", date, date, date, "P91-098FKSJ", "B", 3.00)
example_transaction7=Transaction(example_account.account_id, example_exchange.exchange_id, 4.00, 4, "ASHR PUT 16OCT15 25 (C)", date, date, date, "P91-009KQGE", "B", 4.50)
db.session.add(example_transaction)
db.session.add(example_transaction2)
db.session.add(example_transaction3)
db.session.add(example_transaction4)
db.session.add(example_transaction5)
db.session.add(example_transaction6)
db.session.add(example_transaction7)

db.session.commit()
