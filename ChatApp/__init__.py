from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from os import environ

app = Flask(__name__)

app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
socketio = SocketIO(app)
sess = Session(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'You Need To Log In To Access The Page'

login_manager.session_protection = None
from ChatApp import routes