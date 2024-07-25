from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db_name = "recipe.db"
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}"
    app.config["SECRET_KEY"] = "asdwasdsdasd"
    app.config["UPLOAD_FOLDER"] = "static/images"
    db.init_app(app=app)

    bcrypt = Bcrypt(app)

    from .routes import register_blueprint
    register_blueprint(app, db, bcrypt)

    from .models import User

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user = User.query.get(id)
        return user

    @login_manager.unauthorized_handler
    def unloged_user():
        flash("YOU NEED TO BE LOGGED IN TO ACCESS THIS PAGE", category="error")
        return redirect(url_for("login"))

    migrate = Migrate(app, db, render_as_batch=True)

    return app