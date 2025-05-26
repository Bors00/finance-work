from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.operators.dummy import DummyOperator
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
    "ETF",
    default_args=default_args,
    description="DAG pour l'extraction de données macroéconomiques et boursières",
    schedule_interval=None,
    catchup=False,
)

log_files = {
    "etf": "../../app/stocks/last_processed_etf.txt"
}

extractions = {
    "etf": {
        "log": log_files["etf"],
        "interval": 1,
        "notebook": "../../app/Extract_ETF.ipynb"
    }
}

# Dummy task intermédiaire
wait_for_extractions = DummyOperator(
    task_id="wait_for_extractions",
    trigger_rule=TriggerRule.ONE_SUCCESS,
    dag=dag,
)

# Tâche alternative si aucune extraction n'est lancée
skip_extraction = PythonOperator(
    task_id="skip_extraction",
    python_callable=skip_message,
    op_args=["Aucune extraction nécessaire. Les données sont à jour."],
    trigger_rule=TriggerRule.ALL_SKIPPED,
    dag=dag,
)

# Chargement
load_task = PythonOperator(
    task_id="load_data",
    python_callable=run_notebook,
    op_args=["../../app/load_etf.ipynb"],
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

wait_for_extractions >> load_task  # s'exécute uniquement si au moins une extraction a réussi

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
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    update_log = PythonOperator(
        task_id=f"update_log_{key}",
        python_callable=log_last_run,
        op_args=[meta["log"]],
        dag=dag,
    )

    # Wiring logique
    check >> extract
    check >> skip_extraction
    extract >> wait_for_extractions
    extract >> update_log
