from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

application = Flask(__name__)

class Creator:
	def makeDB(self):
		application.secret_key = "secret key"
		application.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ktmqcjjlutudbz:mY5Y8PxSmAHM0vyR8-qWV-ihUg@ec2-54-227-253-238.compute-1.amazonaws.com:5432/dcgao7i27jocnv'

		# create the sqlalchemy object
		db = SQLAlchemy(application)
		return db

self = Creator()
db = self.makeDB()
