import json, sys, os
import pandas as pd
from datetime import datetime
from airflow import DAG
from airflow.models.xcom import XCom
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook



BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_PATH)
from pipelines.pipelines import _proces_todo, _store_todos


with DAG(
    dag_id="first_test_dag",
    default_args={"owner": "Best Nyah"},
    start_date=datetime(2023, 11, 6),
    schedule="@daily",
    catchup=False,
) as dag:
    create_table_todo = SQLExecuteQueryOperator(
        task_id="create_table_todo",
        conn_id="postgres_user_conn",
        sql="""
            CREATE TABLE IF NOT EXISTS todos (
                userId INTEGER NOT NULL,
                id INTEGER NOT NULL,
                title TEXT NOT NULL,
                completed BOOLEAN NOT NULL
            );
            """,
        show_return_value_in_logs=True,
    )

    # free  API endpoint for test from -->  https://jsonplaceholder.typicode.com
    test_api_enpoint = HttpSensor(
        task_id="is_api_available",
        method="GET",
        http_conn_id="todo_api",
        endpoint="/users/1/todos",
    )

    extract_todos = SimpleHttpOperator(
        task_id="extract_todos",
        method="GET",
        http_conn_id="todo_api",
        endpoint="/users/1/todos",
        log_response=True,
        response_filter=lambda response: json.loads(response.text),
    )

    process_todos = PythonOperator(
        task_id="process_todos",
        python_callable=_proces_todo,
        show_return_value_in_logs=True,
    )
    # extract_todos >> process_todos

    store_todos = PythonOperator(
        task_id="store_todos",
        python_callable=_store_todos,
        show_return_value_in_logs=True,
    )

    (
        create_table_todo >> test_api_enpoint >> extract_todos >> process_todos >> store_todos
    )
