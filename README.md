# Honeypot con dashboard in Flask

Un honeypot web: due finte pagine di login (`/admin` e `/wp-login.php`) che registrano ogni
tentativo di accesso. Una dashboard protetta permette di analizzare i tentativi.

## Indice

- [Cosa fa](#cosa-fa)
- [Installazione](#installazione)
- [Configurazione (.env)](#configurazione-env)
- [Database](#database)
- [Utenti](#utenti)
- [Avvio](#avvio)
- [Tester](#tester)
- [Have I Been Pwned](#have-i-been-pwned)
- [Test](#test)

## Cosa fa

- Salva IP, username, password, percorso e orario di ogni tentativo.
- Dashboard con classifiche (username, password, IP), tentativi per giorno e ultimi tentativi
  con filtro per IP.
- Due ruoli: `analyst` (solo lettura) e `admin` (anche blocklist ed export CSV).
- Blocklist: un IP bloccato riceve errore 403 dall'honeypot e dal login della dashboard.
- Esportazione CSV dei tentativi (solo admin).
- Controllo delle password con Have I Been Pwned.
- Un tester che attacca l'honeypot con una lista di password.

## Installazione

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

## Configurazione (.env)

Copia `.env.example` in `.env` e compila i valori:

- `SECRET_KEY`: una stringa lunga e casuale (serve a Flask per le sessioni)
- `DATABASE_URL`: url del database
- `FLASK_APP`: `wsgi.py`

Il file `.env` non va su git perché contiene dati segreti.

## Database

Le migrazioni sono nella cartella `migrations/`. Per creare le tabelle:

```
flask db upgrade
```

## Utenti

```
flask create-user mario --role admin
flask create-user luca --role analyst
```

## Avvio

```
flask run
```

- Dashboard: http://127.0.0.1:5000/auth/login
- Pagine esca: http://127.0.0.1:5000/wp-login.php e http://127.0.0.1:5000/admin

Il login della dashboard e le pagine esca sono separati: solo i tentativi fatti sulle pagine
esca vengono salvati e contati nelle statistiche. Gli accessi (giusti o sbagliati) al login
della dashboard non vengono registrati. Un IP in blocklist riceve errore 403 sia sulle pagine
esca sia sul login della dashboard.

Attenzione: se blocchi `127.0.0.1` (il tuo computer) non puoi più fare il login. Se ti è
già successo, sblocca l'IP con `flask shell`:

```
from app.models import BlockedIP
from app.extensions import db
BlockedIP.query.filter_by(ip="127.0.0.1").delete()
db.session.commit()
exit()
```

## Tester

Con l'honeypot acceso, in un altro terminale:

```
python scripts/tester.py passwords.txt 500
```

`passwords.txt` deve avere una password in chiaro per riga.
La lista di Have I Been Pwned contiene hash e non si può usare così.

## Have I Been Pwned

```
flask check-pwned
```

Per ogni password chiede a Have I Been Pwned quante volte è comparsa in data breach e salva il
numero. Al sito vengono mandati solo i primi 5 caratteri dell'hash SHA-1, mai la password.
Il risultato si vede nella dashboard e nel CSV. Serve Internet.

## Test

I test usano l'app già avviata. Crea prima due utenti di prova con password `password`:

```
flask create-user test-admin --role admin
flask create-user test-analyst --role analyst
```

Poi, con due terminali:

```
flask run      (terminale 1)
pytest         (terminale 2)
```

`tests/test_ui.py` prova l'interfaccia nel browser con Playwright. Il progetto non ha una vera API
(solo pagine HTML), quindi non ci sono test API.
Se hai messo `127.0.0.1` nella blocklist, sbloccalo prima di lanciare i test.
