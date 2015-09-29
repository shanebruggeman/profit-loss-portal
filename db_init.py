from app import db
from models import *
import datetime

db.create_all()
db.session.commit()

example_user = User("user3@gmail.com","password","user3")
db.session.add(example_user)
db.session.commit()

example_account = Account(example_user.user_id, "example account name")
db.session.add(example_account)
db.session.commit()

example_exchange = Exchange("ex_exchange")
db.session.add(example_exchange)
db.session.commit()

date=datetime.datetime(2014,10,14)
example_transaction=Transaction(example_account.account_id, example_exchange.exchange_id, 1.00, 4, "sec", date, date, date, "tic_num", "buy_me")
db.session.add(example_transaction)
db.session.commit()

#create the database and the tables
# db.create_all()
# db.session.add(User("brian@mail.com", "password", "brian"))
# db.session.add(Account("Good", "I\'m good."))
# db.session.add(Exchange("Good", "I\'m good."))
# db.session.add(Transaction("Good", "I\'m good."))
# db.session.add(Transaction("Good", "I\'m good."))


#insert
# db.session.add(BlogPost("Good", "I\'m good."))
# db.session.add(BlogPost("Good", "I\'m well."))

# commit the changes
# db.session.commit()
