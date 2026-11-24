from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


def now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """Utente della dashboard (non quelli finti dell'honeypot)."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(16), nullable=False, default="analyst")
    created_at = db.Column(db.DateTime, default=now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class Attempt(db.Model):
    """Un tentativo di login registrato dall'honeypot."""

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False, index=True)
    user_agent = db.Column(db.String(256))
    username = db.Column(db.String(128))
    password = db.Column(db.String(128))
    path = db.Column(db.String(128))
    pwned_count = db.Column(db.Integer) 
    created_at = db.Column(db.DateTime, default=now, index=True)


class BlockedIP(db.Model):
    """IP bloccato dall'admin: l'honeypot gli risponde 403."""

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True, nullable=False)
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=now)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
