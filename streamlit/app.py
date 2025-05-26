import streamlit as st
from streamlit_option_menu import option_menu
import os

# Configuration de la page principale
st.set_page_config(page_title="Gestionnaire de portefeuille", page_icon="💰", layout="wide")

# Ajoutez ici le code pour masquer la sidebar
st.markdown(
    """
    <style>
    /* Cache complètement la sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Exemple d'initialisation du statut de connexion
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False  # ou True si connecté

# Définir le libellé de l'option en fonction du statut
connexion_label = "Mon Compte" if st.session_state.authenticated else "Connexion"

# Récupérer le chemin absolu du dossier pages
base_dir = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(base_dir, "pages")

# Barre de navigation horizontale
with st.container():
    st.markdown(
        """
        <style>
            div[data-testid="stHorizontalBlock"] div {
                display: flex;
                justify-content: center;
                width: 100%;
            }
            div[data-testid="stHorizontalBlock"] button {
                flex-grow: 1;
                text-align: center;
                padding: 10px;
                font-size: 18px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    selected = option_menu(
        menu_title=None,  # Pas de titre
        options=["Accueil", connexion_label, "Analyse des actions", "Analyse des marchés", "Lexique"],
        icons = ["house", "lock", "bar-chart", "graph-up", "book"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

# Définition des chemins des pages associées
page_mapping = {
    "Accueil": None,
    "Connexion": os.path.join(pages_dir, "login.py"),
    "Mon Compte": os.path.join(pages_dir, "compte.py"),
    "Analyse des actions": os.path.join(pages_dir, "stock_prices.py"),
    "Analyse des marchés": os.path.join(pages_dir, "stock.py"),
    "Lexique": os.path.join(pages_dir, "lexique.py")
}

page_path = page_mapping.get(selected, None)

# Chargement dynamique de la page sélectionnée
if page_path is None:
    st.title("🏠 Bienvenue")
elif os.path.exists(page_path):
    with open(page_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code)
else:
    st.error(f"Erreur : Le fichier `{page_path}` est introuvable !")
