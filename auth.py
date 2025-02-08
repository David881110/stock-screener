import firebase_admin
from firebase_admin import credentials, auth

# Lade die Firebase Admin SDK Schlüsseldatei (ersetze mit deinem JSON)
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# Funktion zum Registrieren eines neuen Benutzers
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return f"✅ Benutzer {email} erfolgreich registriert!"
    except firebase_admin.exceptions.FirebaseError as e:
        return f"⚠ Fehler bei der Registrierung: {e}"

# Funktion zum Einloggen eines Benutzers
def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        return True, f"✅ Login erfolgreich! Willkommen {email}"
    except firebase_admin.exceptions.FirebaseError:
        return False, "❌ Fehler: Benutzer existiert nicht oder falsches Passwort"
