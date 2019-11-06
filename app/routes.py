from flask import render_template, redirect, flash, url_for, Flask, request, jsonify, flash, session
from app import app,db
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug import secure_filename
from app.models import User,Document
from io import BytesIO
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, login_required, logout_user


db.create_all()

@app.route('/', methods = ['GET','POST'])
def loginRegistration():
    if current_user.is_authenticated:
        username = current_user.username
        session['username']=username
        return redirect(url_for('home', username = current_user.username))
    formReg = RegistrationForm(prefix='formReg')
    formLog = LoginForm(prefix='formLog')
    if formReg.validate_on_submit() and formReg.submit.data:
        public = str(uuid.uuid4())
        new_user = User(
		name = formReg.name.data,
		username = formReg.username.data,
		email = formReg.email.data,
		)
        new_user.set_password(formReg.password.data)
        db.session.add(new_user)
        db.session.commit()
        session['username']=formReg.username.data
        print('New user created')
        return redirect(url_for('home', username = formReg.username.data,))
    if formLog.validate_on_submit() and formLog.submit.data:
        user = User.query.filter_by(username = formLog.username.data).first()
        if user is None or not user.check_password(formLog.password.data):
            flash('Invalid username or password')
            return redirect(url_for('loginRegistration'))
        login_user(user, remember = True)
        print(user.username)
        session['username']=user.username
        return redirect(url_for('home', username = user.username))
    return render_template('login.html', form = formReg, form1 = formLog)


@app.route('/user/<username>',methods = ['GET'])
@login_required
def home(username):
	user = User.query.filter_by(username = username).first_or_404()
	if not user:
		return jsonify({"message":"No user found"})
	user_data = {}
	user_data['id'] = user.id
	user_data['username'] = user.username
	user_data['name'] = user.name
	user_data['password'] = user.password
	session['curr_user'] = user_data
	return render_template('home.html', user = user_data)
@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        x=0
        if request.form.get('privatebool'):
            x=1
        newFile= Document(name=file.filename, username=session['username'],doc=file.read(), privateval=x)
        db.session.add(newFile)
        db.session.commit()
        return render_template('home.html', user=session['curr_user'])
@app.route('/download')
def download():
    file_data= Document.query.filter_by(id=1).first()
    send_file(BytesIO(file_data.doc), attachment_filename=file_data.name, as_attachement=True)
    return render_template('home.html', user=session['curr_user'])        
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('loginRegistration'))
app.run(debug = True)
