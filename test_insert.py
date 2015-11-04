from app import db
from models import *
import os
import sys
import re

### Init database before test
os.system("db_init.py")

trans = Transaction.query.all()

os.system("db_insert.py")

insert_trans = Transaction.query.all()

assert(trans != insert_trans)

sys.exit(0)