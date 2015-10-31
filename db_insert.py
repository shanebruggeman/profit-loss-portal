from app import db
from models import *
import datetime
import sys
sys.path.append('./parser')
import parse
from datetime import datetime
import re

res = parse.main('./parser/testdata1.txt')


#Add to this list for creating transactions
allowedMessages = 'D'
for trans in res:
	if trans.get('MsgType') in allowedMessages:
		print 'Adding transaction to database!'
		try:
			date=trans.get('TransactTime')
			year=date[:4]
			month=date[4:6]
			day=date[6:8]
			ttime=re.split("-", date)[1]
			date_str=year+'/'+month+'/'+day+' '+ttime
			date_obj = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S.%f" )
			bs=trans.get('PutOrCall')
			if bs == 1:
				buy_sell='Buy'
			else:
				buy_sell='Sell'
			new_trans=Transaction(0,0,float(trans.get('Price')), int(trans.get('OrderQty')),trans.get('UnderlyingSymbol'), date_obj, date_obj, date_obj, trans.get('Symbol'), buy_sell, float(trans.get('Commission')))
			db.session.add(new_trans)
		except Exception as e:
			print e
			sys.exit(-1)
db.session.commit()
