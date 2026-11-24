from flask import Flask
from app.extensions import db, login_manager, migrate
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Manca SECRET_KEY: controlla il file .env")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app import models
    from app.auth.routes import bp as auth_bp
    from app.cli import check_pwned, create_user
    from app.dashboard.routes import bp as dashboard_bp
    from app.honeypot.routes import bp as honeypot_bp

    app.register_blueprint(honeypot_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.cli.add_command(create_user)
    app.cli.add_command(check_pwned)

    return app
