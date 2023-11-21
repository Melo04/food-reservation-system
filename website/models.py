from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Parent(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date = db.Column(db.DateTime(timezone=True), default=func.now())

class Worker(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date = db.Column(db.DateTime(timezone=True), default=func.now())

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    studentid = db.Column(db.Integer, unique=True) 
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date = db.Column(db.DateTime(timezone=True), default=func.now())

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')