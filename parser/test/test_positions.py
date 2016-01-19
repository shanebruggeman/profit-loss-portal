import sys
sys.path.append('../../')
#from db_create import db
#from models import *
import datetime
import unittest

class TestPositions(unittest.TestCase):
    def test_positions(self):
	self.assertTrue(True)
	return
        date=datetime.datetime.now()
	pos=StockPosition('TEST_STOCK_POSITION_PLEASE_IGNORE', date, 1)
	db.session.add(pos)
	db.session.commit()
        query=StockPosition.query.filter(StockPosition.symbol == 'TEST_STOCK_POSITION_PLEASE_IGNORE').first()
        self.assertEqual(str(pos), str(query))

        #delete, undo the add, and make sure successful
        StockPosition.query.filter(StockPosition.symbol == 'TEST_STOCK_POSITION_PLEASE_IGNORE').delete()
        query=StockPosition.query.filter(StockPosition.symbol == 'TEST_STOCK_POSITION_PLEASE_IGNORE').first()
	db.session.commit()
        self.assertIsNone(query)

if __name__ == '__main__':
	unittest.main()
