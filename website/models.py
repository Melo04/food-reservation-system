from datetime import datetime
from website import db, login_manager, app
from flask_login import UserMixin
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    USERNAME = db.Column(db.String(20), unique=True, nullable=False)
    FIRST_NAME = db.Column(db.String(20), unique=True, nullable=False)
    LAST_NAME = db.Column(db.String(20))
    EMAIL = db.Column(db.String(120), unique=True, nullable=False)
    PASSWORD = db.Column(db.String(60), nullable=False)
    PHONE = db.Column(db.String(20), nullable=False)
    ROLE = db.Column(db.String(20), nullable=False)
    IMAGE = db.Column(db.String(20), nullable=False, default='default.png')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            USER_ID = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(USER_ID)

    def __repr__(self):
        return f"User('{self.USERNAME}', '{self.EMAIL}', '{self.FIRST_NAME}', '{self.LAST_NAME}', '{self.PHONE}', '{self.IMAGE}', '{self.ROLE}')"
    
class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    STATUS = db.Column(db.String(20), nullable=False)
    PARENT1_ID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    PARENT2_ID = db.Column(db.Integer, db.ForeignKey('user.id'))

    __mapper_args__ = {
        'inherit_condition': (id == User.id)
    }

    def __repr__(self):
        return f"Student('{self.USERNAME}', '{self.EMAIL}', '{self.FIRST_NAME}', '{self.LAST_NAME}', '{self.PHONE}', '{self.IMAGE}', '{self.ROLE}', '{self.STATUS}', '{self.PARENT1_ID}', '{self.PARENT2_ID}')"
    
class Parent(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    EWALLET_BALANCE = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"Parent('{self.USERNAME}', '{self.EMAIL}', '{self.FIRST_NAME}', '{self.LAST_NAME}', '{self.PHONE}', '{self.IMAGE}', '{self.ROLE}', '{self.EWALLET_BALANCE}')"

class Worker(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True , nullable=False)

    def __repr__(self):
        return f"Worker('{self.USERNAME}', '{self.EMAIL}', '{self.FIRST_NAME}', '{self.LAST_NAME}', '{self.PHONE}', '{self.IMAGE}', '{self.ROLE}')"

class Admin(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Admin('{self.USERNAME}', '{self.EMAIL}', '{self.FIRST_NAME}', '{self.LAST_NAME}', '{self.PHONE}', '{self.IMAGE}', '{self.ROLE}')"
    
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    NAME = db.Column(db.String(20), unique=True, nullable=False)
    TYPE = db.Column(db.String(20), nullable=False)
    QUANTITY = db.Column(db.Integer,nullable=False)
    REMARKS = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"FoodItem('{self.NAME},'{self.TYPE}','{self.QUANTITY}','{self.REMARKS}')"

class FoodMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    SET = db.Column(db.String(20), nullable=False)
    PRICE = db.Column(db.Numeric(10, 2), nullable=False)
    TYPE = db.Column(db.String(20), nullable=False)
    DESCRIPTION = db.Column(db.Text, nullable=False)
    VISIBILITY = db.Column(db.String(20), nullable=False, default='private')
    IMAGE = db.Column(db.String(30), default='default_menu.jpg')
    MAIN_COURSE_ID = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False)
    MAIN_COURSE = db.relationship('FoodItem', foreign_keys=[MAIN_COURSE_ID])
    BEVERAGE_ID = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False)
    BEVERAGE = db.relationship('FoodItem', foreign_keys=[BEVERAGE_ID])

    def __repr__(self):
        return f"FoodMenu('{self.SET},'{self.PRICE}','{self.TYPE}','{self.DESCRIPTION}','{self.VISIBILITY}','{self.IMAGE}', '{self.MAIN_COURSE_ID}', '{self.BEVERAGE_ID}')"
    
class FoodOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    ORDER_DAY = db.Column(db.String(20), nullable=False)
    REDEMPTION = db.Column(db.Boolean, nullable=False, default=False)
    MENU_ID = db.Column(db.Integer, db.ForeignKey('food_menu.id'), nullable=False)
    PARENT_ID = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    STUDENT_ID = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    TRANSACTION_ID = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)

    menu = db.relationship('FoodMenu', backref='order')
    parent = db.relationship('Parent', backref='parent_orders', foreign_keys=[PARENT_ID])
    student = db.relationship('Student', backref='student_orders', foreign_keys=[STUDENT_ID])
    transaction = db.relationship('Transaction', backref='order')

    def __repr__(self):
        return f"FoodOrder('{self.ORDER_DAY},'{self.REDEMPTION}','{self.MENU_ID}','{self.PARENT_ID}','{self.STUDENT_ID}','{self.TRANSACTION_ID}')"
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    PARENT_ID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    AMOUNT = db.Column(db.Numeric(10, 2), nullable=False)
    DATE_TIME = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Transaction('{self.PARENT_ID},'{self.AMOUNT}','{self.DATE_TIME}')"
    
class Reload(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    PARENT_ID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    AMOUNT = db.Column(db.Numeric(10, 2), nullable=False)
    DATE_TIME = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Reload('{self.PARENT_ID},'{self.AMOUNT}','{self.DATE_TIME}')"
    
class Payout(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    ADMIN_ID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    AMOUNT = db.Column(db.Numeric(10, 2), nullable=False)
    DATE_TIME = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Payout('{self.ADMIN_ID},'{self.AMOUNT}','{self.DATE_TIME}')"
    
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    PARENT_ID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    MENU_ID = db.Column(db.Integer, db.ForeignKey('food_menu.id'), nullable=False)

    def __repr__(self):
        return f"Payout('{self.PARENT_ID},'{self.MENU_ID}')"
