from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_assets import Environment
from flask_htmlmin import HTMLMIN

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect(app)
assets = Environment(app)
HTMLMIN(app)

from app import views, models
