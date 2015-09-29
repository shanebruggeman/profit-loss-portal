from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

application = Flask(__name__)

class Creator:
	def makeDB(self):
		application.secret_key = "secret key"
		application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tradetable.db'

		# create the sqlalchemy object
		db = SQLAlchemy(application)
		return db

self = Creator()
db = self.makeDB()