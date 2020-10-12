from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from ChatApp.models import User

class RegistrationForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('ConfirmPass', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register Now')
    
    def validate_username(self, username):

        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('That Username is Taken. Please Choose A Different One')
    
    def validate_email(self, email):

        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('That Email is Taken. Please Choose A Different One')
        
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login Now')