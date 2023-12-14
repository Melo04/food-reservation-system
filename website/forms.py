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
    parent1_id = StringField('Parent1Id (for student)')
    parent2_id = StringField('Parent2Id (for student)')
    status = StringField('Status (for student)')
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(USERNAME=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(EMAIL=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_username(self, username):
        user = User.query.filter_by(USERNAME=username.data).first()
        if not user:
            raise ValidationError('That username does not exist. Please choose a different one.')
        
    def validate_password(self, password):
        user = User.query.filter_by(USERNAME=self.username.data).first()
        if user and not bcrypt.check_password_hash(user.PASSWORD, password.data):
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
    ewallet_balance = FloatField('E-Wallet Balance')
    status = StringField('Status')
    parent_id = StringField('ParentId (if student)')
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        if username.data != current_user.USERNAME:
            user = User.query.filter_by(USERNAME=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.EMAIL:
            user = User.query.filter_by(EMAIL=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            
    def validate_phone(self, phone):
        if phone.data != current_user.PHONE:
            user = User.query.filter_by(PHONE=phone.data).first()
            if user:
                raise ValidationError('That phone is taken. Please choose a different one.')

class AdminUpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    status = SelectField('Status', choices=[('active', 'active'), ('inactive', 'inactive')])
    submit = SubmitField('Update Student Status')

class AdminUpdateMenuForm(FlaskForm):
    set = StringField('Menu', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'public'), ('private', 'private'), ('pending', 'pending')])
    submit = SubmitField('Update Menu')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(EMAIL=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Main Course', 'Main Course'), ('Beverage', 'Beverage')])
    quantity = IntegerField('Quantity',validators=[DataRequired()])
    remarks = StringField('Remarks', validators=[DataRequired()])
    submit = SubmitField('Add Food Item',validators=[DataRequired()])

class UpdateItemForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    name = StringField('Food Item', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Main Course', 'Main Course'), ('Beverage', 'Beverage')])
    quantity = IntegerField('Quantity',validators=[DataRequired()])
    remarks = StringField('Remarks', validators=[DataRequired()])
    submit = SubmitField('Update Food Item',validators=[DataRequired()])

class MenuForm(FlaskForm):
    set = StringField('Menu', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Chinese', 'Chinese'), ('Western', 'Western'), ('Japanese', 'Japanese'), ('Malay Cuisines', 'Malay Cuisines'), ('Indian Cuisines', 'Indian Cuisines')])
    desc = TextAreaField('Description', validators=[DataRequired()])
    visibility=SelectField('Visibility',choices=[('private','private'),('pending','set to public')])
    main_course = SelectField('Main Course', coerce=int, validators=[DataRequired()])
    beverage = SelectField('Beverage', coerce=int, validators=[DataRequired()])
    picture = FileField('Menu Image File', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Menu',validators=[DataRequired()])

class UpdateMenuForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    set = StringField('Menu', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Chinese', 'Chinese'), ('Western', 'Western'), ('Japanese', 'Japanese'), ('Malay Cuisines', 'Malay Cuisines'), ('Indian Cuisines', 'Indian Cuisines')])
    desc = TextAreaField('Description', validators=[DataRequired()])
    visibility=SelectField('Visibility',choices=[('private','private'),('pending','set to public')])
    main_course = SelectField('Main Course', coerce=int, validators=[DataRequired()])
    beverage = SelectField('Beverage',coerce=int, validators=[DataRequired()])
    picture = FileField('Menu Image File', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Menu',validators=[DataRequired()])