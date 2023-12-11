from datetime import datetime
from website import db, login_manager, app
from flask_login import UserMixin
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firstname = db.Column(db.String(20), unique=True, nullable=False)
    lastname = db.Column(db.String(20))
    phone = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20))
    parent_id = db.Column(db.String(20))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.firstname}', '{self.lastname}', '{self.phone}', '{self.image_file}', '{self.role}', '{self.status}', '{self.parent_id}')"
    
class MainCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    remarks=db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Main Course('{self.name},'{self.quantity}','{self.remarks}')"

class Beverage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    remarks=db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Beverage('{self.name},'{self.quantity}','{self.remarks}')"

class Menu(db.Model):
    __searchable__ = ['name', 'desc']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(30), default='default_menu.jpg')
    visibility = db.Column(db.String(20), nullable=False, default='public')

    main_course_id = db.Column(db.Integer, db.ForeignKey('main_course.id'), nullable=False)
    main_course = db.relationship('MainCourse', backref='menu') 

    beverage_id = db.Column(db.Integer, db.ForeignKey('beverage.id'), nullable=False)
    beverage = db.relationship('Beverage', backref='menu')

    def __repr__(self):
        return f"Menu('{self.name},'{self.price}','{self.type}','{self.desc}', '{self.image_file}', '{self.visibility}')"