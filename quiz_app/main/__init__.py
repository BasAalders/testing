import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)

    # Configuration
    # In a real app, use environment variables or a config file.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here_change_me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'login' # The route for login
    login_manager.login_message_category = 'info' # Flash message category

    from .models import User # Import models here to avoid circular imports

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import home, register, login, logout, dashboard # Import routes

    # Register blueprints if you decide to use them, for now direct routes
    # app.register_blueprint(routes_blueprint)

    with app.app_context():
        db.create_all() # Create sql tables for our data models

    return app

# This line will be removed when run.py imports create_app
# For now, to allow models.py to import 'db' directly from this module during initial creation phase
# if not Flask(__name__).app_context():
#     app = create_app()
# else:
#     app = Flask(__name__) # temp app for context
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # temp
#     db.init_app(app)


# The following is a common pattern if you want to initialize db here
# and then import it in other files like models.py or routes.py
#
# from flask import current_app
#
# if current_app:
#     db.init_app(current_app)
#     login_manager.init_app(current_app)
#     bcrypt.init_app(current_app)

# Correction: Simpler __init__.py structure.
# The app object will be created by run.py by calling create_app().
# Extensions are initialized but not tied to an app instance here.
# They get tied when app.init_app() is called within create_app().

app = Flask(__name__) # This is a temporary app instance for initial setup.
                      # It will be replaced by the one in create_app.
                      # This is a common workaround for Flask extension initialization.
                      # However, the best practice is to use Application Factory pattern `create_app()`.

# The issue is that models.py and routes.py import db, bcrypt, app from this __init__.py
# So these must be defined at the top level.
# When using create_app, they are typically defined globally and then init_app is called.

# Re-simplifying for clarity and to ensure `db` can be imported by `models`
# The `app` imported by `routes` will be the one from `create_app()` via `run.py` eventually.
# However, direct import `from . import app` in routes.py is problematic with factory pattern if app is not global.
# Let's adjust routes and models to import `current_app` or pass `app` around,
# or make `app` here the actual app instance and remove `create_app` if not using factory for `run.py`.

# For this structure, let's assume `run.py` will call `create_app()` and use the returned app.
# `models.py` imports `db` from `.` (this file). `db` is a global `SQLAlchemy()` instance.
# `routes.py` imports `app`, `db`, `bcrypt` from `.`
# This means `app` also needs to be a global object here, which contradicts the factory pattern slightly,
# or routes need to be structured as a Blueprint.

# Let's go with a simplified setup first and refine to full factory if issues arise.
# Keep global `app`, `db`, `bcrypt`, `login_manager`.

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here_change_me_too')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from .models import User
from .routes import home, register, login, logout, dashboard # This will register routes with `app`

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# This is a simplified structure. For a more robust app, use create_app factory and blueprints.
# For now, this avoids circular dependencies for this specific file structure.
# The `app` object here is the one that will be run.
# `run.py` will import this `app`.

# Create tables needs to be done in app context
with app.app_context():
    db.create_all()
