import sys
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/")
from app import db
from models import *
import datetime

# Stack Overflow said this fixes it and it worked so hooray
print "Initializing tables ..."
db.engine.execute("drop schema if exists public cascade")
db.engine.execute("create schema public")
db.create_all()
db.session.commit()

# sample user1
print "Creating Users"
example_user = User("user@gmail.com","password","user", True)
db.session.add(example_user)
db.session.commit()

# sample user2
user_for_testing = User("test@test.com", "password", "test", False)
db.session.add(user_for_testing)
db.session.commit()

# sample accounts 1,2,3
accountConfig = [
    {
        "name": "Windy City Ventures",
        "initials": "WCV",
        "commission": 2.5
    },
    {
        "name": "Donnie Waters LLC",
        "initials": "DWLLC",
        "commission": 1.0
    },
    {
        "name": "Chicago Options Trading",
        "initials": "COT",
        "commission": 3.75
    }
];

# hold all created accounts
accounts = []

print "Creating accounts"
for info in accountConfig:
    # create an account based on the config
    account = Account(info["name"], info["initials"], info["commission"])

    # one copy for local, one copy for the database
    accounts.append(account)
    db.session.add(account);

    # the test user owns all of these accounts
    user_for_testing.accounts.append(account);
    db.session.commit()

example_user.accounts.append(accounts[0])
db.session.commit()

print "Creating exchanges"
example_exchange = Exchange("default-exchange")
db.session.add(example_exchange)
db.session.commit()

print "Adding a User With Positions and Transactions"

# create the objects to store the data in
data_user = User("datauser@gmail.com","drowssap","Data User XIV",True)
data_account = Account("ProfitLossPortal LLC", "PLPLLC", 7.77)

# link the data account to the data user
data_user.accounts.append(data_account)

print "IMPLEMENT ADDING DATA VIA AN INIT DATA & MAKETAKE FILE"

# save the user and everything associated with them
db.session.add(data_user)
db.session.add(data_account)
db.session.commit()


# date1=datetime.datetime(2014,10,14)
# date2=datetime.datetime(2014,11,14)
# date3=datetime.datetime(2014,12,14)
# date4=datetime.datetime(2015,1,14)
# date5=datetime.datetime(2015,2,14)
# date6=datetime.datetime(2015,3,14)

# example_transaction1  = Transaction(example_account.account_id,  example_exchange.exchange_id,  1.00, 4, "ASHR PUT 16OCT15 25 (C)",  date1, date1, date1, "P91-009KQGF", "B", 4.50 , False)
# example_transaction2  = Transaction(example_account2.account_id, example_exchange.exchange_id,  3.00, 6, "CBI CALL 15SEP15 25 (C)",  date1, date1, date1, "P91-455FJSK", "S", 5.00 , False)
# example_transaction3  = Transaction(example_account3.account_id, example_exchange.exchange_id,  2.00, 2, "DANG PUT 18SEP15 6 (C)",   date1, date1, date1, "P91-098FKSJ", "B", 6.75 , False)
# example_transaction4  = Transaction(example_account.account_id,  example_exchange.exchange_id,  1.00, 4, "BLAH PUT 16OCT15 25 (C)",  date1, date1, date1, "P91-009KQGF", "B", 10.00, False)
# example_transaction5  = Transaction(example_account2.account_id, example_exchange.exchange_id,  3.00, 6, "TEST CALL 15SEP15 25 (C)", date1, date1, date1, "P91-455FJSK", "S", 2.00 , False)
# example_transaction6  = Transaction(example_account3.account_id, example_exchange.exchange_id,  2.00, 2, "HELLO PUT 18SEP15 6 (C)",  date1, date1, date1, "P91-098FKSJ", "B", 3.00 , False)
# example_transaction7  = Transaction(example_account.account_id,  example_exchange.exchange_id,  2.00, 4, "ASHR PUT 16OCT15 25 (C)",  date2, date1, date1, "P91-009KQGE", "B", 4.50 , False)
# example_transaction8  = Transaction(example_account.account_id,  example_exchange.exchange_id,  5.00, 4, "ASHR PUT 16OCT15 25 (C)",  date3, date1, date1, "P91-009KQGE", "B", 4.50 , False)
# example_transaction9  = Transaction(example_account.account_id,  example_exchange.exchange_id,  3.00, 4, "ASHR PUT 16OCT15 25 (C)",  date4, date1, date1, "P91-009KQGE", "B", 4.50 , False)
# example_transaction10 = Transaction(example_account.account_id,  example_exchange.exchange_id,  2.00, 4, "ASHR PUT 16OCT15 25 (C)",  date5, date1, date1, "P91-009KQGE", "B", 4.50 , False)
# example_transaction11 = Transaction(example_account.account_id,  example_exchange.exchange_id,  1.00, 4, "ASHR PUT 16OCT15 25 (C)",  date6, date1, date1, "P91-009KQGE", "B", 4.50 , False)

# db.session.add(example_transaction1)
# db.session.add(example_transaction2)
# db.session.add(example_transaction3)
# db.session.add(example_transaction4)
# db.session.add(example_transaction5)
# db.session.add(example_transaction6)
# db.session.add(example_transaction7)
# db.session.add(example_transaction8)
# db.session.add(example_transaction9)
# db.session.add(example_transaction10)
# db.session.add(example_transaction11)

# db.session.commit()
