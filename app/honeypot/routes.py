from flask import Blueprint, abort, render_template, request

from app.extensions import db
from app.models import Attempt, BlockedIP

bp = Blueprint("honeypot", __name__)



@bp.route("/admin", methods=["GET", "POST"])
@bp.route("/wp-login.php", methods=["GET", "POST"])
def fake_login():
    if BlockedIP.query.filter_by(ip=request.remote_addr).first():
        abort(403)

    error = None

    if request.method == "POST":
        attempt = Attempt(
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:256],
            username=request.form.get("username", "")[:128],
            password=request.form.get("password", "")[:128],
            path=request.path,
        )
        db.session.add(attempt)
        db.session.commit()
        error = "Nome utente o password non validi."

    return render_template("honeypot/login.html", error=error)
