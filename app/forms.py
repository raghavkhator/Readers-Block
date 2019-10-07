from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from werkzeug.security import generate_password_hash,check_password_hash
from app.models import User
 
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('Username doesn\'t exist!')

 
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=40)],render_kw={"placeholder": "Name"})
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)],render_kw={"placeholder": "Password"})
    c_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')],render_kw={"placeholder": "Confirm Password"})
    email = StringField('Email',validators=[DataRequired(),Email()],render_kw={"placeholder": "Email"})
    submit = SubmitField('Register')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
 
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')