from wtforms import FileField, Form,FloatField,StringField,TextAreaField,validators 
from flask_wtf.file import FileAllowed

class Addmenus(Form):
    name = StringField('Menu', [validators.DataRequired()])
    price = FloatField('Price', [validators.DataRequired()])
    type = StringField('Type', [validators.DataRequired()])
    desc = TextAreaField('Description', [validators.DataRequired()])
    picture = FileField('Menu Picture', validators=[FileAllowed(['jpg', 'png'],'Only images allowed')])