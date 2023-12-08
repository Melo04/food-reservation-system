from wtforms import FileField, Form,FloatField, IntegerField, SelectField,StringField, SubmitField,TextAreaField,validators 
from flask_wtf.file import FileAllowed

class MainCourses(Form):
    name = StringField('MainCourse', validators=[validators.DataRequired()])
    quantity = IntegerField('Quantity',validators=[validators.DataRequired()])
    remarks = StringField('Remarks', validators=[validators.DataRequired()])
    submit = SubmitField('Submit',validators=[validators.DataRequired()])

class Beverages(Form):
    name = StringField('Beverage', validators=[validators.DataRequired()])
    quantity = IntegerField('Quantity',validators=[validators.DataRequired()])
    remarks = StringField('Remarks', validators=[validators.DataRequired()])
    submit = SubmitField('Submit',validators=[validators.DataRequired()])

class Menus(Form):
    name = StringField('Menu', validators=[validators.DataRequired()])
    price = FloatField('Price', validators=[validators.DataRequired()])
    type = StringField('Type', validators=[validators.DataRequired()])
    desc = TextAreaField('Description', validators=[validators.DataRequired()])
    main_course=SelectField('Main Course',coerce=int, validators=[validators.DataRequired()])
    beverage=SelectField('Beverage',coerce=int, validators=[validators.DataRequired()])
    picture = FileField('Menu Picture', validators=[FileAllowed(['jpg', 'png'],'Only images allowed')])
    submit = SubmitField('Submit',validators=[validators.DataRequired()])
    