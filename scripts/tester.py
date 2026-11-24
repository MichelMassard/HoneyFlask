"""Tester dell'honeypot: prova una lista di password sul finto login.

Uso:  python scripts/tester.py passwords.txt 500
(il secondo numero è quante password provare, di default 200)

Va usato solo sul proprio computer: l'indirizzo qui sotto è localhost.
"""
import sys

import requests

URL = "http://127.0.0.1:5000/wp-login.php"
USERNAMES = ["admin", "root", "user", "test"]

if len(sys.argv) < 2:
    sys.exit("Uso: python scripts/tester.py passwords.txt [quante]")

nome_file = sys.argv[1]
limite = int(sys.argv[2]) if len(sys.argv) > 2 else 200
inviati = 0

try:
    with open(nome_file, encoding="latin-1") as f:
        for riga in f:
            password = riga.strip()
            if password == "":
                continue

            # La lista scaricabile di Have I Been Pwned ha hash ("40 caratteri:numero"), non password
            if ":" in password and len(password.split(":")[0]) == 40:
                sys.exit("Il file contiene hash, non password in chiaro.")

            if inviati >= limite:
                break

            username = USERNAMES[inviati % len(USERNAMES)]
            risposta = requests.post(URL, data={"username": username, "password": password}, timeout=5)
            if risposta.status_code == 403:
                print(f"Bloccato dalla blocklist dopo {inviati} tentativi.")
                break
            inviati += 1
except FileNotFoundError:
    sys.exit(f"File non trovato: {nome_file}")
except requests.ConnectionError:
    sys.exit("Honeypot non raggiungibile: hai avviato flask run?")

print(f"Inviati {inviati} tentativi.")
