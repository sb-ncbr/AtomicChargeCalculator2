from flask import Flask
from flask_bootstrap import Bootstrap
import os

application = Flask(__name__)
Bootstrap(application)

application.secret_key = os.environ.get('SECRET_KEY')

from app import routes

