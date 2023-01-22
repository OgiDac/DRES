from Engine import  db
from flask_login import UserMixin

def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(length = 20), nullable = False)
    surname = db.Column(db.String(length = 20), nullable = False)
    address = db.Column(db.String(length = 20), nullable = False)
    city = db.Column(db.String(length = 20),  nullable = False)
    country = db.Column(db.String(length = 20),  nullable = False)
    phone = db.Column(db.String(length = 20), nullable = False, unique = True)
    email = db.Column(db.String(length = 20), nullable = False, unique = True)
    password = db.Column(db.String(length=60), nullable=False)
    verificated = db.Column(db.Boolean(),default=False, nullable=False)
    budget = db.Column(db.Integer(), default = 0)
    transactions = db.Column(db.PickleType())
    card = db.relationship("Card", backref = "owned_user", lazy = 'subquery')

    def __repr__(self):
        return f'User {self.email}'
    
    def __iter__(self):
        return iter([self.id, self.email, self.name, self.surname, self.address, self.city, self.country, self.phone, self.password, self.verificated, self.card])

    def check_password_correction(self, attempted_password):
        if self.password==attempted_password:
            return True
        else:
            return False 



class Card(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    number = db.Column(db.String(length = 20), nullable = False, unique = True)
    expire_date = db.Column(db.String(length = 10), nullable = False)
    code = db.Column(db.Integer(), nullable = False)
    budget = db.Column(db.Integer(), default = 1000)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    