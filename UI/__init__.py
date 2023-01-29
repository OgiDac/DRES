from flask import Flask
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '8c9fa3d6ed31570f45b6084b'

login_manager = LoginManager(app)
login_manager.login_view = "profileView"
login_manager.login_message_category = "info"
login_manager.init_app(app)

from UI import routes


