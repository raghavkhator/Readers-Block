from app import db, login
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50),unique = True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(50))
	email = db.Column(db.String(50))

	def __repr__(self):
		return '<User {}>'.format(self.username)
	def set_password(self,password):
		self.password = generate_password_hash(password)
	def check_password(self,password):
		return check_password_hash(self.password,password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Document(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50))
	username = db.Column(db.String(50))
	doc = db.Column(db.LargeBinary)
	private = db.Column(db.Integer)
	def __repr__(self):
		return  '<Doc {}>'.format(self.doc)
		