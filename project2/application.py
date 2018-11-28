import os

from flask import Flask, request, session, render_template, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('username'):
        return redirect("/login")
    print(f'logged in as {session["username"]}')
    return render_template("home.html", username=session['username'])

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
