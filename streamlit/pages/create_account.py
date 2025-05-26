import streamlit as st
import psycopg2
import psycopg2.errors
import time

# 1) Fonction de connexion à la base
def get_connection():
    """
    Établit la connexion à la base de données PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            host="db",
            database="user_db",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return None

# 2) Fonction d'insertion d'un nouvel utilisateur
def insert_user(username, email, password):
    """
    Insère l'utilisateur dans la table 'users' et renvoie l'ID inséré.
    """
    conn = get_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
                RETURNING id
            """
            cursor.execute(query, (username, email, password))
            conn.commit()
            new_id = cursor.fetchone()
            return new_id[0] if new_id else None
    except psycopg2.Error as e:
        st.error(f"Erreur SQL : {e.pgcode} - {e.pgerror}")
        return None
    except Exception as e:
        st.error(f"Erreur lors de l'insertion : {e}")
        return None
    finally:
        conn.close()

# 3) Initialisation des valeurs dans le session_state
if "username" not in st.session_state:
    st.session_state.username = ""
if "email" not in st.session_state:
    st.session_state.email = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# 4) Page Streamlit : Création de compte
st.title("Créer un compte")

# 5) Vérification du nombre d'utilisateurs avant insertion
def check_users():
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
        except Exception as e:
            st.error(f"Erreur lors du test de requête : {e}")
        finally:
            conn.close()

check_users()

# 6) Formulaire Streamlit avec session_state
with st.form("create_account_form"):
    st.session_state.username = st.text_input("Nom d'utilisateur", value=st.session_state.username)
    st.session_state.email = st.text_input("Email", value=st.session_state.email)
    st.session_state.password = st.text_input("Mot de passe", type="password", value=st.session_state.password)
    submit = st.form_submit_button("Créer le compte")

# 7) Gestion du clic sur le bouton
if submit:
    if not st.session_state.username or not st.session_state.email or not st.session_state.password:
        st.error("Veuillez remplir tous les champs.")
    else:
        try:
            new_id = insert_user(st.session_state.username, st.session_state.email, st.session_state.password)
            if new_id:
                st.success(f"Compte créé avec succès")
                st.session_state.form_submitted = True
                st.session_state.username = ""
                st.session_state.email = ""
                st.session_state.password = ""
                st.session_state.form_submitted = False
                st.session_state["page"] = "login"
                time.sleep(2)
                st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de la création du compte : {e}")

# Bouton pour retourner au login
if st.button("Retourner à la page de connexion"):
    st.session_state["page"] = "login"
    st.rerun()


