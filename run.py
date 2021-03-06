####################################  Setup  ####################################

from flask import Flask, request, session, redirect, url_for, render_template, flash
import os

app = Flask(__name__)

from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import uuid

username = 'neo4j'
password = 'WebDev'
graph = Graph('http://localhost:7474/db/data/', username=username, password=password)

def create_uniqueness_constraint(label, property):
	query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
	query = query.format(label=label, property=property)
	graph.run(query)

create_uniqueness_constraint("User", "username")
create_uniqueness_constraint("Topic", "name")
create_uniqueness_constraint("Question", "id")
create_uniqueness_constraint("Answer", "id")


##################################  Functions  ##################################

class User:
	def __init__(self, username):
		self.username = username

	def find(self):
		user = graph.find_one("User", "username", self.username)
		return user
	
	def register(self, email, password):
		if not self.find():
			user = Node("User", username=self.username, email=email, password=bcrypt.encrypt(password))
			graph.create(user)
			return True
		else:
			return False
			
	def verify_password(self, password):
		user = self.find()
		if user:
			return bcrypt.verify(password, user['password'])
		else:
			return False
			
	def add_question(self, text, topics):
		user = self.find()
		question = Node(
			"Question",
			id=str(uuid.uuid4()),
			text=text,
			timestamp=timestamp(),
			date=date()
		)
		rel = Relationship(user, "ASKED", question)
		graph.create(rel)

		topics = [x.strip() for x in topics.lower().split(',')]
		for t in set(topics):
			topic = graph.merge_one("Topic", "name", t)
			rel = Relationship(topic, "TAGGED", question)
			graph.create(rel)
			
def timestamp():
	epoch = datetime.utcfromtimestamp(0)
	now = datetime.now()
	delta = now - epoch
	return delta.total_seconds()

def date():
	return datetime.now().strftime('%Y-%m-%d')

	
####################################  Views  ####################################

@app.route('/')
def index():
	return render_template('index.html', title="Quora-lite")

@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		email = request.form['email']
		username = request.form['username']
		password = request.form['psw']
		if len(email) < 1:																# Proper email checks
			flash('Your email must be at least one character.')
		if len(username) < 1:															# better username checks?
			flash('Your username must be at least one character.')
		elif len(password) < 5:															# better password checks?
			flash('Your password must be at least 5 characters.')
		elif not User(username).register(email, password):								# Should probably have separate checks for username and email
			flash('A user with that username or email already exists.')
		else:
			session['username'] = username
			flash('Logged in.')
			return redirect(url_for('index'))

	return render_template('register.html', title="Register")
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['psw']

		if not User(username).verify_password(password):
			flash('Invalid login.')
		else:
			session['username'] = username
			flash('Logged in.')
			return redirect(url_for('index'))

	return render_template('login.html', title="Login")
	
@app.route('/add_question', methods=['POST'])
def add_question():
	text = request.form['question']
	topics = request.form['topics']

	if not text:
		flash('You must give your post a title.')
	else:
		User(session['username']).add_question(text, topics)

	return redirect(url_for('index'))
	
@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logged out.')
	return redirect(url_for('index'))
	
@app.route('/changePassword')
def changePassword():
	return render_template('Changepsw.html', title="Change Password")
	
@app.route('/profile')
def profile():
	return render_template('profile.html', title="Profile")

	
###################################  Run app  ###################################

app.secret_key = os.urandom(24)
app.run(debug=True)