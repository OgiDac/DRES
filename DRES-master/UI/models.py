import pickle
import requests
from UI import login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    response =  requests.get('http://localhost:5001/getuser',data=user_id)
    attempted_user = pickle.loads(response.content)
    # card_response = requests.get('http://localhost:5001/getcardbyowner', data = str(attempted_user.id))
    # if response.content == b'false':
    #     pass
    # else:
    #     card = pickle.loads(card_response.content)
    #     attempted_user.card[0] = card
    return attempted_user

class User:

    def __init__(self, name, surname, address, city, country, phone, email, password):
        self.name = name
        self.surname = surname
        self.address = address
        self.city = city
        self.country = country
        self.phone = phone
        self.email = email
        self.password = password
        self.card = Card
        self.transactions = []

    # id = db.Column(db.Integer(), primary_key = True)
    # name = db.Column(db.String(length = 20), nullable = False)
    # surname = db.Column(db.String(length = 20), nullable = False)
    # address = db.Column(db.String(length = 20), nullable = False)
    # city = db.Column(db.String(length = 20),  nullable = False)
    # country = db.Column(db.String(length = 20),  nullable = False)
    # phone = db.Column(db.String(length = 20), nullable = False, unique = True)
    # email = db.Column(db.String(length = 20), nullable = False, unique = True)
    # password = db.Column(db.String(length=60), nullable=False)
    # verificated=db.Column(db.Boolean(),default=False, nullable=False)
    # card = db.relationship("Card", backref = "owned_user", lazy = True)

    def __repr__(self):
        return f'User {self.email}'
    
    def __iter__(self):
        return iter([self.id, self.email, self.name, self.surname, self.address, self.city, self.country, self.phone, self.password, self.verificated, self.card])

    def check_password_correction(self, attempted_password):
        if self.password==attempted_password:
            return True
        else:
            return False 



class Card():

    def __init__(self,number, owner, expire_date, code):
        self.id = id
        self.owner = owner
        self.number = number
        self.expire_date = expire_date
        self.code = code
    # id = db.Column(db.Integer(), primary_key = True)
    # number = db.Column(db.String(length = 20), nullable = False, unique = True)
    # expire_date = db.Column(db.String(length = 10), nullable = False)
    # code = db.Column(db.Integer(), nullable = False)
    # owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
#class Transaction():
#    def __init__(self, state, from_who, to_who, amount):
#        self.state = state
#        self.from_who = from_who
#        self.to_who = to_who
#        self.amount = amount
class Transaction():
    def __init__(self, email, amount):
        self.email = email
        self.amount = amount
class TransactionCard():
    def __init__(self, number, amount):
        self.number = number
        self.amount = amount
