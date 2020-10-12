from flask import render_template, url_for, flash, redirect, current_app, request,session
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import send, emit, Namespace, join_room, leave_room
from ChatApp.forms import LoginForm, RegistrationForm
from ChatApp.models import User, Room, Participants, Message
from ChatApp import app, bcrypt, db, socketio

users = dict()

@app.template_filter()
def sender_message(message):
    
    sender_username = message.message_user.username

    return sender_username

app.jinja_env.filters['sender_message'] = sender_message

def get_all_user():

    return User.query.all()

@app.route('/', methods=["GET", "POST"])
def login():
    
    form = LoginForm()
    print(current_app.config['SQLALCHEMY_DATABASE_URI'])
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            print(current_user.id)

            #Next Page
            return redirect(url_for('chat_page'))

        else:
            flash('Login Unsuccessfully', 'danger')
    return render_template("user_login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Logout Successfully', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=["GET","POST"])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)

        db.session.add(user)
        db.session.commit()

        flash("Congratulations! You can Now Login", "success")
        return redirect(url_for('login'))
        
    return render_template("user_register.html", form=form)

@app.route("/chat_page/group_chat", methods=["GET"])
def group_chat():
    room = Room.query.all()
    return render_template("new_group_chat.html", rooms=room)

@app.route("/chat_page", methods=["GET"])
@login_required
def chat_page():
    friends = get_all_user()
    return render_template("chat_page.html", friends=friends)

@app.route("/chat_page/<int:user_id>", methods=["GET"])
@login_required
def friend_chat(user_id):

    friends = get_all_user()
    receiver = User.query.get(user_id)
    sender = User.query.get(current_user.id)
    
    old_room = None

    for user1 in sender.user_participants:
        for user2 in receiver.user_participants:

            if user1.room_id == user2.room_id:
                room = user2.room_id
                old_room = Room.query.get(int(room))
                break

    return render_template("chat_friend.html", receiver=receiver, friends=friends, user=sender.username, room=old_room)

@app.route("/chat_page/messages", methods=["POST"])
def receive_messages():

    req = request.get_json()
    message = req['message']
    user_id = req['receiver_id']

    # Asssume their is a conversation
    receiver = User.query.get(user_id)
    sender = User.query.get(current_user.id)
    
    room = None
    
    for user1 in sender.user_participants:
        for user2 in receiver.user_participants:

            if user1.room_id == user2.room_id:
                room = user2.room_id
                break
    
    if room:
        old_room = Room.query.get(int(room))
        sender_message = Message(message=message, room_id=old_room.id, user_id=sender.id)

        db.session.add(sender_message)
        db.session.commit()

    else:

        new_room = Room(name="private_chat")
        db.session.add(new_room)
        db.session.commit()

        participant1 = Participants(user_id=sender.id, room_id=new_room.id)
        participant2 = Participants(user_id=receiver.id, room_id=new_room.id)
        db.session.add_all([participant1, participant2])
        db.session.commit()

        sender_message = Message(message=message, room_id=new_room.id, user_id=sender.id)
        db.session.add(sender_message)
        db.session.commit()

    return {}

# SocketIo

class MyCustomNamespace(Namespace):

    def on_connect(self):
        print("I am connected")

    def on_disconnect(self):
        pass

    def on_receiver_url(self, data):

        # friend_id = data.split('/')[-1]
        users[current_user.username] = request.sid
        print(users)
    
    def on_friend_chat(self, data):
        friend_url = data['user_id']
        friend_id = friend_url.split('/')[-1]
        receiver = User.query.get(friend_id)

        session_id = users[receiver.username]
        message = data['message']

        emit('my_custom_response', message, room=session_id)

socketio.on_namespace(MyCustomNamespace('/private'))

@socketio.on('join')
def join(data):

    join_room(data['room'])
    send({'msg':data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

@socketio.on('leave')
def leave(data):

    leave_room(data['room'])
    send({'msg':data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])

@socketio.on('send_messages')
def send_messages(data):

    emit('messages_send', {'msg':data['msg'], 'username':data['username']}, room=data['room'])