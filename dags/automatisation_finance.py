from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime, timedelta
import subprocess
import os
from airflow.utils.trigger_rule import TriggerRule


def run_notebook(notebook_path):
    command = [
        "python", "-m", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--stdout",
        notebook_path
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Exécution réussie de {notebook_path}.\nSortie : {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de {notebook_path}.\nErreur : {e.stderr}")
        raise

def log_last_run(log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    today = datetime.today().strftime('%Y%m%d')
    with open(log_file, "w") as f:
        f.write(f"{today}\n")
    print(f"Fichier de log mis à jour : {log_file}")


def check_interval(log_file, interval_days):
    if not os.path.exists(log_file):
        print(f"[{log_file}] introuvable → extraction nécessaire")
        return True
    with open(log_file, "r") as f:
        last_run = datetime.strptime(f.read().strip(), '%Y%m%d')
    days_elapsed = (datetime.today() - last_run).days
    print(f"[{log_file}] dernier run {last_run.date()} → {days_elapsed} jour(s) écoulé(s)")
    return days_elapsed >= interval_days

def skip_message(msg):
    print(msg)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 3, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    "extraction_et_chargement_donnees",
    default_args=default_args,
    description="DAG pour extraire et charger des données",
    schedule_interval="30 * * * *",
    catchup=False,
)

# Chemins des fichiers logs
log_files = {
    "macro_usa": "../../app/macroeconomics/last_processed_usa_macro.txt",
    "macro_canada": "../../app/macroeconomics/last_processed_canada_macro.txt",
    "sp500": "../../app/stocks/last_processed_sp500.txt",
    "tsx": "../../app/stocks/last_processed_tsx.txt"
}

# Paramètres des extractions
extractions = {
    "macro_usa": {
        "log": log_files["macro_usa"],
        "interval": 30,
        "notebook": "../../app/Extract_Macroeconomics_USA.ipynb"
    },
    "macro_canada": {
        "log": log_files["macro_canada"],
        "interval": 30,
        "notebook": "../../app/Extract_Macroeconomics_CAN.ipynb"
    },
    "sp500": {
        "log": log_files["sp500"],
        "interval": 1,
        "notebook": "../../app/Extract_S&P500.ipynb"
    },
    "tsx": {
        "log": log_files["tsx"],
        "interval": 1,
        "notebook": "../../app/Extract_TSX.ipynb"
    }
}


# Tâche alternative si aucune extraction n'est lancée
skip_extraction = PythonOperator(
    task_id="skip_extraction",
    python_callable=skip_message,
    op_args=["Aucune extraction nécessaire. Les données sont à jour."],
    trigger_rule=TriggerRule.ALL_SKIPPED,  # <- ne s’exécute que si TOUS les check_tasks sont SKIPPED
    dag=dag,
)

# Chargement
load_task = PythonOperator(
    task_id="load_data",
    python_callable=run_notebook,
    op_args=["../../app/load_data.ipynb"],
    # trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,  # <- au moins 1 extraction réussie
    trigger_rule=TriggerRule.ONE_SUCCESS,  # <— NE LANCE que si 1 upstream a réussi
    dag=dag,
)

for key, meta in extractions.items():
    check = ShortCircuitOperator(
        task_id=f"check_interval_{key}",
        python_callable=check_interval,
        op_args=[meta["log"], meta["interval"]],
        dag=dag,
    )

    extract = PythonOperator(
        task_id=f"extract_{key}",
        python_callable=run_notebook,
        op_args=[meta["notebook"]],
        dag=dag,
        trigger_rule=TriggerRule.ALL_SUCCESS,  # ne s’exécute que si le check a SUCCÉDÉ
    )

    update_log = PythonOperator(
        task_id=f"update_log_{key}",
        python_callable=log_last_run,
        op_args=[meta["log"]],
        dag=dag,
    )

    # wiring
    check >> extract      # extract ne tourne que si check renvoie True
    check >> skip_extraction  # si check renvoie False, il est SKIPPED et contribue à déclencher skip_extraction
    extract >> load_task     # chargement si au moins une extraction
    extract >> update_log    # mise à jour du log si extraction réussie