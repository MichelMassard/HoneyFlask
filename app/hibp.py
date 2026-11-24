import hashlib

import requests


def pwned_count(password):
    """Dice quante volte la password è comparsa in data breach (Have I Been Pwned).

    Restituisce 0 se non è mai comparsa e None se il servizio non risponde.
    Al sito mando solo i primi 5 caratteri dell'hash SHA-1, mai la password.
    """
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefisso = sha1[:5]
    resto = sha1[5:]

    try:
        risposta = requests.get("https://api.pwnedpasswords.com/range/" + prefisso, timeout=5)
    except requests.RequestException:
        return None
    if risposta.status_code != 200:
        return None

    for riga in risposta.text.splitlines():
        resto_hash, numero = riga.split(":")
        if resto_hash == resto:
            return int(numero)
    return 0
