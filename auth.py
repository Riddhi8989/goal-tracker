from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User  # Peewee model

def register_route(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                try:
                    hashed_password = generate_password_hash(password)
                    User.create(username=username, password=hashed_password)
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    error = f'Username {username} is already taken or error occurred: {e}'

            flash(error, 'danger')
        return render_template('register.html')


def login_route(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            try:
                user = User.get(User.username == username)
                if not check_password_hash(user.password, password):
                    error = 'Incorrect username or password.'
            except User.DoesNotExist:
                user = None
                error = 'Incorrect username or password.'

            if error is None:
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))

            flash(error, 'danger')
        return render_template('login.html')


def logout_route(app):
    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
