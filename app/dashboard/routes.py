import csv
import io
import ipaddress
from collections import Counter

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Attempt, BlockedIP

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def solo_admin():
    """Se l'utente non è admin risponde 403 (accesso negato)."""
    if not current_user.is_admin:
        abort(403)


@bp.route("/")
@login_required
def index():
    attempts = Attempt.query.all()
    top_usernames = Counter(a.username for a in attempts).most_common(5)
    top_passwords = Counter(a.password for a in attempts).most_common(5)
    top_ips = Counter(a.ip for a in attempts).most_common(5)
    per_day = sorted(Counter(a.created_at.date() for a in attempts).items())[-14:]

    checked = [a for a in attempts if a.pwned_count is not None]
    pwned = [a for a in checked if a.pwned_count > 0]
    pwned_pct = round(len(pwned) / len(checked) * 100) if checked else None

    ip = request.args.get("ip", "").strip()
    query = Attempt.query
    if ip:
        query = query.filter_by(ip=ip)
    latest = query.order_by(Attempt.created_at.desc()).limit(50).all()

    return render_template(
        "dashboard/index.html",
        total=len(attempts),
        top_usernames=top_usernames,
        top_passwords=top_passwords,
        top_ips=top_ips,
        per_day=per_day,
        checked=len(checked),
        pwned_pct=pwned_pct,
        latest=latest,
        ip=ip,
    )


@bp.route("/blocklist", methods=["GET", "POST"])
@login_required
def blocklist():
    solo_admin()

    if request.method == "POST":
        ip = request.form.get("ip", "").strip()


        try:
            ipaddress.ip_address(ip)
        except ValueError:
            flash("Indirizzo IP non valido.", "error")
            return redirect(url_for("dashboard.blocklist"))

        if BlockedIP.query.filter_by(ip=ip).first():
            flash("Questo IP è già bloccato.", "error")
        else:
            blocked = BlockedIP(ip=ip, reason=request.form.get("reason", ""), created_by=current_user.id)
            db.session.add(blocked)
            db.session.commit()
            flash(f"{ip} bloccato.", "ok")
        return redirect(url_for("dashboard.blocklist"))

    blocked = BlockedIP.query.order_by(BlockedIP.created_at.desc()).all()
    return render_template("dashboard/blocklist.html", blocked=blocked)


@bp.route("/blocklist/<int:blocked_id>/delete", methods=["POST"])
@login_required
def unblock(blocked_id):
    solo_admin()

    blocked = db.get_or_404(BlockedIP, blocked_id)
    ip = blocked.ip
    db.session.delete(blocked)
    db.session.commit()
    flash(f"{ip} sbloccato.", "ok")
    return redirect(url_for("dashboard.blocklist"))


def pulisci(testo):
    """Excel trasforma in formula i valori che iniziano con = + - @ : metto un apice davanti."""
    testo = testo or ""
    if testo[:1] in ("=", "+", "-", "@"):
        return "'" + testo
    return testo


@bp.route("/export.csv")
@login_required
def export_csv():
    solo_admin()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["data", "ip", "username", "password", "breach"])
    for a in Attempt.query.order_by(Attempt.created_at):
        writer.writerow([a.created_at, a.ip, pulisci(a.username), pulisci(a.password), a.pwned_count])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tentativi.csv"},
    )
