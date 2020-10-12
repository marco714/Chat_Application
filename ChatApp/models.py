from ChatApp import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))
    
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file= db.Column(db.String(20), nullable=False, default='default.jpg')
    password=db.Column(db.String(20), nullable=False)

    user_participants = db.relationship('Participants', backref='participants_user', lazy=True)
    user_room = db.relationship('Message', backref='message_user', lazy=True)
    
    def __repr__(self):

        return f"{self.username}"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=True)
    type = db.Column(db.Boolean, nullable=True)

    room_participants = db.relationship('Participants', backref='participants_room', lazy=True)
    room_message = db.relationship('Message', backref='message_room', lazy=True)

class Participants(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):

        return f"{self.message}"