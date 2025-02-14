import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Initialisierung
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Test: Neuen Benutzer in Firestore speichern
def test_firestore():
    user_ref = db.collection("users").document("testuser@example.com")
    user_ref.set({"requests_count": 0, "is_premium": False})
    
    # Test: Daten abrufen
    user = user_ref.get()
    if user.exists:
        print("✅ Firestore funktioniert!")
        print("Daten:", user.to_dict())
    else:
        print("❌ Fehler: Daten nicht gefunden!")

# Test starten
test_firestore()
