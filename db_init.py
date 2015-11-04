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

user_for_testing = User("test@test.com", "password", "test", False)
db.session.add(user_for_testing)
db.session.commit()

example_account = Account("Windy City Ventures", "WVC", 2.5)
example_account2 = Account("Donnie Waters LLC", "DWLLC", 1.0)
example_account3 = Account("Chicago Options Trading", "COT", 3.75)


db.session.add(example_account)
db.session.add(example_account2)
db.session.add(example_account3)
db.session.commit()

user_for_testing.accounts.append(example_account)
user_for_testing.accounts.append(example_account2)
user_for_testing.accounts.append(example_account3)
db.session.commit()

example_user.accounts.append(example_account)
db.session.commit()

example_exchange = Exchange("ex_exchange")
db.session.add(example_exchange)
db.session.commit()


date=datetime.datetime(2014,10,14)
date2=datetime.datetime(2014,11,14)
date3=datetime.datetime(2014,12,14)
date4=datetime.datetime(2015,1,14)
date5=datetime.datetime(2015,2,14)
date6=datetime.datetime(2015,3,14)
example_transaction=Transaction(example_account.account_id, example_exchange.exchange_id, 1.00, 4, "ASHR PUT 16OCT15 25 (C)", date, date, date, "P91-009KQGF", "B", 4.50)
example_transaction2=Transaction(example_account2.account_id, example_exchange.exchange_id, 3.00, 6, "CBI CALL 15SEP15 25 (C)", date, date, date, "P91-455FJSK", "S", 5.00)
example_transaction3=Transaction(example_account3.account_id, example_exchange.exchange_id, 2.00, 2, "DANG PUT 18SEP15 6 (C)", date, date, date, "P91-098FKSJ", "B", 6.75)
example_transaction4=Transaction(example_account.account_id, example_exchange.exchange_id, 1.00, 4, "BLAH PUT 16OCT15 25 (C)", date, date, date, "P91-009KQGF", "B", 10.00)
example_transaction5=Transaction(example_account2.account_id, example_exchange.exchange_id, 3.00, 6, "TEST CALL 15SEP15 25 (C)", date, date, date, "P91-455FJSK", "S", 2.00)
example_transaction6=Transaction(example_account3.account_id, example_exchange.exchange_id, 2.00, 2, "HELLO PUT 18SEP15 6 (C)", date, date, date, "P91-098FKSJ", "B", 3.00)
example_transaction7=Transaction(example_account.account_id, example_exchange.exchange_id, 2.00, 4, "ASHR PUT 16OCT15 25 (C)", date2, date, date, "P91-009KQGE", "B", 4.50)
example_transaction8=Transaction(example_account.account_id, example_exchange.exchange_id, 5.00, 4, "ASHR PUT 16OCT15 25 (C)", date3, date, date, "P91-009KQGE", "B", 4.50)
example_transaction9=Transaction(example_account.account_id, example_exchange.exchange_id, 3.00, 4, "ASHR PUT 16OCT15 25 (C)", date4, date, date, "P91-009KQGE", "B", 4.50)
example_transaction10=Transaction(example_account.account_id, example_exchange.exchange_id, 2.00, 4, "ASHR PUT 16OCT15 25 (C)", date5, date, date, "P91-009KQGE", "B", 4.50)
example_transaction11=Transaction(example_account.account_id, example_exchange.exchange_id, 1.00, 4, "ASHR PUT 16OCT15 25 (C)", date6, date, date, "P91-009KQGE", "B", 4.50)
db.session.add(example_transaction)
db.session.add(example_transaction2)
db.session.add(example_transaction3)
db.session.add(example_transaction4)
db.session.add(example_transaction5)
db.session.add(example_transaction6)
db.session.add(example_transaction7)
db.session.add(example_transaction8)
db.session.add(example_transaction9)
db.session.add(example_transaction10)
db.session.add(example_transaction11)

db.session.commit()
