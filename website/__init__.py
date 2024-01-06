from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
import os
import stripe

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '397a6521b760efeb6144b9705bf7fabc'
if os.environ.get("DATABASE_URL") is None:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL").replace("://", "ql://", 1)
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category='info'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
stripe.api_key = app.config['STRIPE_SECRET_KEY']

mail = Mail(app)

from website.routes.main import main
from website.routes.parent import parent
from website.routes.student import student
from website.routes.worker import worker
from website.routes.admin import admin

app.register_blueprint(main)
app.register_blueprint(parent)
app.register_blueprint(student)
app.register_blueprint(worker)
app.register_blueprint(admin)