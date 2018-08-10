from functools import wraps
from flask import Flask, session, jsonify, render_template, request, redirect, url_for

def login_required(f):
    '''function taken from CS50 login_required'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def render_error(code, message):
    return render_template('error.html', code=code, message=message)
