from flask import Flask

from .config import CONFIG_FILE

application = Flask(__name__)

application.jinja_env.trim_blocks = True
application.jinja_env.lstrip_blocks = True

with open(CONFIG_FILE) as f:
    application.config['SECRET_KEY'] = f.read().strip()

from . import routes
