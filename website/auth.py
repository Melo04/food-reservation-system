from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from .models import Parent, Worker, Student, Admin
from . import db

auth = Blueprint('auth', __name__)
app = Flask(__name__)
bcrypt = Bcrypt()

@auth.route('/parent_login', methods=['GET', 'POST'])
def parent_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        parent = Parent.query.filter_by(email=email).first()
        if parent:
            if bcrypt.check_password_hash(parent.password, password):
                flash('Logged in successfully!', category='success')
                login_user(parent, remember=True)
                return redirect(url_for('views.parent'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("parent/login.html", parent=current_user)

@auth.route('/worker_login', methods=['GET', 'POST'])
def worker_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        worker = Worker.query.filter_by(email=email).first()
        if worker:
            if bcrypt.check_password_hash(worker.password, password):
                flash('Logged in successfully!', category='success')
                login_user(worker, remember=True)
                return redirect(url_for('views.worker'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("worker/login.html", worker=current_user)

@auth.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        studentid = request.form.get('studentid')
        password = request.form.get('password')

        student = Student.query.filter_by(studentid=studentid).first()
        if student:
            if bcrypt.check_password_hash(student.password, password):
                flash('Logged in successfully!', category='success')
                login_user(student, remember=True)
                return redirect(url_for('views.student'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Student ID does not exist.', category='error')

    return render_template("student/login.html", student=current_user)

@auth.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if bcrypt.check_password_hash(admin.password, password):
                flash('Logged in successfully!', category='success')
                login_user(admin, remember=True)
                return redirect(url_for('views.admin'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("admin/login.html", admin=current_user)

@auth.route('/parent_signup', methods=['GET', 'POST'])
def parent_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        parent = Parent.query.filter_by(email=email).first()
        if parent:
            flash('Email already exists.', category='error')
        if len(email) < 6:
            flash('Email must be greater than 5 characters.', category='error')
        elif len(firstName) < 3:
            flash('First name must be greater than 2 characters.', category='error')
        elif len(lastName) < 3:
            flash('Last name must be greater than 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_parent = Parent(email=email, firstName=firstName, lastName=lastName, password=bcrypt.generate_password_hash(password1).decode('utf-8'))
            db.session.add(new_parent)
            db.session.commit()
            login_user(new_parent)
            flash('Account created!', category='success')
            return redirect(url_for('views.parent'))

    return render_template("parent/signup.html", parent=current_user)

@auth.route('/worker_signup', methods=['GET', 'POST'])
def worker_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        worker = Worker.query.filter_by(email=email).first()
        if worker:
            flash('Email already exists.', category='error')
        if len(email) < 6:
            flash('Email must be greater than 5 characters.', category='error')
        elif len(firstName) < 3:
            flash('First name must be greater than 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_worker = Worker(email=email, firstName=firstName, password=bcrypt.generate_password_hash(password1).decode('utf-8'))
            db.session.add(new_worker)
            db.session.commit()
            login_user(new_worker, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.worker'))

    return render_template("worker/signup.html", worker=current_user)

@auth.route('/student_signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        studentid = request.form.get('studentid')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        student = Student.query.filter_by(studentid=studentid).first()
        if student:
            flash('Student ID already exists.', category='error')
        if len(email) < 6:
            flash('Email must be greater than 5 characters.', category='error')
        elif len(studentid) < 1:
            flash('Student ID is required.', category='error')
        elif len(firstName) < 3:
            flash('First name must be greater than 2 characters.', category='error')
        elif len(lastName) < 3:
            flash('Last name must be greater than 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_student = Student(email=email, studentid=studentid, firstName=firstName, lastName=lastName, password=bcrypt.generate_password_hash(password1).decode('utf-8'))
            db.session.add(new_student)
            db.session.commit()
            login_user(new_student, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.student'))

    return render_template("student/signup.html", student=current_user)

@auth.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        admin = Admin.query.filter_by(username=username).first()
        if admin:
            flash('Email already exists.', category='error')
        if len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif len(name) < 3:
            flash('First name must be greater than 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_admin = Admin(username=username, name=name, password=bcrypt.generate_password_hash(password1).decode('utf-8'))
            db.session.add(new_admin)
            db.session.commit()
            login_user(new_admin, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.admin'))

    return render_template("admin/signup.html", admin=current_user)

@auth.route('/parent_logout')
@login_required
def parent_logout():
    logout_user()
    return redirect(url_for('auth.parent_login'))

@auth.route('/worker_logout')
@login_required
def worker_logout():
    logout_user()
    return redirect(url_for('auth.worker_login'))

@auth.route('/student_logout')
@login_required
def student_logout():
    logout_user()
    return redirect(url_for('auth.student_login'))

@auth.route('/admin_logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login'))

@auth.route('/parent_profile')
@login_required
def parent_profile():
    return render_template("parent/profile.html", parent=current_user)

@auth.route('/worker_profile')
@login_required
def worker_profile():
    return render_template("worker/profile.html", worker=current_user)

@auth.route('/student_profile')
@login_required
def student_profile():
    return render_template("student/profile.html", student=current_user)

@auth.route('/admin_profile')
@login_required
def admin_profile():
    return render_template("admin/profile.html", admin=current_user)