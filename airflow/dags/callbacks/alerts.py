import logging
from airflow.utils.email import send_email

def on_failure_alert(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    execution_date = context["execution_date"]
    exception = context.get("exception", "No exception details available")
    log_url = context["task_instance"].log_url

    subject = f"[Airflow] DAG failed: {dag_id} — {task_id}"

    body = f"""
    <h3>Task failed in Airflow</h3>
    <ul>
        <li><b>DAG:</b> {dag_id}</li>
        <li><b>Task:</b> {task_id}</li>
        <li><b>Execution date:</b> {execution_date}</li>
        <li><b>Exception:</b> {exception}</li>
        <li><b>Log:</b> <a href="{log_url}">{log_url}</a></li>
    </ul>
    """

    send_email(
        to="robertorodriguez7288@gmail.com",
        subject=subject,
        html_content=body,
    )

    logging.info(f"Failure alert sent for {dag_id}.{task_id}")