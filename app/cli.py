import click
from flask.cli import with_appcontext

from app.extensions import db
from app.hibp import pwned_count
from app.models import Attempt, User


@click.command("create-user")
@click.argument("username")
@click.option("--role", type=click.Choice(["analyst", "admin"]), default="analyst")
@click.password_option()
@with_appcontext  # serve per poter usare il database
def create_user(username, role, password):
    """Crea un utente della dashboard. Esempio: flask create-user mario --role admin"""
    if User.query.filter_by(username=username).first():
        click.echo("Questo utente esiste già.")
        return

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Utente {username} creato ({role}).")


@click.command("check-pwned")
@with_appcontext
def check_pwned():
    """Controlla con Have I Been Pwned le password dei tentativi."""
    passwords = {a.password for a in Attempt.query.filter_by(pwned_count=None) if a.password}

    controllate = 0
    for password in list(passwords)[:200]:  # al massimo 200 per volta
        count = pwned_count(password)
        if count is None:
            click.echo("Servizio non raggiungibile, riprova più tardi.")
            break
        Attempt.query.filter_by(password=password).update({"pwned_count": count})
        db.session.commit()
        controllate += 1

    click.echo(f"Password controllate: {controllate}")
