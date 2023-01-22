
from Engine import app
import pickle
from flask import redirect, render_template, request, flash, session, url_for
from Engine import db
import Engine
from Engine.models import User, Card
import requests
from sqlalchemy.orm import lazyload
import multiprocessing
import time


@app.route('/register', methods=['POST'])
def home():
    s =pickle.loads(request.data)
    print(s)
    user_to_create = User(name = s['name'], surname = s['surname'], address = s['address'], city = s['city'], country = s['country'], phone = s['phone'], email = s['email'], password = s['password'])
    #user_to_create = User(username = s['username'],email = s['email'], password = s['password'])
    db.session.add(user_to_create)
    db.session.commit()
    return 'Hello from app2!'


@app.route('/login', methods=[ 'GET'])
def login():
    data =pickle.loads(request.data)
    print(data)
    user = User.query.filter_by(email = data['email']).first()
    print('---')
    print(user)
    user_binary = pickle.dumps(user)
    if user:
        #login_user(user)
      
        return user_binary
    else:
        return 'false'
        
    
@app.route('/getuser', methods=['GET'])
def getuser(): 
    id = request.data.decode("utf-8") 
    user = User.query.filter_by(id = id).first()
    user_binary = pickle.dumps(user)
    if user:
        #login_user(user)
      
        return user_binary
    else:
        return 'false'


    
@app.route('/updateprofile', methods=['POST', 'GET'])
def updateprofile():
    s =pickle.loads(request.data)
    print(s)
    changed_user = User.query.filter_by(id = s['id']).first()
    changed_user.name = s['name']
    changed_user.surname = s['surname']
    changed_user.address = s['address']
    changed_user.city = s['city']
    changed_user.country = s['country']
    changed_user.phone = s['phone']
    changed_user.email = s['email']
    changed_user.password = s['password']
    changed_user.verificated = s['verificated']
    changed_user.budget = s['budget']
    changed_user.transactions = s['transactions']

    db.session.commit()
    return 'Hello from app2!'

@app.route('/updatecard', methods=['POST', 'GET'])
def updatecard():
    s =pickle.loads(request.data)
    print(s)
    changed_card = Card.query.filter_by(id = s['id']).first()
    changed_card.number = s['number']
    changed_card.expire_date = s['expire_date']
    changed_card.code = s['code']
    changed_card.budget = s['budget']
    print(changed_card.budget)

    db.session.commit()
    return 'Hello from app2!'

# @app.route('/verificate', methods=['POST'])
# def verificated():
#     s =pickle.loads(request.data)
#     print(s)
#     card_to_create = Card(number = s['number'], owner = s['owner'], expire_date = s['expire_date'], code = s['code'])
#     user = User.query.filter_by(id=card_to_create.owner).first()
#     user.budget = user.budget -1
#     user.verificated=True
#     db.session.add(card_to_create)
#     db.session.commit()
#     return "blahblah"


@app.route('/getcard', methods=['GET'])
def get_card():
    number = request.data.decode("utf-8") 
    card = Card.query.filter_by(number = number).first()
    print(card)
    card_binary = pickle.dumps(card)
    if card:
        #login_user(user)
      
        return card_binary
    else:
        return 'false'
    
@app.route('/getcardbyowner', methods=['GET'])
def get_card_by_owner():
    number = request.data.decode("utf-8") 
    card = Card.query.filter_by(owner = number).first()
    print(card)
    card_binary = pickle.dumps(card)
    if card:
        #login_user(user)
      
        return card_binary
    else:
        return 'false'

@app.route("/transaction", methods=['GET', 'POST'])
def transaction():
    data = request.data
    objects = pickle.loads(data)
    dat, user_data = objects
    print(dat,user_data)
    email = dat['email']
    amount = int(dat['amount'])
    id = user_data['id']
    
    user = User.query.filter_by(email = email).first()

    card_and_user_binary = pickle.dumps(user)
    if user:
        p1 = multiprocessing.Process(target=update_budget, args=(id,user.id,amount))
        p1.start()
        
        card_and_user_binary = pickle.dumps(user)
        
        return card_and_user_binary
    else: 
       print('false')
       return 'false'

def update_budget(id,id2,amount):
    app.app_context().push()
    current_user = User.query.filter_by(id = id).first()
    user = User.query.filter_by(id = id2).first()
    print(current_user, user, amount)
    current_user.budget -= amount
    user.budget += amount
    print('----------')
    print(current_user.budget, user.budget)
    
    db.session.commit()
          

@app.route("/cardTransaction", methods=['GET', 'POST'])
def cardTransaction():
    data = request.data
    objects = pickle.loads(data)
    dat, user_data = objects
    print(dat, user_data)
    number = dat['number']
    amount = int(dat['amount'])
    id = user_data['id']
    card = Card.query.filter_by(number = number).first()
    current_user = User.query.filter_by(id = id).first()
    card_and_user_binary = pickle.dumps(card)
    if card:
        current_user.budget -= int(amount)
        card.budget += int(amount)
        print(card.budget)
        print(current_user.budget)
        db.session.commit()
        return card_and_user_binary
    else: 
       print('false')
       return 'false'

    """
    if user :
        user.budget += int(data['amount'])
        print(user.budget)
    #elif card: 
        #card.budget += int(data['amount'])
    else:
        print('false')
        return 'false'
    """
    

