# finance-work
Personalized Financial Portfolio Management Web Application – Canadian and U.S. Markets

## Description

Ce projet a été réalisé dans le cadre du cours `Préparation à l'activité de synthèse et d'intégration (MIG8110)`, offert durant la session d’hiver 2025 par M. Aziz Salah à l’Université du Québec à Montréal (UQAM).

C'est une application web destinée aux investisseurs souhaitant suivre, analyser et gérer efficacement leur portefeuille d’actifs boursiers, avec un focus sur les marchés canadien et américain.
Elle fournit une vision claire et actualisée du marché, des visualisations interactives, ainsi qu’un espace personnel de gestion de portefeuille intégrant des suggestions d'investissements.

## Objectifs

* Collecte automatisée des listes d'actions et ETFs des marchés CA/US via Wikipédia.

* Récupération de données financières depuis Yahoo Finance.

* Stockage structuré dans une base de données (PostgreSQL).

* Développement d’une application web interactive avec :

    * Vue d’ensemble du marché à travers des graphiques dynamiques.

    * Création et gestion de portefeuilles d’investissement personnalisés.

    * Suggestions intelligentes d’actifs à fort potentiel.


## Installation
> <i>Prérequis</i>:  Docker;
Docker Compose

1. Cloner ce dépôt :

   ```bash
   git clone https://github.com/Bors00/finance-work.git
   cd finance-project
   ```

2. Construire et démarrer les conteneurs :

   ```bash
   docker-compose up --build
   ```

---

## Structure du projet

```
├── dags/                      # Scripts Airflow (DAGs)
│   ├── __pycache__/           # Cache Python
│   ├── ETF.py                 # DAG extraction ETF
│   ├── macroCAN.py            # DAG extraction macroéconomiques Canada
│   ├── macroUSA.py            # DAG extraction macroéconomiques USA
│   ├── SP500.py               # DAG extraction S&P 500
│   ├── TSX.py                 # DAG extraction TSX
|── loads/                     # Notebooks de chargement
│   ├── load_macroCAN.ipynb
│   ├── load_macroUSA.ipynb
│   ├── load_SP500.ipynb
│   └── load_TSX.ipynb
├── macroeconomics/            # Scripts et données macroéconomiques
├── marches/                   # Scripts et données de marché
├── plugins/                   # Plugins Airflow
├── stocks/                    # Scripts et données actions
├── streamlit/                 # Application Streamlit
│   └── app.py
├── Extract_ETF.ipynb           # Notebook d'extraction ETF
├── Extract_Macroeconomics_CAN.ipynb # Notebook d'extraction macroéconomiques Canada
├── Extract_Macroeconomics_USA.ipynb # Notebook d'extraction macroéconomiques USA
├── Extract_S&P500.ipynb        # Notebook d'extraction S&P 500
├── Extract_Sectors.ipynb       # Notebook d'extraction secteurs
├── Extract_TSX.ipynb           # Notebook d'extraction TSX
├── init_db.ipynb               # Notebook d'initialisation de la base
├── init_db.sql                 # Script SQL d'initialisation
├── jupyter_entrypoint.sh       # Script d'entrée pour Jupyter
├── load_data.ipynb             # Notebook de chargement des données scrappées
├── load_etf.ipynb              # Notebook de chargement des ETF
├── requirements.txt            # Bibliothèques Python
├── start_airflow.sh            # Script de démarrage Airflow
├── wait_for_services.sh        # Script d'attente des services
├── docker-compose.yml          # Définition des services Docker
└── Dockerfile                  # Image de base Python pour Streamlit & Jupyter
```
## Lancement des conteneurs

Le fichier `docker-compose.yml` définit cinq services principaux :

- **db** : Base de données PostgreSQL (image `postgres:13`).
- **streamlit** : Application Streamlit pour visualisation.
- **jupyter** : Environnement Jupyter Notebook pour exécution et visualisation des notebooks.
- **pgadmin** : Interface pgAdmin pour administrer PostgreSQL.
- **airflow** : Orchestrateur Apache Airflow (version 2.6.0) en `SequentialExecutor` avec SQLite.

Chaque service se base sur le même contexte (`.:/app`) et dépendances appropriées.

---

## Initialisation automatique

Au premier démarrage des conteneurs :

1. Le service **db** crée la base `stocks_db` avec l'utilisateur `postgres` / `postgres`.
2. Dans **jupyter**, trois notebooks sont exécutés automatiquement via `papermill` :
   - `init_db.ipynb` : création des tables.
   - `load_data.ipynb` : scrapping et extraction.
   - `load_etf.ipynb` : chargement des données ETF.
3. Les scripts `wait_for_services.sh` garantissent que PostgreSQL est accessible avant d'exécuter les notebooks.

---

## Orchestration Airflow

Les DAGs stockés dans `dags/` définissent les processus d'automatisation à exécuter quotidiennement ou selon la planification choisie. Le script `start_airflow.sh` :

1. Installe `nbconvert`, `ipykernel` et crée un kernel Python3.
2. Initialise la base Airflow (`airflow db init`).
3. Crée l'utilisateur admin (`admin` / `admin`).
4. Lance le scheduler et le webserver Airflow.

Vous pouvez ajouter vos DAGs Python dans `dags/` et vos plugins dans `plugins/`.

---

## Accès aux services

| Service     | URL                     | Identifiants par défaut         |
|-------------|-------------------------|---------------------------------|
| PostgreSQL  | `localhost:5432`        | `postgres` / `postgres`         |
| pgAdmin     | `localhost:5050`        | `admin@example.com` / `secret`  |
| Streamlit   | `localhost:8501`        | —                               |
| Jupyter     | `localhost:8888`        | token désactivé (accès libre)   |
| Airflow UI  | `localhost:8080`        | `admin` / `admin`               |

---

## Organisation

- **Conteneurs Docker** pour isolation et reproductibilité.
- **Papermill** pour exécuter et versionner les notebooks.
- **Airflow** pour orchestrer les workflows ETL.
- **Streamlit** pour tableau de bord interactif.
- **pgAdmin** pour administration visuelle de la base de données.

---

## Auteurs

* Rickiel Bamessi
* Arnaud Blanchet
* Fabrice Hountondji