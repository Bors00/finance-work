#!/usr/bin/env bash
set -e

echo "Installation de nbconvert..."
pip install nbconvert

echo "Installation d'ipykernel..."
pip install ipykernel

echo "Installation du kernel python3..."
python -m ipykernel install --user --name python3 --display-name "Python 3"

echo "Installation de yfinance..."
pip install yfinance

echo "Initialisation de la DB Airflow..."
airflow db init

echo "Création de l'utilisateur admin..."
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin || true

echo "Démarrage du scheduler..."
airflow scheduler &

echo "Démarrage du webserver..."
exec airflow webserver
