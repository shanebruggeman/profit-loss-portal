from models import *

print 'USER'
print User.query.all()
print 'ACCOUNT'
print Account.query.all()
print 'TRANSACTION'
print Transaction.query.all()
print 'EXCHANGE'
print Exchange.query.all()
