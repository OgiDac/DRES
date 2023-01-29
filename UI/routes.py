from multiprocessing import Process
from UI import app
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request
from UI.models import Card, User, Transaction
import pickle
import requests
from UI.forms import AddFundsForm, CurrencyForm, PasswordForm, RegisterForm, LoginForm, UpdateProfileForm, VerificationForm, TransactionForm, TransactionCardForm, FilterTransactionForm
from flask_login import login_user, login_required, logout_user, current_user
import threading


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(name = form.name.data, surname = form.surname.data, address = form.address.data, city = form.city.data, country = form.country.data, phone = form.phone.data, email = form.email.data, password = form.password1.data)
        dat = {'name' :user_to_create.name, 'surname' :user_to_create.surname, 'address' :user_to_create.address, 'city' :user_to_create.city, 'country' :user_to_create.country, 'phone' :user_to_create.phone, 'email' :user_to_create.email, 'password' :user_to_create.password}
        requests.post('http://localhost:5001/register', data=pickle.dumps(dat))
        
        return redirect(url_for('login'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category='danger')
    return render_template('register.html', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        response =  requests.get('http://localhost:5001/login', data=pickle.dumps({'email':email}))
        if response.content == b'false':
            print('pogresnoo')
        else:
            attempted_user = pickle.loads(response.content)
            if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
            ):
               
                login_user(attempted_user)
            
                return redirect(url_for('profileView'))
            else:
                flash("Incorrect email or password", category='danger')
 
    return render_template('login.html', form=form)
                

@app.route("/profile")
@login_required
def profileView():
    
    return render_template('profileView.html')



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateProfile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
         current_user.name = form.name.data
         current_user.surname = form.surname.data
         current_user.address = form.address.data
         current_user.city = form.city.data
         current_user.country = form.country.data
         current_user.phone = form.phone.data
         current_user.email = form.email.data
         dat = make_user_to_update(current_user)
         requests.post('http://localhost:5001/updateprofile', data=pickle.dumps(dat))
        
         return redirect(url_for('profileView'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category='danger')
    return render_template('updateprofile.html', form = form)

@app.route("/verificate", methods=['GET', 'POST'])
@login_required
def verificate():
    form=VerificationForm()
    if form.validate_on_submit():
        card_to_create = Card(number = form.number.data, owner = current_user.id, expire_date = form.expire_date.data, code = form.code.data)
        dat = {'number':card_to_create.number, 'owner': card_to_create.owner, 'expire_date': card_to_create.expire_date, 'code':card_to_create.code}

        response = requests.get('http://localhost:5001/getcard', data= form.number.data)
        if response.content == b'false':
            return render_template('profileView.html')
        card = pickle.loads(response.content)
        print(card)

        attempt_user_response = requests.get('http://localhost:5001/getuser', data = str(card.owner))
        if attempt_user_response.content == b'false':
            return render_template('profileView.html')
        attempt_user = pickle.loads(attempt_user_response.content)
        
        if card.code == int(form.code.data) and card.expire_date.__eq__(form.expire_date.data ) and attempt_user.name.__eq__(form.owner.data):
            current_user.verificated = True
            card.budget = card.budget-1
            user_to_send = {'id' : current_user.id, 'name' :current_user.name, 'surname' :current_user.surname, 'address' :current_user.address, 'city' :current_user.city, 'country' :current_user.country, 'phone' :current_user.phone, 'email' :current_user.email, 'password' :current_user.password, 'verificated' :current_user.verificated, 'budget': current_user.budget, 'currency': current_user.currency}
            card_to_send = {'id' : card.id, 'number': card.number, 'expire_date': card.expire_date, 'code': card.code, 'budget': card.budget}
           
            requests.get('http://localhost:5001/updateprofile', data=pickle.dumps(user_to_send))
            requests.get('http://localhost:5001/updatecard', data=pickle.dumps(card_to_send))

        
        return render_template('profileView.html')
    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category='danger')

    return render_template('verificateAccount.html', form=form)


@app.route("/addFunds", methods=['GET', 'POST'])
@login_required
def add_funds():
    form = AddFundsForm()
    if form.validate_on_submit():
        if int(form.amount.data) > 0 and int(form.amount.data) < current_user.card[0].budget:
            response =  requests.get('https://api.exchangerate-api.com/v4/latest/RSD')
            data = response.json()
            rate = data['rates'][current_user.currency]
            amount = rate * float(form.amount.data)
            current_user.budget = current_user.budget + amount
            current_user.card[0].budget = current_user.card[0].budget - float(form.amount.data)        
            current_user.budget = round(current_user.budget, 4)
            user_data = make_user_to_update(current_user)
            card_data = make_card_to_update(current_user.card[0])

            requests.get('http://localhost:5001/updateprofile', data=pickle.dumps(user_data))
            requests.get('http://localhost:5001/updatecard', data=pickle.dumps(card_data))
            return render_template('profileView.html')
    return render_template("addFunds.html", form = form)

@app.errorhandler(404)
def handle_404(e):
    # handle all other routes here
    return render_template('index.html')




def make_card_to_update(card):
    card_to_send = {'id' : card.id, 'number': card.number, 'expire_date': card.expire_date, 'code': card.code, 'budget': card.budget}
    return card_to_send

def make_user_to_update(user):
    user_to_send = {'id' : current_user.id, 'name' :current_user.name, 'surname' :current_user.surname, 'address' :current_user.address, 'city' :current_user.city, 'country' :current_user.country, 'phone' :current_user.phone, 'email' :current_user.email, 'password' :current_user.password, 'verificated' :current_user.verificated, 'budget': current_user.budget, 'currency': current_user.currency}
    return user_to_send

@app.route("/makeTransaction", methods=['GET', 'POST'])
@login_required
def makeTransaction():
    
    return render_template('makeTransaction.html')




# 1-U obradai 2-Obradjeno 3-Odbijeno

@app.route("/transaction", methods=['GET', 'POST'])
@login_required
def transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        tran = {'type':'online', 'state':1, 'sender':str(current_user.id), 'receiver':form.email.data, 'amount' : form.amount.data, 'currency' : current_user.currency}
        

        requests.post('http://localhost:5001/makeTransaction', data = pickle.dumps(tran))
        return redirect(url_for('profileView'))                     
    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category='danger')    
    return render_template('transaction.html', form = form)

@app.route('/cardTransaction', methods=['GET', 'POST'])
@login_required
def cardTransaction():
    form = TransactionCardForm()
    if form.validate_on_submit():
        tran = {'type':'card', 'state':1, 'sender':str(current_user.id), 'receiver':form.number.data, 'amount' : form.amount.data, 'currency' : current_user.currency}
        requests.post('http://localhost:5001/makeTransaction', data = pickle.dumps(tran))   
        return redirect(url_for('profileView'))                     
    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category='danger')    
    return render_template('cardTransaction.html', form = form)



@app.route('/transactionHistory', methods=['GET', 'POST'])
@login_required
def transactionHistory():
    response = requests.get('http://localhost:5001/getAllTransactions', data=str(current_user.id))
    list = pickle.loads(response.content)
    #print(list)
    return render_template('transactionHistory.html', items = list)

@app.route('/filterBy', methods=['GET','POST'])
@login_required
def filterBy():
    form = FilterTransactionForm()
    if form.validate_on_submit():
            response = requests.get('http://localhost:5001/getAllTransactions', data=str(current_user.id))
            list = pickle.loads(response.content) 
            person = form.person.data
            print(person)
            actions = form.actions.data
            print(actions)
            typeOfTransaction = form.typeOfTransaction.data
            print(typeOfTransaction)
            list1 = []

            #AKO SE UNESE SAMO EMAIL
            if person and typeOfTransaction=='none' and actions=='none':
                for el in list:
                    if person == el.email:
                        list1.append(el) 

                return render_template('transactionHistory.html', items = list1)
            
            #AKO SE UNESE SAMO TIP TRANSAKCIJE CARD/ONLINE
            elif typeOfTransaction != 'none' and person=="" and actions=='none':
                for el in list:
                    if typeOfTransaction == el.type:
                        
                        list1.append(el)
                print(list1)
                return render_template('transactionHistory.html', items = list1)
            
             #AKO SE UNESE SAMO AKCIJA TJ DA LI CE ISPLATU ILI UPLATU
            elif actions!="None" and actions=="payment" and person=="" and typeOfTransaction=='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])>0: #uplata/payment
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            elif actions!="None" and actions=="disbursement" and person=="" and typeOfTransaction=='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])<0: #isplata/ disbursement
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)

            #AKO SE UNESE TIP TRANSAKCIJE I IMEJL
            elif typeOfTransaction != 'none' and person and actions=='none':
                for el in list:
                    if typeOfTransaction==el.type and person==el.email:
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            
            #AKO SE UNESE UPLATA/ISPLATA i TIP TRANSAKCIJE
            elif actions!="None" and actions=="payment" and person=="" and typeOfTransaction!='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])>0 and el.type==typeOfTransaction: #uplata/payment
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            elif actions!="None" and actions=="disbursement" and person=="" and typeOfTransaction!='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])<0 and el.type==typeOfTransaction: #isplata/ disbursement
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            
             #AKO SE UNESE UPLATA/ISPLATA i MEJL
            elif actions!="None" and actions=="payment" and person and typeOfTransaction=='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])>0 and el.email==person: #uplata/payment
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            elif actions!="None" and actions=="disbursement" and person and typeOfTransaction=='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])<0 and el.email==person: #isplata/ disbursement
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            
            #AKO SE UNESU SVA TRI 
            elif actions!="none" and actions=="payment" and person and typeOfTransaction !='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])>0 and el.type==typeOfTransaction and el.email==person:
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            elif actions!="none" and actions=="disbursement"and person and typeOfTransaction !='none':
                for el in list:
                    payment=el.money.split(" ")
                    if int(payment[0])<0 and el.type==typeOfTransaction and el.email==person:
                        list1.append(el)
                return render_template('transactionHistory.html', items=list1)
            
            
            #AKO SE NE UNESE NISTA
            else:
                return render_template('transactionHistory.html', items=list)

    return render_template('filterBy.html', form=form)

@app.route('/exchange', methods=['GET', 'POST'])
@login_required
def exchange():
    print("total")
    form = CurrencyForm()
    if form.is_submitted():
        total = request.form['return']
        currency = request.form['returnCurrency']
        print(total)
        print(currency)
        current_user.budget = round(float(total), 4)
        current_user.budget = total
        current_user.currency = currency
        user_data = make_user_to_update(current_user)
        requests.get('http://localhost:5001/updateprofile', data=pickle.dumps(user_data))
        return render_template('profileView.html')
       
    return render_template('exchange.html', form=form)

@app.route('/sort', methods = ['GET', 'POST'])
@login_required
def sort():
    response = requests.get('http://localhost:5001/sort', data=str(current_user.id))
    list = pickle.loads(response.content)

    return render_template('transactionHistory.html', items = list)

@app.route('/sortDesc', methods = ['GET', 'POST'])
@login_required
def sortDesc():
    response = requests.get('http://localhost:5001/getAllTransactions', data=str(current_user.id))
    list = pickle.loads(response.content)

    return render_template('transactionHistory.html', items = list)


@app.route('/updatePassword', methods=['GET', 'POST'])
@login_required
def updatePassword():
    form = PasswordForm()
    if form.validate_on_submit():
        if form.oldPassword.data.__eq__(current_user.password):
            current_user.password = form.newPassword.data
            object = make_user_to_update(current_user)
            requests.post('http://localhost:5001/updateprofile', data=pickle.dumps(object))
            return redirect(url_for('profileView'))
            
    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category='danger')
    return render_template('password.html', form = form)