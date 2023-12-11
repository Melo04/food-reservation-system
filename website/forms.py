from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from website.models import User
from website import bcrypt

class RegistrationForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name')
    phone = StringField('Phone', validators=[Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    parent_id = StringField('ParentId (for student)')
    status = StringField('Status (for parent and student)')
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('That username does not exist. Please choose a different one.')
        
    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError('Incorrect password. Please try again.')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name')
    phone = StringField('Phone', validators=[DataRequired(), Length(min=2, max=20)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    parent_id = StringField('ParentId (if student)')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            
    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('That phone is taken. Please choose a different one.')

class AdminUpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    status = SelectField('Status', choices=[('active', 'active'), ('inactive', 'inactive')])
    submit = SubmitField('Update User')

class AdminUpdateMenuForm(FlaskForm):
    name = StringField('Menu', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'public'), ('private', 'private'), ('pending', 'pending')])
    submit = SubmitField('Update Menu')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class MainCourses(FlaskForm):
    name = StringField('MainCourse', validators=[DataRequired()])
    quantity = IntegerField('Quantity',validators=[DataRequired()])
    remarks = StringField('Remarks', validators=[DataRequired()])
    submit = SubmitField('Add Main Course',validators=[DataRequired()])

class UpdateMainCourses(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    name = StringField('MainCourse', validators=[DataRequired()])
    quantity = IntegerField('Quantity',validators=[DataRequired()])
    remarks = StringField('Remarks', validators=[DataRequired()])
    submit = SubmitField('Update Main Course',validators=[DataRequired()])

class Beverages(FlaskForm):
    name = StringField('Beverage', validators=[DataRequired()])
    quantity = IntegerField('Quantity',validators=[DataRequired()])
    remarks = StringField('Remarks', validators=[DataRequired()])
    submit = SubmitField('Add Beverage',validators=[DataRequired()])

class UpdateBeverages(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    name = StringField('Beverage', validators=[DataRequired()])
    quantity = IntegerField('Quantity',validators=[DataRequired()])
    remarks = StringField('Remarks', validators=[DataRequired()])
    submit = SubmitField('Update Beverage',validators=[DataRequired()])

class Menus(FlaskForm):
    name = StringField('Menu', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    main_course=SelectField('Main Course',coerce=int, validators=[DataRequired()])
    beverage=SelectField('Beverage',coerce=int, validators=[DataRequired()])
    visibility=SelectField('Visibility',choices=[('private','private'),('pending','set to public')])
    picture = FileField('Menu Image File', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Menu',validators=[DataRequired()])

class UpdateMenus(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    name = StringField('Menu', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    main_course=SelectField('Main Course',coerce=int, validators=[DataRequired()])
    beverage=SelectField('Beverage',coerce=int, validators=[DataRequired()])
    visibility=SelectField('Visibility',choices=[('private','private'),('pending','set to public')])
    picture = FileField('Menu Image File', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Menu',validators=[DataRequired()])