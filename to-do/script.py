#!/usr/bin/env python

from flask import Flask, request, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from flask_sqlalchemy import SQLAlchemy
from wtforms import validators
import datetime
import os

app = Flask(__name__)
db = SQLAlchemy(app)
#Post.query.filter_by(id = id).all()
#Post.query.filter_by(category=category).all()

db_path = os.path.join(os.path.dirname(__file__), 'test.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SECRET_KEY'] = 'shhdonttell'




class RegisterForm(FlaskForm):
	username = StringField('choose a username', [validators.DataRequired()])
	password = PasswordField("choose a password", [validators.DataRequired()])
	submit = SubmitField("register")


class LoginForm(FlaskForm):
	username = StringField("enter your username", [validators.DataRequired()])
	password = PasswordField("enter your password", [validators.DataRequired()])
	submit = SubmitField("login")


class ToDoForm(FlaskForm):
	task = StringField("to-do title", [validators.DataRequired()])
	content = TextAreaField("to-do content", [validators.DataRequired()])
	submit = SubmitField("add item")



class User(db.Model):

	__tablename__ = 'users'
	username = db.Column(db.String(64), unique=True)
	password = db.Column(db.Integer)
	user_id = db.Column(db.Integer, primary_key = True)


class TodoItem(db.Model):
	__tablename__ = 'todoitems'
	task = db.Column(db.String)
	new_id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String)
	#make unique=false so that we can store items 1, 2, 3 for user_one, items 1, 2, 3 for user_two; all in same table.
	task_id = db.Column(db.Integer, unique=False)
	user_created = db.Column(db.String)
	date = db.Column(db.Date)
	finished = db.Column(db.Boolean)




@app.route("/additem", methods=['GET', 'POST'])
def additem():
	form = ToDoForm()
	if form.validate_on_submit():
		task = form.task.data
		content = form.content.data
		date = datetime.datetime.today()
		finished = False 
		user = session.get("name")
		task_id = len(TodoItem.query.filter_by(user_created=session.get("name")).all()) + 1
		newitem = TodoItem(task=task, content=content,task_id=task_id, user_created=user, date=date, finished=finished )
		db.session.add(newitem)
		db.session.commit()
		flash("new item added")
		return redirect(url_for("home"))


	return render_template("additem.html", form=form)



@app.route("/viewitem/<int:id>", methods=['GET', 'POST'])
def viewitem(id):

	item_pressed = TodoItem.query.filter_by(task_id=id, user_created=session.get("name")).first()
	if request.method == "POST":
		if request.form['update'] == "update":
			if request.form['task'] == "" or request.form['content'] == "":
				flash("Please do not leave either the task or content blank.")
				return redirect(url_for("viewitem", id=item_pressed.task_id))
			else:
				task = request.form['task']
				content = request.form['content']
				finished = str(request.form.get("finished"))
				if finished == "None":
					item_pressed.task = task 
					item_pressed.content = content
					item_pressed.finished = False
				else:
					item_pressed.task = task 
					item_pressed.content = content
					item_pressed.finished = True
				db.session.commit()
				return redirect(url_for("home"))
		else:
			#change all ids of items before - 1
			items = TodoItem.query.filter_by(user_created = session.get("name"))
			all_items_after = items.filter(TodoItem.task_id > item_pressed.task_id).all()
			for item in all_items_after:
				item.task_id = item.task_id - 1
			db.session.delete(item_pressed)
			db.session.commit()
			return redirect(url_for("home"))


	return render_template("viewitem.html", item = item_pressed)

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	errors = []
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		if len(username) < 6 or len(password) < 6:
			errors.append('Sorry, your username and/or password are too short.')
		result = User.query.filter_by(username=username).all()
		if result:
			errors.append( 'Sorry, your username is already taken.')
		if errors:
			for error in errors:
				flash(error)
			return redirect(url_for("register"))
		else:
			db.session.add(User(username= username, password=password))
			db.session.commit()
			return redirect(url_for("login"))



	return render_template('register.html', form=form)
#items=User.query.filter_by(username=session.get("username")).all()
# items.size() + 1


@app.route("/login", methods=['GET', 'POST'])
def login():
	if session.get("name") is not None:
		return redirect(url_for("home"))
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		result = User.query.filter_by(username=username).all()
		if result != [] and result[0].password == password: 
			session['name'] = username
			return redirect(url_for("home"))
		else:
			flash("your username and/or password is incorrect")
			return redirect(url_for("login"))


	
	return render_template("login.html", form=form)


@app.route("/home", methods=['POST', 'GET'])
def home():
	if session.get("name") is None:
		return redirect(url_for("login"))
	if request.method == 'POST':
		if request.form['logout']:
			session.clear()
			return redirect(url_for("login"))


	return render_template("home.html", name=session.get("name"), items=TodoItem.query.filter_by(user_created=session.get("name")).all())


	

if __name__ == "__main__":
	app.run(debug=True)