from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import os
from datetime import datetime, timedelta

default_args = {
    'owner':'babaj',
    'retries': 1,
    'email_on_retry':'no_mail@nohost.org',
    'email_on_failure':'no_mail@nohost.org',
    'depends_on_past':False,
    'start_date':datetime(2009,12,1)}

dag = DAG('monthly_dag', default_args=default_args, catchup=True, schedule_interval='@monthly')

def func_1(path, filename):
    f = open(os.path.join(path, filename), 'a')
    f.write(f'Time: {datetime.now().hour}:{datetime.now().minute:02}:{datetime.now().second:02}\n')
    f.close()

func_2 = lambda: print(2 + 2)

run_first = PythonOperator(
    task_id='first_monthly_task',
    python_callable=func_1,
    op_kwargs={'path':'/home/yurii/Desktop/new', 'filename':'monthly.txt'},
    dag=dag)

run_second = PythonOperator(task_id='second_monthly_task',
    python_callable=func_2,
    dag=dag)

run_first << run_second
