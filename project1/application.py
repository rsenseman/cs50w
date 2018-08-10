from datetime import datetime
import json
import os
import sys

from flask import Flask, session, jsonify, render_template, redirect, request
from flask_session import Session
from helpers import login_required, render_error
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from urllib.request import urlopen
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv('DATABASE_URL'):
    raise RuntimeError('DATABASE_URL is not set')

if not os.getenv('GOODREADS_KEY'):
    raise RuntimeError('GOODREADS_KEY is not set')
goodreads_key = os.getenv('GOODREADS_KEY')

# Configure session to use filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set up database
engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        query = text('''
            SELECT *
            FROM books
            WHERE
                LOWER(isbn) LIKE :search_term
                OR LOWER(title) LIKE :search_term
                OR LOWER(author) LIKE :search_term
                OR CAST(year AS VARCHAR) LIKE :search_term
        ''')

        search_term = request.form.get('search_term')
        if search_term:
            search_term = '%' + search_term.lower() + '%'
            rows = db.execute(query, {'search_term': search_term}).fetchall()
        return render_template("homesearch.html", results=rows[:20])

    return render_template("homesearch.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Log user in'''
    # clear any user data
    session.clear()

    if request.method == 'POST':
        # Ensure username was submitted
        if not request.form.get('username'):
            return render_error(403, 'must provide username')

        # Ensure password was submitted
        elif not request.form.get('password'):
            return render_error(403, 'must provide password')

        # Query database for username
        query = text("SELECT * FROM users WHERE username = :username")
        rows = db.execute(query, {'username': request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            return render_error(403, 'invalid username and/or password')

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # if post, register the user and redirect to the home page, if get then show registration form
    if request.method == "POST":
        username=request.form.get("username")

        query = text("SELECT * FROM users WHERE username=:username;")
        results = db.execute(query, {'username': username}).fetchall()

        if len(results) > 0:
            return render_error(403, 'username taken')

        password=request.form.get("password")
        password_confirmation=request.form.get("confirmation")

        if username=='' or password=='' or password_confirmation=='':
            return render_error(403, 'All fields must be filled out')

        if password != password_confirmation:
            del password
            del password_confirmation
            return render_error(403, 'Password and confirmation must match')
            # return render_template("register.html", mismatch=True)
        password_hash = generate_password_hash(password)
        del password

        query = text('INSERT INTO users (username, password_hash) VALUES (:username, :password_hash);')
        db.execute(query, {'username': username, 'password_hash': password_hash})
        db.commit()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route('/book/<isbn>', methods=["GET", "POST"])
@login_required
def book(isbn):
    if request.method == "POST":
        query = text('''INSERT INTO reviews
                        (user_id, book_isbn, review_text, review_stars, date_created)
                    VALUES
                        (:user_id, :book_isbn, :review_text, :review_stars, :date_created);
                    ''')

        right_now = datetime.now()
        right_now = datetime.strftime(right_now, '%Y-%m-%d')

        db.execute(query, {
            'user_id': request.form.get('user_id'),
            'book_isbn': request.form.get('book_isbn'),
            'review_text': request.form.get('review_text'),
            'review_stars': int(request.form.get('review_stars')),
            'date_created': right_now
        })
        db.commit()

    query = text("SELECT isbn, title, author, year FROM books WHERE isbn=:isbn;")
    book_info = db.execute(query, {'isbn': isbn}).fetchone()
    db.commit()

    query = text('''
        SELECT
            reviews.user_id
            ,reviews.book_isbn
            ,reviews.review_text
            ,reviews.review_stars
            ,reviews.date_created
            ,users.username
        FROM reviews
        JOIN users ON users.user_id = reviews.user_id
        WHERE reviews.book_isbn = :isbn
        ORDER BY reviews.date_created DESC;
    ''')
    reviews = db.execute(query, {'isbn': isbn}).fetchall()
    db.commit()

    query = text('''
        SELECT
            *
        FROM reviews
        WHERE
            book_isbn = :isbn
            AND user_id = :user_id
    ''')
    user_review = db.execute(query, {'isbn': isbn, 'user_id': session['user_id']}).fetchone()
    db.commit()

    user_has_reviewed = user_review is not None

    goodreads_data = urlopen(f"https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key={goodreads_key}").read()
    goodreads_data = json.loads(goodreads_data)
    goodreads_data = goodreads_data['books'][0]
    goodreads_data = {
        'ratings_count': goodreads_data['work_ratings_count'],
        'average_rating': goodreads_data['average_rating']

    }

    return render_template(
        "book_details.html",
        book_info=book_info,
        reviews=reviews,
        userid=session["user_id"],
        goodreads_data=goodreads_data,
        user_has_reviewed=user_has_reviewed
    )

@app.route('/api/<isbn>')
def api(isbn):

    query = text('''
        SELECT
            isbn
            ,title
            ,author
            ,year
        FROM books
        WHERE isbn=:isbn
    ''')
    book_info = db.execute(query, {'isbn': isbn}).fetchone()
    db.commit()

    if book_info is None:
        return render_error(404, 'book not found in database')

    query = text('''
        SELECT
            CAST(COALESCE(AVG(reviews.review_stars), 0) AS VARCHAR) average_score
            ,CAST(COALESCE(COUNT(*), 0) AS VARCHAR) review_count
        FROM reviews
        WHERE book_isbn=:isbn
    ''')
    review_info = db.execute(query, {'isbn': isbn}).fetchone()
    db.commit()

    return jsonify(title=book_info['title'],
                   author=book_info['author'],
                   year=book_info['year'],
                   isbn=book_info['isbn'],
                   review_count=review_info['review_count'],
                   average_score=review_info['average_score'][:3],
                   )
