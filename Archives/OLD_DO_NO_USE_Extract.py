import requests
import os
from google.cloud import storage

# Définir les variables
CSV_URL = "https://api.worldbank.org/v2/en/country/CAN?downloadformat=csv"
LOCAL_TMP_FILE = "/tmp/data.csv"  
BUCKET_NAME = "mig8110" 

def telecharger_csv():
    """Télécharge un fichier CSV depuis une URL et l'enregistre temporairement."""
    response = requests.get(CSV_URL)
    if response.status_code == 200:
        with open(LOCAL_TMP_FILE, "wb") as file:
            file.write(response.content)
        print(f"Fichier téléchargé : {LOCAL_TMP_FILE}")
    else:
        raise Exception(f"Échec du téléchargement. Code : {response.status_code}")

def televerser_sur_gcs():
    """Copie le fichier dans Google Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob("data.csv")  # Nom du fichier dans GCS
    blob.upload_from_filename(LOCAL_TMP_FILE)
    print(f"Fichier copié dans GCS : gs://{BUCKET_NAME}/data.csv")

def main(event, context):
    """Fonction principale exécutée par Cloud Functions."""
    try:
        telecharger_csv()
        televerser_sur_gcs()
    except Exception as e:
        print(f"Erreur : {str(e)}")
