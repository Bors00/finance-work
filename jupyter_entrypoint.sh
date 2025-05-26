#!/bin/bash
# Démarrer Jupyter Notebook en arrière-plan
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token='' --NotebookApp.disable_check_xsrf=True --NotebookApp.allow_origin='*' &
JUPYTER_PID=$!
echo "Jupyter Notebook démarré en arrière-plan (PID: $JUPYTER_PID)"

# Attendre que les services dépendants soient accessibles
/app/wait_for_services.sh

echo "Exécution automatique des notebooks..."

papermill /app/init_db.ipynb
papermill /app/Extract_ETF.ipynb
papermill /app/Extract_Macroeconomics_CAN.ipynb
papermill /app/Extract_Macroeconomics_USA.ipynb
papermill "/app/Extract_S&P500.ipynb"
papermill /app/Extract_Sectors.ipynb
papermill /app/Extract_TSX.ipynb
papermill /app/load_data.ipynb
papermill /app/load_etf.ipynb

echo "Initialisation terminée. Le conteneur Jupyter reste actif."
wait $JUPYTER_PID
