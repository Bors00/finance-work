import streamlit as st
import os
import importlib.util
import psycopg2
import time

# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    host="db",
    database="user_db",
    user="postgres",
    password="postgres",
    port=5432
)
cursor = conn.cursor()

# Initialisation de la session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"  # Page par défaut

# Chargement dynamique de la page de création de compte
if st.session_state["page"] == "create_account":
    page_path = "/app/streamlit/pages/create_account.py"
    if os.path.exists(page_path):
        spec = importlib.util.spec_from_file_location("page_module", page_path)
        page_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(page_module)
    else:
        st.error(f"Erreur : Le fichier `{page_path}` est introuvable !")
    st.stop()  # Arrête l'exécution du script courant après chargement

# Chargement dynamique de la page du compte utilisateur
if st.session_state["page"] == "compte":
    page_path = "/app/streamlit/pages/compte.py" 
    if os.path.exists(page_path):
        spec = importlib.util.spec_from_file_location("page_module", page_path)
        page_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(page_module)
    else:
        st.error(f"Erreur : Le fichier `{page_path}` est introuvable !")
    st.stop()

# Si aucune page dynamique n'est définie, on affiche la page de connexion

st.header("Connexion")
with st.form("login_form", clear_on_submit=True):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    submit_button = st.form_submit_button("Se connecter")

if submit_button:
    if not email or not password:
        st.error("Veuillez remplir tous les champs.")
    else:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, password)
        )
        user = cursor.fetchone()
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            st.success("Connexion réussie !")
            time.sleep(1) 
            st.session_state["page"] = "compte"
            st.rerun()
        else:
            st.error("Identifiants incorrects.")

# Bouton pour créer un compte
if st.button("Créer un compte"):
    st.session_state["page"] = "create_account"
    st.rerun()

