import streamlit as st
import firebase_admin
from firebase_admin import firestore
from auth import db  # Firestore-Datenbank
import pandas as pd

# **Admin-E-Mails definieren**
ADMIN_EMAILS = ["david.striegl@gmx.at"]  # 🚨 Hier deine Admin-Mail eintragen!

# **📌 Funktion zum Abrufen aller Nutzer aus Firestore**
def get_all_users():
    users_ref = db.collection("users").stream()
    users_data = []

    for user in users_ref:
        data = user.to_dict()
        data["email"] = user.id  # Firestore speichert die E-Mail als Dokument-ID

        # **Setze Standardwerte für fehlende Felder**
        if "last_login" not in data:
            data["last_login"] = "Keine Daten"
        if "is_banned" not in data:
            data["is_banned"] = False

        users_data.append(data)

    return pd.DataFrame(users_data) if users_data else None

# **📌 Admin-Dashboard**
def admin_dashboard():
    st.title("🚀 Admin-Dashboard")

    # **Admin-Check**
    if st.session_state["user"] not in ADMIN_EMAILS:
        st.error("⛔ Zugriff verweigert! Nur Admins dürfen diese Seite sehen.")
        return

    # **📋 Nutzerliste anzeigen**
    users_df = get_all_users()
    if users_df is not None:
        st.write("👥 **Registrierte Nutzer:**")

        # **Nur vorhandene Spalten anzeigen**
        columns_to_show = ["email"]
        if "last_login" in users_df.columns:
            columns_to_show.append("last_login")
        if "is_banned" in users_df.columns:
            columns_to_show.append("is_banned")

        st.dataframe(users_df[columns_to_show])

        # **🔍 Nutzer nach E-Mail suchen**
        search_email = st.text_input("🔎 Nutzer per E-Mail suchen:")

        if search_email:
            user_info = users_df[users_df["email"] == search_email]
            if not user_info.empty:
                st.write(user_info)
            else:
                st.warning("❌ Kein Nutzer mit dieser E-Mail gefunden.")

    else:
        st.warning("🚨 Keine registrierten Nutzer gefunden.")
