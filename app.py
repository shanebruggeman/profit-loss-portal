from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps

from db_create import db, application
from models import *

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('login'))
	return wrap

@application.route('/')
def home():
	# posts = db.session.query(User).all()
	# return render_template("index.html")

	# totalstring = ""
	# for item in posts:
	# 	 totalstring += str(item)

	# print totalstring
	return render_template("index.html")

@application.route('/index')
def main_page():
	return redirect(url_for('home'))

@application.route('/about')
def about():
	return render_template("about.html")

@application.route('/customers')
def customers():
	return render_template("customers.html")

@application.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			session['logged_in'] = True
			flash('You were just logged in!')
			return redirect(url_for('home'))

	return render_template("login.html", error=error)

@application.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were just logged out!')
	return redirect(url_for('welcome'))

@application.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		if  request.form['name'] != None and request.form['username'] != None and request.form['password'] != None and request.form['password'] == request.form['confirm_password']:

			req_name = request.form['name']
			req_username = request.form['username'] 
			req_password = request.form['password']

			new_user = User(req_username, req_password, req_name)
			db.session.add(new_user)
			db.session.commit()

			redirect(url_for('home'))
		else:
			session['logged_in'] = True
			flash('You were just logged in!')
			return redirect(url_for('home'))

	return render_template("register.html")

if __name__ == '__main__':
	application.run(debug=True)