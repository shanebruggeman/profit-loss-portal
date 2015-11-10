from app import db
from models import *
import datetime
import sys
sys.path.append('./parser')
import parse
from datetime import datetime
import re

parse_dir='./parser/' + sys.argv[1]
res = parse.main(parse_dir)

#Add to this list for creating transactions, (CURRENTLY ONLY SEND ORDERS)
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

			sym=trans.get('UnderlyingSymbol') + ' ' + ('CALL ' if bs==1 else 'PUT ') + day+ date_obj.strftime("%b").upper()+year[2:] + ' ' + trans.get('StrikePrice') + (' (C)' if bs==1 else ' (P)')
			new_trans=Transaction(1,1,float(trans.get('Price')), int(trans.get('OrderQty')),sym, date_obj, date_obj, date_obj, 'UNKNOWN TICKET NUMBER', buy_sell, float(trans.get('Commission')))
			db.session.add(new_trans)
		except Exception as e:
			print e
			sys.exit(-1)
db.session.commit()
