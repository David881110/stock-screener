import requests

# **Ersetze mit deinem Firebase Web API Key**
FIREBASE_API_KEY = "AIzaSyCjzqIG16XrNQ_BdgDBhUyqXXYokCiIRAo"

# **1️⃣ Funktion: Neuen Benutzer registrieren**
def register_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=data)
    print("Registrierungsantwort:", response.json())  # Debugging

    if response.status_code == 200:
        return response.json().get("idToken")  # ✅ ID-Token zurückgeben
    else:
        print("⚠ Fehler bei der Registrierung:", response.json())
        return None

# **2️⃣ Funktion: Nutzer einloggen & ID-Token erhalten**
def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=data)
    print("Loginantwort:", response.json())  # Debugging

    if response.status_code == 200:
        return response.json().get("idToken")  # ✅ ID-Token zurückgeben
    else:
        print("⚠ Fehler beim Login:", response.json())
        return None

# **3️⃣ Funktion: Bestätigungs-E-Mail senden**
def send_verification_email(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    data = {
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token  # ✅ Jetzt senden wir den `idToken`
    }
    response = requests.post(url, json=data)
    print("E-Mail Bestätigung Antwort:", response.json())  # Debugging

    if response.status_code == 200:
        print("✅ Bestätigungs-E-Mail erfolgreich gesendet!")
    else:
        print("⚠ Fehler beim Senden der E-Mail:", response.json())

# **TEST-DURCHLAUF**
test_email = "david.striegl@gmx.at"
test_password = "DeinSicheresPasswort123"

# **1️⃣ Nutzer registrieren**
id_token = register_user(test_email, test_password)

if not id_token:
    # Falls Nutzer bereits existiert, einloggen und ID-Token holen
    id_token = login_user(test_email, test_password)

# **2️⃣ Bestätigungs-E-Mail senden**
if id_token:
    send_verification_email(id_token)
else:
    print("❌ Fehler: Konnte keinen ID-Token abrufen.")
