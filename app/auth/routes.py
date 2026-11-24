from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app.models import BlockedIP, User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    # Un IP in blocklist non può usare nemmeno il login vero
    if BlockedIP.query.filter_by(ip=request.remote_addr).first():
        abort(403)

    # Aprendo la pagina di login si esce dall'utente di prima
    if request.method == "GET":
        logout_user()

    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user)
            return redirect(url_for("dashboard.index"))
        error = "Credenziali non valide."

    return render_template("auth/login.html", error=error)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
