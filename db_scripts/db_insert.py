import sys
import time
sys.path.append('../')
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/")
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/parser")
from app import db
from models import *
import datetime
from sqlalchemy.sql import extract

sys.path.append('../parser')
import parse
from datetime import datetime
import re

def main(exec_args):
	dataFile = open("db_scripts/example_parse_data.txt","r").read()
	maketakeFile = open("db_scripts/example_maketake.txt","r").read()
	chosenExchange = "Box"

	res = parse.main(["", dataFile, maketakeFile, chosenExchange])

	#Add to this list for creating transactions, (CURRENTLY ONLY SEND ORDERS)
	allowedMessages = 'D'
	for trans in res:
		if trans.get('MsgType') in allowedMessages:
			print '\nAdding transaction to database!'

			# convert all the parsed transactions into database transactions
			try:
				# build the database transaction from the parsed result
				parsed_transaction = build_db_transaction(trans)

				transaction_date = parsed_transaction.settle

				today_position = get_date_position(parsed_transaction.account_id, parsed_transaction.sec_sym, transaction_date.month, transaction_date.day, transaction_date.year)

				# if there is no position today yet
				if today_position == None:

					# get the most recent position on the account
					most_recent_position = get_most_recent_position(parsed_transaction.account_id, parsed_transaction.sec_sym)
					last_position = get_most_recent_position(parsed_transaction.account_id, parsed_transaction.sec_sym)

					# the user has never traded this stock
					if last_position == None:
						print 'User has never traded this option before. Building first position ...'
						establish_first_position(parsed_transaction)

					# this stock has been traded before this day, but not on this day (yet)
					else:
						print 'User has traded this option in the past, but not today. Adding an additional position'
						establish_new_position(parsed_transaction, last_position)

				else:
					print "Building on today's position"
					add_to_day_position(parsed_transaction, today_position)

			except Exception as e:
				print e
				db.session.rollback()
				raise

	db.session.commit()

def build_db_transaction(trans):
	date=trans.get('TransactTime')
	year=date[:4]
	month=date[4:6]
	day=date[6:8]

	print month + ' ' + day + ' ' + year

	ttime=re.split("-", date)[1]
	date_str=year+'/'+month+'/'+day+' '+ttime
	bs=trans.get('PutOrCall')

	account_id = 1
	exchange_id = 1
	price = float(trans.get('Price'))
	units = int(trans.get('OrderQty'))
	settle = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S.%f" )
	# sec_sym = trans.get('UnderlyingSymbol') + ' ' + ('CALL ' if bs==1 else 'PUT ') + day+ settle.strftime("%b")+year[2:] + ' ' + trans.get('StrikePrice') + ' (C)'
	sec_sym = trans.get('UnderlyingSymbol')
	entry = settle
	trade = settle
	ticket_number = "UNKNOWN TICKET NUMBER"
	if bs == 1:
		buy_sell='Buy'
	else:
		buy_sell='Sell'

	commission = float(trans.get('Commission'))

	# all parsed transactions are not opening positions
	isPosition = False
	parsed_transaction = Transaction(account_id, exchange_id, price, units, sec_sym, settle, entry, trade, ticket_number, buy_sell, commission, isPosition)
	return parsed_transaction

def get_date_position(account_id, sec_sym, month, day, year):
	# limit possible existing positions to the ones with the same stock and date
	today_position = StockPosition.query.filter(StockPosition.account_id==account_id).filter(StockPosition.symbol == sec_sym).filter(extract('year', StockPosition.date) == year).filter(extract('month', StockPosition.date) == month).filter(extract('day', StockPosition.date) == day).first()
	return today_position

def get_most_recent_position(account_id, sec_sym):
	most_recent_position = StockPosition.query.filter(StockPosition.account_id == account_id).filter(StockPosition.symbol == sec_sym).order_by(StockPosition.date.desc()).first()
	return most_recent_position

def get_all_positions(account_id):
	all_positions = StockPosition.query.filter(StockPosition.account_id==account_id).all()
	return all_positions

# for if the user has never traded this stock before
def establish_first_position(parsed_transaction):
	# make an empty '0' position for our first start position and flag it as 'isPosition'
	startIsPosition = True
	baseStartPosition = Transaction(parsed_transaction.account_id, parsed_transaction.exchange_id, -1, 0, parsed_transaction.sec_sym, parsed_transaction.settle, parsed_transaction.entry, parsed_transaction.trade, parsed_transaction.ticket_number, parsed_transaction.buy_sell, parsed_transaction.commission, startIsPosition)

	# create the position itself
	firstStockPosition = StockPosition(parsed_transaction.sec_sym, parsed_transaction.entry, parsed_transaction.account_id)

	# add the starting position and the first day trade to the new position
	firstStockPosition.all_transactions.append(baseStartPosition)
	firstStockPosition.all_transactions.append(parsed_transaction)

	# write the changes to the database
	db.session.add(firstStockPosition)
	db.session.commit()

# for if the user has traded the stock before, but not on this day yet
def establish_new_position(parsed_transaction, last_position):
	# take the net values from the old position and represent them as a summed transaction of all that has occurred before this day
	positionSumTransaction = sumPosition(last_position)

	# the new day has the net value of the old position and the newly parsed entry
	newDayPosition = StockPosition(parsed_transaction.sec_sym, parsed_transaction.entry, parsed_transaction.account_id)
	newDayPosition.all_transactions.append(positionSumTransaction)
	newDayPosition.all_transactions.append(parsed_transaction)

	db.session.add(newDayPosition)
	db.session.commit()

# for if the user is already involved in trading the stock today
def add_to_day_position(parsed_transaction, today_position):
	previous = StockPosition.query.filter(StockPosition.symbol == parsed_transaction.sec_sym).order_by(StockPosition.date.desc()).all()
	isPreviousDay = False
	if isPreviousDay:
		print 'Adding transaction into previous day history, updating later positions'
		# update all stock positions on days after the inserted position
	else:
		print 'Adding transaction to today, no retroactive update needed'
		today_position.all_transactions.append(parsed_transaction)
		db.session.commit()

#
# A position's transaction list is composed of three parts:
# 	1) The opening position for the day (flagged as isPosition)
# 	2) All transactions that are traded during the day
# 	3) The closing position for the day (flagged as isPosition)
#
# This function will take all transactions within this list and
# find the net effects for the day, summed up as if it all
# happened in one transaction. The returned transaction will also
# be flagged as "isPosition" to indicate it is a summary of other
# transactions on a given day.
#
# Note, if using this function for finding the closing position,
# remember to remove the old closing position before summing.
##
def sumPosition(old_position):
	old_transactions = old_position.all_transactions

	sum_sec_sym = old_transactions[0].sec_sym
	sum_settle = old_transactions[0].settle
	sum_entry = old_transactions[0].entry
	sum_trade = old_transactions[0].trade
	sum_ticket_number = old_transactions[0].ticket_number
	sum_buy_sell = 'buy'

	total_price = 0
	total_units = 0
	total_commision = 0

	sum_sec_sym = old_position.symbol

	for transaction in old_transactions:
		total_units += transaction.units

		if transaction.buy_sell == 'buy':
			total_price += transaction.price * transaction.units
		else:
			total_price += transaction.price * -1 * transaction.units

		total_commision += transaction.units * transaction.commission

	sum_price = total_price / total_units
	sum_units = total_units
	sum_commision = total_commision / total_units

	# we need to hook the exchanges up to actual data
	sum_exchange_id = 1

	return Transaction(old_position.account_id, sum_exchange_id, sum_price, sum_units, sum_sec_sym, sum_settle, sum_entry, sum_trade, sum_ticket_number, sum_buy_sell, sum_commision, True)

if __name__ == '__main__':
	main(sys.argv)