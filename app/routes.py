from flask import render_template, redirect, flash, url_for, Flask, request, jsonify, flash, session, send_file
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


@app.route('/user/<username>',methods = ['GET','POST'])
@login_required
def home(username):
    user = User.query.filter_by(username = username).first_or_404()
    if not user:
        return jsonify({"message":"No user found"})
    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    user_data['name'] = user.name
    user_data['email'] = user.email
    session['curr_user'] = user_data
    files=[]
    all_files=Document.query.filter_by(privateval=0)
    for f in all_files:
        files.append({'fname':f.name,'fuser':f.username})
    #print(files)
    session['files']=files
    return render_template('home.html', user = user_data, files=files,found=True,ufound=True, ffound=True)
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
        files=[]
        all_files=Document.query.filter_by(privateval=0)
        for f in all_files:
            files.append({'fname':f.name,'fuser':f.username})
        #print(files)
        session['files']=files
        # return render_template('home.html', user=session['curr_user'])
        return render_template('home.html', user=session['curr_user'],files=session['files'],found=True,ufound=True, ffound=True)

@app.route('/download',  methods=['GET','POST'])
def download():
    ipname=request.form.get('file')
    file_data= Document.query.filter_by(name=ipname).first()
    temp=True
    if file_data is None:
        temp=False
    print(temp)
    if temp:
        return send_file(BytesIO(file_data.doc), attachment_filename=file_data.name, as_attachment=True)
    else:
        return render_template('home.html', user=session['curr_user'],files=session['files'],found=temp)
        #return render_template('home.html', user=session['curr_user'],found=temp)
    return render_template('home.html', user=session['curr_user'],found=temp) 

@app.route('/shared', methods=['GET','POST'])
def shared():
    files=[]
    all_files=Document.query.filter_by(sharedval=1, username=session['username'],privateval=1)
    for f in all_files:
        files.append({'fname':f.name,'fuser':f.username})
    print(files)
    session['files']=files
    return render_template('home.html', user = session['curr_user'], files=files, found=True,ufound=True, ffound=True)

@app.route('/sharefile',methods=['GET','POST'])
def sharefile():
    if request.method=='POST':
        uname=request.form.get('shareduser')
        fname=request.form.get('sharedfile')
        file_data= Document.query.filter_by(name=fname).first()
        user=User.query.filter_by(username=uname).first()
        ffound=True;
        ufound=True;
        if file_data is None:
            ffound=False
        if user is None:
            ufound=False
        if ffound and ufound:    
            newFile= Document(name=file_data.name, username=uname,doc=file_data.doc, privateval=1,sharedval=1)
            db.session.add(newFile)
            db.session.commit()
        files=[]
        all_files=Document.query.filter_by(privateval=0)
        for f in all_files:
            files.append({'fname':f.name,'fuser':f.username})
        #print(files)
        session['files']=files
        if  not ffound or not ufound:
            return render_template('home.html', user=session['curr_user'],files=session['files'],ufound=ufound, ffound=ffound,found=True)
            #return render_template('home.html', user=session['curr_user'],found=temp) 
        return render_template('home.html', user = session['curr_user'], files=session['files'],ufound=ufound, ffound=ffound,found=True)

@app.route('/profilePage',methods=['POST','GET'])
def profile():
    files=[]
    all_files=Document.query.filter_by(privateval=1,username=session['username'])
    for f in all_files:
        files.append({'fname':f.name,'fuser':f.username})
    #print(files)
    session['privatefiles']=files
    return render_template('profile.html', user=session['curr_user'],alert=False,hide=True,files=files)

@app.route('/changePassword', methods=['POST'])
def changePassword():
    matched=False
    error="password doesnt match"
    if request.method=='POST':
        op = User.query.filter_by(username=session['username']).first()
        matched = op.check_password(request.form.get('passOld'))
        print(matched)
        newPass = request.form.get('passNew')
        if matched and newPass and newPass==request.form.get('passRe'):
            op.set_password(newPass)
            db.session.commit()
            return render_template('profile.html',user=session['curr_user'],alert=True,error='',hide=True)
        if not matched:
            error="Incorrect old password"
    return render_template('profile.html',user=session['curr_user'],alert=False,error=error,hide=False)

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method=='POST':
        files=[]
        all_files=Document.query.filter_by(sharedval=0, privateval=0)
        searchstr=request.form.get('searchBar')
        print(searchstr)
        for f in all_files:
            if searchstr in f.name:
                files.append({'fname':f.name,'fuser':f.username})
        print(files)
        session['files']=files
    return render_template('home.html', user = session['curr_user'], files=files, found=True,ufound=True, ffound=True)


@app.route('/logout')
def logout():
    logout_user()
    session['username']=''
    return redirect(url_for('loginRegistration'))
app.run(debug = True)
