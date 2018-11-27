from flask import Flask
import os

application = Flask(__name__)
application.secret_key = os.environ.get('SECRET_KEY')

from app import routes

