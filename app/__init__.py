from flask import Flask

from config import CONFIG_FILE

application = Flask(__name__)

with open(CONFIG_FILE) as f:
    application.config['SECRET_KEY'] = f.read().strip()

from app import routes
