from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'food recommendation system'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Parent, Worker, Student

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        parent = Parent.query.get(int(id))
        worker = Worker.query.get(int(id))
        student = Student.query.get(int(id))
        admin = Student.query.get(int(id))
        if parent:
            return parent
        elif worker:
            return worker
        elif student:
            return student
        elif admin:
            return admin
        else:
            return None
        
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path == '/parent' or request.path == '/parent_profile':
            return redirect(url_for('auth.parent_login'))
        elif request.path == '/worker' or request.path == '/worker_profile':
            return redirect(url_for('auth.worker_login'))
        elif request.path == '/student' or request.path == '/student_profile':
            return redirect(url_for('auth.student_login'))
        elif request.path == '/admin' or request.path == '/admin_profile':
            return redirect(url_for('auth.admin_login'))
    
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')