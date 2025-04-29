from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash
from bson.objectid import ObjectId
from datetime import datetime
from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('todos', __name__, url_prefix='/todos')

@bp.route('/')
@login_required
def index():
    db = get_db()
    todos = db['todos'].find({'user_id': g.user['_id']}).sort('created_at', -1)
    return render_template('todos/index.html', todos=todos)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        due_date = request.form.get('due_date')
        db = get_db()
        todo = {
            'user_id': g.user['_id'],
            'title': title,
            'description': description,
            'due_date': due_date if due_date else None,
            'completed': False,
            'created_at': datetime.utcnow()
        }
        db['todos'].insert_one(todo)
        flash('To-Do added!')
        return redirect(url_for('todos.index'))
    return render_template('todos/add_edit.html', action='Add')

@bp.route('/edit/<todo_id>', methods=['GET', 'POST'])
@login_required
def edit(todo_id):
    db = get_db()
    todo = db['todos'].find_one({'_id': ObjectId(todo_id), 'user_id': g.user['_id']})
    if not todo:
        flash('To-Do not found.')
        return redirect(url_for('todos.index'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        due_date = request.form.get('due_date')
        completed = 'completed' in request.form
        db['todos'].update_one({'_id': ObjectId(todo_id)}, {'$set': {
            'title': title,
            'description': description,
            'due_date': due_date if due_date else None,
            'completed': completed
        }})
        flash('To-Do updated!')
        return redirect(url_for('todos.index'))
    return render_template('todos/add_edit.html', action='Edit', todo=todo)

@bp.route('/delete/<todo_id>', methods=['POST'])
@login_required
def delete(todo_id):
    db = get_db()
    db['todos'].delete_one({'_id': ObjectId(todo_id), 'user_id': g.user['_id']})
    flash('To-Do deleted!')
    return redirect(url_for('todos.index'))

@bp.route('/toggle/<todo_id>', methods=['POST'])
@login_required
def toggle(todo_id):
    db = get_db()
    todo = db['todos'].find_one({'_id': ObjectId(todo_id), 'user_id': g.user['_id']})
    if todo:
        db['todos'].update_one({'_id': ObjectId(todo_id)}, {'$set': {'completed': not todo['completed']}})
        flash('To-Do status updated!')
    return redirect(url_for('todos.index'))
