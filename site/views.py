from .models import User, get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

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

    return render_template('register.html')