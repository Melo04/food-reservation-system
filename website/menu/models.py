from website import db,app

class Addmenu(db.Model):
    __searchbale__ = ['name','desc']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    type = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,default='default_menu.jpg')

    def __repr__(self):
        return '<Menu %r>' % self.name

with app.app_context():
    db.create_all()