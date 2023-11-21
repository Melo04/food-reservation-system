from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/parent')
@login_required
def parent():
    return render_template("parent/dashboard.html", parent=current_user)

@views.route('/worker')
@login_required
def worker():
    return render_template("worker/dashboard.html", worker=current_user)

@views.route('/student')
@login_required
def student():
    return render_template("student/dashboard.html", student=current_user)

@views.route('/admin')
@login_required
def admin():
    return render_template("admin/dashboard.html", admin=current_user)