import os

from flask import Flask, request, session, render_template, redirect, jsonify
from flask_socketio import SocketIO, emit

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

if not os.getenv('DATABASE_URL_FLACK'):
    raise RuntimeError('DATABASE_URL is not set')

# Set up database
engine = create_engine(os.getenv('DATABASE_URL_FLACK'))
db = scoped_session(sessionmaker(bind=engine))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('username'):
        return redirect("/login")
    print(f'logged in as {session["username"]}')

    data=dict()
    data['channel_names'] = get_channel_list()
    data['username'] = session['username']
    return render_template("home.html", data=data)

def get_channel_list():
    rows = db.execute('SELECT name FROM channels ORDER BY time_added').fetchall()
    channel_names = [row['name'] for row in rows]
    return channel_names

def get_messages(channel_name):
    query = text('SELECT * FROM messages WHERE channel=:channel_name ORDER BY time_added')
    rows = db.execute(query, {'channel_name': channel_name}).fetchall()
    return rows

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Log user in'''
    # clear any user data
    session.clear()

    if request.method == 'POST':
        # Ensure username was submitted
        if not request.form.get('username'):
            return redirect("/login")

        # Remember which user has logged in
        session["username"] = request.form.get('username')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
