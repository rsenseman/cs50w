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
    print(f'last channel: {session.get("last_page")}')
    return load_home()


def load_home(channel_select=None):
    data=dict()
    data['channel_names'] = get_channel_list()
    data['username'] = session['username']

    if channel_select:
        data['channel_select'] = channel_select
        session['last_page'] = channel_select
    elif session.get('last_page'):
        data['channel_select'] = session['last_page']
    else:
        data['channel_select'] = ''

    return render_template("home.html", data=data)


@app.route('/add_new_channel', methods=['POST'])
def add_new_channel():
    query = text('''INSERT INTO channels ("channel_name", "creator") VALUES (:channel_name, :creator);''')
    result = db.execute(query, {'channel_name': request.form.get('channel_name'), 'creator': session['username']})
    db.commit()
    print(db.execute('select * from channels').fetchall())
    return 'channel_added'


def get_channel_list():
    rows = db.execute('SELECT channel_name FROM channels ORDER BY time_added').fetchall()
    channel_names = [row['channel_name'] for row in rows]
    return channel_names


@app.route('/channel/<channel_name>', methods=['GET', 'POST'])
def get_channel_messages(channel_name):
    session['last_page'] = channel_name
    if request.method == 'POST':
        print(f'getting messages for {channel_name}')
        query = text("SELECT to_char(time_added, 'HH12:MI:SS AM'), username, message FROM messages WHERE channel=:channel_name ORDER BY time_added LIMIT 100")
        rows = db.execute(query, {'channel_name': channel_name}).fetchall()
        print([row.values() for row in rows])
        return jsonify({'messages': [row.values() for row in rows]})
    else:
        return load_home(channel_name)


@app.route('/submit_message', methods=['POST'])
def submit_message():
    query = text('''INSERT INTO messages ("time_added", "channel", "username", "message") VALUES (to_timestamp(:timestamp), :channel, :username, :message);''')
    result = db.execute(query, {
                                'timestamp': request.form.get('timestamp'),
                                'channel': request.form.get('channel_name'),
                                'username': session['username'],
                                'message': request.form.get('message_text'),
                                }
    )
    print(db.execute('select * from channels').fetchall())
    print(result)
    db.commit()
    return 'message_stored'


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
