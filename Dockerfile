# Dockerfile
FROM python:3.10

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer Streamlit, Jupyter, psycopg2-binary, papermill et nbconvert
RUN pip install --upgrade pip
RUN pip install streamlit jupyter psycopg2-binary
RUN pip install --upgrade streamlit

# Copier les scripts dans l'image et les rendre exécutables
COPY jupyter_entrypoint.sh /app/jupyter_entrypoint.sh
COPY wait_for_services.sh /app/wait_for_services.sh
RUN chmod +x /app/jupyter_entrypoint.sh /app/wait_for_services.sh

# Exposer les ports utilisés par Streamlit (8501) et Jupyter (8888)
EXPOSE 8501 8888

# CMD par défaut (sera surchargé pour Jupyter via docker-compose)
CMD ["python", "app.py"]
