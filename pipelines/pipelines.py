import pandas as pd
from airflow.models.xcom import XCom
from airflow.providers.postgres.hooks.postgres import PostgresHook


def _proces_todo(ti: XCom) -> None:
    """process todo
        This processes the todo json response from the HTTP operator

    Args:
        ti (XCom): airflow XCom push output from extract todo
    """
    todo = ti.xcom_pull(task_ids="extract_todos")

    processed = pd.DataFrame(todo)
    processed.to_csv("./processed_todo.csv", index=None, header=False)
    print(processed)


def _store_todos():
    """Store processed todo to csv in postgres db"""

    hook = PostgresHook(postgres_conn_id="postgres_user_conn")
    hook.copy_expert(
        sql="COPY todos FROM stdin WITH DELIMITER as ','",
        filename="./processed_todo.csv",
    )
