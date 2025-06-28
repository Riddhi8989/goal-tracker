import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from ai_utils import generate_goal_suggestions
from models import db, create_tables, User, StudyGoal

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_super_secret_key_for_dev')

# ---------------------------- Database Hooks ---------------------------- #
@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    if not db.is_closed():
        db.close()
    return response

# ---------------------------- Helpers ---------------------------- #
def get_current_user():
    user_id = session.get('user_id')
    return User.get_or_none(User.id == user_id)

# ---------------------------- Home / Dashboard ---------------------------- #
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = get_current_user()
    if not user:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    suggestions = []
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            suggestions = generate_goal_suggestions(prompt)

    avatar_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={user.username}"
    return render_template('dashboard.html', user=user, avatar_url=avatar_url, suggestions=suggestions)

# ---------------------------- Auth Routes ---------------------------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password or password != confirm_password:
            flash('Invalid input or passwords do not match.', 'danger')
        elif User.get_or_none(User.username == username):
            flash('Username already exists.', 'danger')
        else:
            User.create(username=username, password=generate_password_hash(password))
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_or_none(User.username == username)

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------------------------- Goal CRUD ---------------------------- #
@app.route('/goals')
def view_goals():
    user = get_current_user()
    if not user:
        flash('Please log in to view your goals.', 'warning')
        return redirect(url_for('login'))

    goals = StudyGoal.select().where(StudyGoal.user == user)
    return render_template('goals.html', goals=goals, user=user)

@app.route('/goals/add', methods=['GET', 'POST'])
def add_goal():
    user = get_current_user()
    if not user:
        flash('Please log in to add goals.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        target_date_str = request.form.get('target_date')

        if not title or not target_date_str:
            flash('Title and target date are required.', 'danger')
        else:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                StudyGoal.create(user=user, title=title, description=description, target_date=target_date)
                flash('Goal added successfully!', 'success')
                return redirect(url_for('view_goals'))
            except Exception as e:
                flash(f'Error adding goal: {e}', 'danger')

    return render_template('create.html')

@app.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
def edit_goal(goal_id):
    user = get_current_user()
    goal = StudyGoal.get_or_none((StudyGoal.id == goal_id) & (StudyGoal.user == user))
    if not goal:
        flash('Goal not found or permission denied.', 'danger')
        return redirect(url_for('view_goals'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        target_date_str = request.form['target_date']
        completed = 'completed' in request.form

        if not title or not target_date_str:
            flash('Title and target date are required.', 'danger')
        else:
            try:
                goal.title = title
                goal.description = description
                goal.target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                goal.completed = completed
                goal.save()
                flash('Goal updated successfully!', 'success')
                return redirect(url_for('view_goals'))
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')

    return render_template('edit.html', goal=goal)

@app.route('/goals/<int:goal_id>/delete', methods=['GET', 'POST'])
def delete_goal(goal_id):
    user = get_current_user()
    goal = StudyGoal.get_or_none((StudyGoal.id == goal_id) & (StudyGoal.user == user))
    if not goal:
        flash('Goal not found or permission denied.', 'danger')
        return redirect(url_for('view_goals'))

    if request.method == 'POST':
        goal.delete_instance()
        flash('Goal deleted successfully!', 'success')
        return redirect(url_for('view_goals'))

    return render_template('delete_confirm.html', goal=goal)

# ---------------------------- Save AI Suggestion ---------------------------- #
@app.route('/save_suggestion', methods=['POST'])
def save_suggestion():
    user = get_current_user()
    if not user:
        flash("Please log in to save suggestions.", "warning")
        return redirect(url_for('login'))

    suggestion_text = request.form.get('suggestion')
    target_date = date.today() + timedelta(days=7)

    StudyGoal.create(user=user, title=suggestion_text, target_date=target_date)
    flash("AI suggestion saved as a goal!", "success")
    return redirect(url_for('dashboard'))

# ---------------------------- App Runner ---------------------------- #
if __name__ == '__main__':
    print("🔧 Initializing Database...")
    db.connect()
    create_tables()
    db.close()
    print("✅ Ready. Starting app...")
    app.run(debug=True)
