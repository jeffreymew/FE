from flask import Flask
from config import BaseConfig
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask("application", static_folder="../static/dist", template_folder="../static")
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
