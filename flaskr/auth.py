import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId

from flaskr.db import get_db
from pymongo.errors import DuplicateKeyError

from flask import current_app

bp = Blueprint('auth', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            users = db['users']
            if users.find_one({'email': email}):
                error = f"Email {email} is already registered."
            elif users.find_one({'username': username}):
                error = f"Username {username} is already taken."
            else:
                try:
                    users.insert_one({
                        'username': username,
                        'email': email,
                        'password': generate_password_hash(password)
                    })
                    flash('Registration successful! Please log in.')
                    return redirect(url_for('auth.login'))
                except DuplicateKeyError:
                    error = f"User {username} or email {email} is already registered."

        flash(error)

    return render_template('auth/register.html')



@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db['users'].find_one({'email': email})

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            # Convert ObjectId to string before storing in session
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        # Convert string back to ObjectId when querying
        g.user = db['users'].find_one({'_id': ObjectId(user_id)})
    

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
