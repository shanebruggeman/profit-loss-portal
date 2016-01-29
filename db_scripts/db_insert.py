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
				print parsed_transaction

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
						print 'User has traded this option in the past, but not today. Adding an additional position for today'
						establish_new_position(parsed_transaction, last_position)

				else:
					print "Building on today's position"
					add_to_day_position(parsed_transaction, today_position)

				# db.session.commit()


			except Exception as e:
				print e
				print 'Rolling back session ...'
				db.session.rollback()
				raise

	# db.session.commit()

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

def get_positions_after(position):
	account_id = position.account_id
	sec_sym = position.symbol


	print 'getting positions after'
	print position.date.year
	print position.date.month
	print position.date.day
	positions_impacted = StockPosition.query.filter(StockPosition.account_id==account_id)\
														.filter(StockPosition.symbol==sec_sym)\
														.filter(extract('year',StockPosition.date) >= position.date.year)\
														.filter(extract('month', StockPosition.date) >= position.date.month)\
														.filter(extract('day', StockPosition.date) > position.date.day)\
														.order_by(StockPosition.date.asc()).all()\

	return positions_impacted

# for if the user has never traded this stock before
def establish_first_position(parsed_transaction):
	# make an empty '0' position for our first start position and flag it as 'isPosition'
	startIsPosition = True
	baseStartPosition = Transaction(parsed_transaction.account_id, parsed_transaction.exchange_id, 0, 0, parsed_transaction.sec_sym, parsed_transaction.settle, parsed_transaction.entry, parsed_transaction.trade, parsed_transaction.ticket_number, parsed_transaction.buy_sell, parsed_transaction.commission, startIsPosition)

	# create the position itself
	firstStockPosition = StockPosition(parsed_transaction.sec_sym, parsed_transaction.entry, parsed_transaction.account_id)
	db.session.add(firstStockPosition)
	db.session.commit()

	# add the starting position and the first day trade to the new position
	print 'Adding first stock base'
	firstStockPosition.all_transactions.append(baseStartPosition)
	print 'Adding first stock transaction'
	firstStockPosition.all_transactions.append(parsed_transaction)

	# add the closing position
	first_close_transaction = sumPosition(firstStockPosition)
	print 'Adding first stock close position'
	firstStockPosition.all_transactions.append(first_close_transaction)

	print '-- Established position: --'
	print firstStockPosition
	print '---------------------------\n'

	check_impacted(firstStockPosition)
	db.session.commit()

# for if the user has traded the stock before, but not on this day yet
def establish_new_position(parsed_transaction, last_position):
	last_close = last_position.all_transactions[-1].clone()
	last_close.entry = parsed_transaction.entry
	last_close.settle = parsed_transaction.settle
	last_close.trade = parsed_transaction.trade

	# the new day has the net value of the old position and the newly parsed entry
	newDayPosition = StockPosition(parsed_transaction.sec_sym, parsed_transaction.entry, parsed_transaction.account_id)

	# add in the actual position for the day and stock
	print 'Adding position for a new day'
	db.session.add(newDayPosition)

	print 'Adding new day open position'
	newDayPosition.all_transactions.append(last_close)
	print 'Adding new day transaction'
	newDayPosition.all_transactions.append(parsed_transaction)

	# find the net after adding in the start position and the parsed transaction
	new_closing_position_as_transaction = sumPosition(newDayPosition)

	# add a transaction that shows the net position after the parsed transaction has been added
	print 'Adding new day close position'
	newDayPosition.all_transactions.append(new_closing_position_as_transaction)

	check_impacted(newDayPosition)
	db.session.commit()

# for if the user is already involved in trading the stock today
def add_to_day_position(parsed_transaction, today_position):
	# pull down all the positions that are affected by a change in today's position
	# previous = get_positions_after(today_position)
	# should_trigger_update = bool(previous)

	# print('Adding transaction to today. Needs to update later transactions already in the database: %s' % (should_trigger_update))
	print 'Adding to an existing position'

	# remove the current closing position
	old_closing_position_as_transaction = today_position.all_transactions.pop()
	Transaction.query.filter(Transaction.transaction_id == old_closing_position_as_transaction.transaction_id).delete()

	# add on the new transaction
	print 'Adding transaction to existing position'
	today_position.all_transactions.append(parsed_transaction)

	# recalculate the closing values, then add to the position
	new_closing_transaction = sumPosition(today_position)
	print 'Adding closing transaction to existing position'
	today_position.all_transactions.append(new_closing_transaction)

	print '--- Changed today position to be: ---'
	print today_position
	print '---------------------------------\n'

	check_impacted(today_position)
	db.session.commit()


def check_impacted(changed_position):
	# update positions that occurred after the changed position
	impacted_positions = get_positions_after(changed_position)

	print 'These positions are impacted: '
	print impacted_positions

	ap = get_all_positions(changed_position.account_id)

	for impacted in impacted_positions:
		print '\nImpacted position is '
		print impacted
		print '\nChanged position is \n'
		print changed_position

		update_impacted_position(changed_position, impacted_positions, 0)
		changed_position = impacted
		db.session.commit()

		print 'Updated: '
		print impacted

	# print ap
	pass

def update_impacted_position(cause_position, impacted_positions, pos):
	if len(impacted_positions) is 0 or len(impacted_positions) <= pos:
		return

	# print 'impact data'
	# print cause_position
	# print pos
	impacted_position = impacted_positions[pos]
	# print impacted_position

	next_impacted = None
	if len(impacted_positions) >= pos + 2:
		next_impacted = impacted_positions[pos + 1]
	# print next_impacted

	# update the impacted position's opening position with the closing position from the causer
	cause_close = cause_position.all_transactions[-1]
	last_close = cause_close.clone()
	last_close.entry = impacted_position.all_transactions[0].entry
	last_close.settle = impacted_position.all_transactions[0].settle
	last_close.trade = impacted_position.all_transactions[0].trade

	# capture the beginning and close on the impacted position
	deleted_open = impacted_position.all_transactions[0]
	deleted_close = impacted_position.all_transactions.pop()

	# replace the open, leaving a correct opening but no closing position
	impacted_position.all_transactions[0] = last_close
	db.session.commit()

	# calculate a new closing position
	new_impacted_close = sumPosition(impacted_position)
	impacted_position.all_transactions.append(new_impacted_close)
	db.session.commit()

	# delete the old beginning / close positions
	Transaction.query.filter(Transaction.transaction_id == deleted_open.transaction_id).delete()
	Transaction.query.filter(Transaction.transaction_id == deleted_close.transaction_id).delete()

	update_impacted_position(next_impacted, impacted_positions, pos + 1)
	db.session.commit()

	# return the impacted position, with updated opening and closing values
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
	# print '\n-- summing position --'
	# print old_position
	old_transactions = old_position.all_transactions

	sum_sec_sym = old_transactions[0].sec_sym
	sum_settle = old_transactions[0].settle
	sum_entry = sum_settle
	sum_trade = sum_settle
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

	summed_transaction = Transaction(old_position.account_id, sum_exchange_id, sum_price, sum_units, sum_sec_sym, sum_settle, sum_entry, sum_trade, sum_ticket_number, sum_buy_sell, sum_commision, True)
	# print 'Summing Result:'
	# print summed_transaction
	# print '--------------------------\n'
	return summed_transaction

if __name__ == '__main__':
	main(sys.argv)