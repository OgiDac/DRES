from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired


class RegisterForm(FlaskForm):
    name = StringField(label='Name', validators=[Length(min=3, max=20), DataRequired()])
    surname = StringField(label='Surname', validators=[Length(min=3, max=20), DataRequired()])
    address = StringField(label='Address', validators=[Length(min=3, max=20), DataRequired()])
    city = StringField(label='City', validators=[Length(min=3, max=20), DataRequired()])
    country = StringField(label='County', validators=[Length(min=3, max=20), DataRequired()])
    phone = StringField(label='Phone', validators=[Length(min=3, max=20), DataRequired()])
    email = StringField(label='Email Address', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password',validators=[EqualTo('password1', "Passwords are not same"), DataRequired()])
    submit = SubmitField(label='CREATE ACCOUNT')

class LoginForm(FlaskForm):
     email = StringField(label='Email Address', validators=[Email(), DataRequired()])
     password = PasswordField(label='Password', validators=[DataRequired()])
     submit = SubmitField(label='LOG IN')

class UpdateProfileForm(FlaskForm):
    name = StringField(label='Name', validators=[Length(min=3, max=20),DataRequired()])
    surname = StringField(label='Surname', validators=[Length(min=3, max=20), DataRequired()])
    email = StringField(label='Email Address', validators=[Email(), DataRequired()])
    address = StringField(label='Address', validators=[Length(min=3, max=20), DataRequired()])
    city = StringField(label='City', validators=[Length(min=3, max=20), DataRequired()])
    country = StringField(label='County', validators=[Length(min=3, max=20), DataRequired()])
    phone = StringField(label='Phone', validators=[Length(min=3, max=20), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    
    submit = SubmitField(label='Update')

class VerificationForm(FlaskForm):
    number=StringField(label='Card Number', validators=[Length(20), DataRequired()])
    owner=StringField(label='Card Owner', validators=[Length(max=20), DataRequired()])
    expire_date=StringField(label='Expire Date', validators=[Length(max=10), DataRequired()])
    code=StringField(label='Code', validators=[DataRequired()])
    submit = SubmitField(label='Verificate')

class TransactionForm(FlaskForm):
    email = StringField(label='Email Address', validators=[Email(), DataRequired()])
    amount = StringField(label='Amount', validators=[Length(max=20), DataRequired()])
    submit = SubmitField(label='Send')

class TransactionCardForm(FlaskForm):
    number = StringField(label='Card Number', validators=[Length(20), DataRequired()])
    amount = StringField(label='Amount', validators=[Length(max=20), DataRequired()])
    submit = SubmitField(label='Send')


class AddFundsForm(FlaskForm):
    amount=StringField(label='Amount', validators=[DataRequired()])
    
    submit = SubmitField(label='Submit')
