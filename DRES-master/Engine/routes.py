
import threading
from Engine import app
import pickle
from flask import redirect, render_template, request, flash, session, url_for, jsonify
from Engine import db
import Engine
from Engine.models import User, Card, Transaction
import requests
from sqlalchemy.orm import lazyload
from multiprocessing import Process, Queue
from time import sleep

queue = Queue()


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
    print("Pozvan sam za " + id)
    user_binary = pickle.dumps(user)
    if user:
        #login_user(user)
      
        return user_binary
    else:
        return 'false'
    
@app.route('/getuserbyemail', methods=['GET'])
def getuserbyemail(): 
    email = request.data.decode("utf-8") 
    user = User.query.filter_by(email = email).first()
    print("Pozvan sam za " + email)
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
    changed_user.currency = s['currency']

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

@app.route('/getcard', methods=['GET'])
def get_card():
    number = request.data.decode("utf-8") 
    card = Card.query.filter_by(number = number).first()
    print(card.number)
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

   
@app.route("/makeTransaction", methods=['GET', 'POST'])
def makeTransaction():
    print('Izvrsava se')
    data = request.data
    object = pickle.loads(data)
    sender = User.query.filter_by(id = object['sender']).first()
    
    transaction = Transaction(sender = object['sender'], receiver = object['receiver'], amount = object['amount'], state = object['state'], currency = object['currency'], type = object['type'])
    db.session.add(transaction)
    db.session.commit()

    thread = threading.Thread(target=transactionThread, args=(transaction.id, ))
    thread.start()

    return 'OK'

def transactionThread(id):
    print("NOVI TRED")
    sleep(10)
    queue.put(id)



@app.route('/getAllTransactions', methods=['GET'])
def getAllTransactions(): 
    id = request.data.decode("utf-8") 
    user = User.query.filter_by(id = id).first()
    list1 = user.sender 
    list2 = user.receiver
    for el in list1:
        if not isinstance(el.receiver, int):
            el.email = el.receiver
        else:
            el.email = el.receiver_ref.email
        el.money = '-' + str(el.amount) + ' ' + el.currency
    for el in list2:
        if not isinstance(el.receiver, int):
            el.email = el.receiver
        else:
            el.email = el.sender_ref.email
        el.money = '+' + str(el.amount) + ' ' + el.currency

    list = list1 + list2
    sort = sorted(list, key=lambda x: x.time_created, reverse=True)

    return pickle.dumps(sort)

@app.route('/sort', methods=['GET'])
def sort(): 
    id = request.data.decode("utf-8") 
    user = User.query.filter_by(id = id).first()
    list1 = user.sender 
    list2 = user.receiver
    for el in list1:
        if not isinstance(el.receiver, int):
            el.email = el.receiver
        else:
            el.email = el.receiver_ref.email
        el.money = '-' + str(el.amount) + ' ' + el.currency
    for el in list2:
        if not isinstance(el.receiver, int):
            el.email = el.receiver
        else:
            el.email = el.sender_ref.email
        el.money = '+' + str(el.amount) + ' ' + el.currency

    list = list1 + list2
    sort = sorted(list, key=lambda x: x.time_created)

    return pickle.dumps(sort)


def transactionProcess(queue: Queue):
    app.app_context().push()
    while 1:
        try:
            id = queue.get()
        except KeyboardInterrupt:
            break
        
        transaction = Transaction.query.filter_by(id = id).first()
        sender = User.query.filter_by(id = transaction.sender).first()
        print(transaction)
        if str(transaction.type).__eq__('online'):
            receiver = User.query.filter_by(email = transaction.receiver).first()
            
            if receiver == None:
                transaction.state = 3
                db.session.commit()
                continue
            string = 'https://api.exchangerate-api.com/v4/latest/' + str(transaction.currency)
            response =  requests.get(string)
            data = response.json()
            rate = data['rates'][receiver.currency]
            amount = rate * float(transaction.amount)

            
            if sender.budget - float(str(transaction.amount)) > 0:

                sender.budget = round(sender.budget - float(transaction.amount), 4)
                receiver.budget = round(receiver.budget + amount, 4)
                transaction.state = 2
                db.session.commit()
            else:
                transaction.state = 3
                db.session.commit()

        else:
            card = Card.query.filter_by(number = transaction.receiver).first()
            if card == None:
                transaction.state = 3
                db.session.commit()
                continue
            receiver = User.query.filter_by(id = card.owner).first()
            string = 'https://api.exchangerate-api.com/v4/latest/' + str(transaction.currency)
            response =  requests.get(string)
            data = response.json()
            rate = data['rates'][receiver.currency]
            amount = rate * float(transaction.amount)
            if sender.budget - float(str(transaction.amount)) > 0:
                sender.budget = round(sender.budget - float(transaction.amount), 4)
                card.budget = round(card.budget + amount, 4)
                transaction.state = 2
                print('DEBUG')
                db.session.commit()
                continue
            else:
                transaction.state = 3
                db.session.commit()
                continue
        
    




"""
@app.route('/sortTransactions', methods=['POST'])
def sortTransactions():
    sortBy = request.json['sortBy']
    order = request.json['order']

    transactions = Transaction.query.all()
    if order == 'desc':
        transactions = sorted(transactions, key=lambda x: getattr(x, sortBy), reverse=True)
    else:
        transactions = sorted(transactions, key=lambda x: getattr(x, sortBy),reverse=False)

    return jsonify(transactions)
"""