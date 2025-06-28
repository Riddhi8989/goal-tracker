from flask import Flask, render_template, request, redirect, url_for, flash
from models import StudyGoal, db, User
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Dummy function to simulate current user (replace with actual user logic later)
def get_current_user():
    return User.get_by_id(1)

@app.route('/goals/')
def list_goals():
    user = get_current_user()
    user_goals = StudyGoal.select().where(StudyGoal.user == user).order_by(StudyGoal.target_date.asc())
    return render_template('list.html', goals=user_goals)

@app.route('/goals/create', methods=('GET', 'POST'))
def create_goal():
    user = get_current_user()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        target_date_str = request.form['target_date']
        error = None

        if not title:
            error = 'Title is required.'
        elif not target_date_str:
            error = 'Target date is required.'

        if error is None:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                StudyGoal.create(
                    user=user,
                    title=title,
                    description=description,
                    target_date=target_date
                )
                flash('Goal created successfully!', 'success')
                return redirect(url_for('list_goals'))
            except ValueError:
                error = 'Invalid date format. Use YYYY-MM-DD.'
            except Exception as e:
                error = f'An error occurred: {e}'
        
        flash(error, 'danger')
    return render_template('create.html')

@app.route('/goals/<int:goal_id>/edit', methods=('GET', 'POST'))
def edit_goal(goal_id):
    user = get_current_user()
    try:
        goal = StudyGoal.get((StudyGoal.id == goal_id) & (StudyGoal.user == user))
    except StudyGoal.DoesNotExist:
        flash('Goal not found or you do not have permission.', 'danger')
        return redirect(url_for('list_goals'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        target_date_str = request.form['target_date']
        completed = 'completed' in request.form
        error = None

        if not title:
            error = 'Title is required.'
        elif not target_date_str:
            error = 'Target date is required.'

        if error is None:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                goal.title = title
                goal.description = description
                goal.target_date = target_date
                goal.completed = completed
                goal.save()
                flash('Goal updated successfully!', 'success')
                return redirect(url_for('list_goals'))
            except ValueError:
                error = 'Invalid date format. Use YYYY-MM-DD.'
            except Exception as e:
                error = f'An error occurred: {e}'
        
        flash(error, 'danger')
    return render_template('edit.html', goal=goal)

@app.route('/goals/<int:goal_id>/delete', methods=('GET', 'POST'))
def delete_goal(goal_id):
    user = get_current_user()
    try:
        goal = StudyGoal.get((StudyGoal.id == goal_id) & (StudyGoal.user == user))
    except StudyGoal.DoesNotExist:
        flash('Goal not found or you do not have permission.', 'danger')
        return redirect(url_for('list_goals'))

    if request.method == 'POST':
        goal.delete_instance()
        flash('Goal deleted successfully!', 'success')
        return redirect(url_for('list_goals'))

    return render_template('delete_confirm.html', goal=goal)

if __name__ == '__main__':
    app.run(debug=True)
