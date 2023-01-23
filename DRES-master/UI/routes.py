from UI import app
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request
from UI.models import Card, User, Transaction, TransactionCard
import pickle
import requests
from UI.forms import AddFundsForm, CurrencyForm, RegisterForm, LoginForm, UpdateProfileForm, VerificationForm, TransactionForm, TransactionCardForm
from flask_login import login_user, login_required, logout_user, current_user

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
        #user_to_create = User(username = form.username.data,email = form.email.data, password = form.password1.data)
        #dat = {'username':user_to_create.username, 'password': user_to_create.password, 'email': user_to_create.email}
        requests.post('http://localhost:5001/register', data=pickle.dumps(dat))
        
        return redirect(url_for('index'))
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
            #attempted_user = User.query.filter_by(email=form.email.data).first()
            if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
            ):
               
                login_user(attempted_user)
            
                return redirect(url_for('profileView'))##OVDE TREBA DA SE UCITA PROFIL AL GA NISAM JOS NAPRAVILA
            else:
                flash("Incorrect email or password", category='danger')
 
    return render_template('login.html', form=form)
                

@app.route("/profile")
@login_required
def profileView():
    
    return render_template('profileView.html')

@app.route('/com')
def home():
    # Send a request to app2
    requests.post('http://localhost:5001/', data='porukicaa')
    return 'sads'

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateProfile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
         user_to_create = User(name = form.name.data, surname = form.surname.data, address = form.name.data, city = form.city.data, country = form.country.data, phone = form.phone.data, email = form.email.data, password = form.password.data)
         dat = {'id' : current_user.id, 'name' :user_to_create.name, 'surname' :user_to_create.surname, 'address' :user_to_create.address, 'city' :user_to_create.city, 'country' :user_to_create.country, 'phone' :user_to_create.phone, 'email' :user_to_create.email, 'password' :user_to_create.password}
        
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

        attempt_user_response = requests.get('http://localhost:5001/getuser', data = str(card.owner))
        if attempt_user_response.content == b'false':
            return render_template('profileView.html')
        attempt_user = pickle.loads(attempt_user_response.content)
        
        if card.code == int(form.code.data) and card.expire_date.__eq__(form.expire_date.data ) and attempt_user.name.__eq__(form.owner.data):
            current_user.verificated = True
            card.budget = card.budget-1
            user_to_send = {'id' : current_user.id, 'name' :current_user.name, 'surname' :current_user.surname, 'address' :current_user.address, 'city' :current_user.city, 'country' :current_user.country, 'phone' :current_user.phone, 'email' :current_user.email, 'password' :current_user.password, 'verificated' :current_user.verificated, 'budget': current_user.budget, 'currency': current_user.currency, 'transactions': current_user.transactions}
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
    print('TUuuuu SAM')
    form = AddFundsForm()
    if form.validate_on_submit():
        if int(form.amount.data) > 0 and int(form.amount.data) < current_user.budget:
            response =  requests.get('https://api.exchangerate-api.com/v4/latest/USD')
            data = response.json()
            rate = data['rates'][current_user.currency]
            amount = rate * int(form.amount.data)
            current_user.budget = current_user.budget + amount
            current_user.card[0].budget = current_user.card[0].budget - int(form.amount.data)        
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
    user_to_send = {'id' : current_user.id, 'name' :current_user.name, 'surname' :current_user.surname, 'address' :current_user.address, 'city' :current_user.city, 'country' :current_user.country, 'phone' :current_user.phone, 'email' :current_user.email, 'password' :current_user.password, 'verificated' :current_user.verificated, 'budget': current_user.budget, 'currency': current_user.currency, 'transactions': current_user.transactions}
    return user_to_send

@app.route("/transaction", methods=['GET', 'POST'])
@login_required
def transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        transaction_to_create = Transaction(email = form.email.data, amount = form.amount.data)
        dat = {'email': transaction_to_create.email, 'amount': transaction_to_create.amount}
        user_data = make_user_to_update(current_user)
        objects = (dat, user_data)
        response =  requests.get('http://localhost:5001/transaction', data=pickle.dumps(objects))
        print(response)
        if response.content == b'false':
            return redirect(url_for('profileView'))
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
        transaction_to_create = TransactionCard(number = form.number.data, amount = form.amount.data)
        dat = {'number': transaction_to_create.number, 'amount': transaction_to_create.amount}
        user_data = make_user_to_update(current_user)
        objects = (dat, user_data)
        response =  requests.get('http://localhost:5001/cardTransaction', data=pickle.dumps(objects))
        print(response)
        if response.content == b'false':
            return redirect(url_for('profileView'))
        return redirect(url_for('cardTransaction'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category='danger')    
    return render_template('cardTransaction.html', form = form)


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
        current_user.budget = total
        current_user.currency = currency
        user_data = make_user_to_update(current_user)
        requests.get('http://localhost:5001/updateprofile', data=pickle.dumps(user_data))
        return render_template('profileView.html')
       
    return render_template('exchange.html', form=form)