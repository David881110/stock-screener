import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests

# **Firebase Admin SDK initialisieren**
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

# **Firestore Verbindung**
db = firestore.client()

# **📌 Funktion: Überprüfen, ob Nutzer die tägliche Grenze für Screener-Abfragen erreicht hat**
def is_premium_user(email):
    user_ref = db.collection("users").document(email)
    user = user_ref.get()

    if user.exists:
        return user.to_dict().get("is_premium", False)
    return False

# **Firebase Web API Key für REST API**
FIREBASE_API_KEY = "AIzaSyCjzqIG16XrNQ_BdgDBhUyqXXYokCiIRAo"  # 🔹 Ersetze mit deinem aktuellen API Key

# **📌 Funktion zur Registrierung mit E-Mail-Bestätigung**
def register_user(email, password):
    try:
        # 🔹 Nutzer in Firebase Authentication erstellen (über REST API)
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=data)

        if response.status_code == 200:
            user_data = response.json()
            id_token = user_data["idToken"]  # 🔥 ID-Token für Bestätigungs-E-Mail nutzen

            # 🔹 Nutzer in Firestore speichern
            db.collection("users").document(email).set({
                "requests_count": 0,
                "is_premium": False,
                "verified": False
            })

            # 🔹 Bestätigungs-E-Mail senden
            send_verification_email(id_token)

            return f"✅ Registrierung erfolgreich! Bitte bestätige deine E-Mail."
        else:
            return f"⚠ Fehler bei der Registrierung: {response.json()}"

    except Exception as e:
        return f"⚠ Fehler bei der Registrierung: {e}"


# **📌 Funktion zum Senden der Bestätigungs-E-Mail**
def send_verification_email(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    data = {
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    }
    response = requests.post(url, json=data)

    if response.status_code == 200:
        return "✅ Bestätigungs-E-Mail wurde gesendet!"
    else:
        return f"⚠ Fehler beim Senden der E-Mail: {response.json()}"


# **📌 Funktion zum Einloggen (nur wenn E-Mail verifiziert wurde)**
def login_user(email, password):
    try:
        # 🔹 Nutzer anmelden und ID-Token abrufen
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=data)

        if response.status_code == 200:
            user_data = response.json()
            id_token = user_data["idToken"]

            # 🔹 Überprüfen, ob die E-Mail verifiziert wurde
            if is_verified(id_token):
                return True, f"✅ Login erfolgreich! Willkommen {email}"
            else:
                return False, "❌ Bitte bestätige zuerst deine E-Mail!"
        else:
            return False, f"❌ Fehler: {response.json()}"

    except Exception as e:
        return False, f"❌ Fehler: {e}"


# **📌 Funktion zur Überprüfung, ob E-Mail verifiziert ist**
def is_verified(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"
    data = {
        "idToken": id_token
    }
    response = requests.post(url, json=data)

    if response.status_code == 200:
        users = response.json().get("users", [])
        if users and users[0].get("emailVerified", False):
            return True
    return False


# **📌 Funktion zur Erhöhung des Abrufzählers**
def increment_request_count(email):
    user_ref = db.collection("users").document(email)
    user = user_ref.get()

    if user.exists:
        data = user.to_dict()
        if data["requests_count"] < 5 or data["is_premium"]:
            user_ref.update({"requests_count": data["requests_count"] + 1})
            return True, f"✅ Abruf Nr. {data['requests_count'] + 1}"
        else:
            return False, "❌ Limit erreicht! Upgrade auf Premium nötig."
    else:
        # Falls der User nicht existiert, neu anlegen
        user_ref.set({"requests_count": 1, "is_premium": False})
        return True, "✅ Erster Abruf gespeichert."


# **📌 Funktion zur Aktivierung von Premium (nach Zahlung)**
def upgrade_to_premium(email):
    user_ref = db.collection("users").document(email)
    user_ref.update({"is_premium": True})
    return "✅ Premium aktiviert!"
