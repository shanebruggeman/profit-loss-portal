import sys
sys.path.append("/Users/watersdr/Documents/Github/profit-loss-portal/")
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/")
sys.path.append("../")
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
]

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

# print "IMPLEMENT ADDING DATA VIA AN INIT DATA & MAKETAKE FILE"

# save the user and everything associated with them
db.session.add(data_user)
db.session.add(data_account)
db.session.commit()
