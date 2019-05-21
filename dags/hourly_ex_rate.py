from get_currency import ExchangeRate
import psycopg2
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

currency_list = ('usd', 'eur', 'plz', 'czk', 'gbp', 'btc')
def update_table(currency):
    """
    Connect to the PostgreSQL database
    """
    input = ExchangeRate(currency)
    conn = None
    updated_rows = 0
    ###
    now = datetime.now().strftime('%Y-%m-%d, %H:%M')
    sql = """
INSERT INTO currencies_hourly (date_time, ccy, pair, provider, buy, sell)
/**/
VALUES (%s, %s, %s, %s, %s, %s);
""".format(currency)
    data = (now, input.ccy(),f'{input.base_ccy()}/{input.ccy()}', input.bank(), float(input.buy()), float(input.sell()))
    try:
        # connect to the PostgreSQL server
        print('Trying to connect to the server')
        conn = psycopg2.connect(database='exchange_rate', user='yurii', password='yurii', host='localhost')

        # create a cursor
        cur = conn.cursor()

        # Execute a statement
        cur.execute(sql, data)
        updated_rows = cur.rowcount

        # Commit changes to the DB
        conn.commit()

        # Close a communication with SQL
        cur.close()
        print('Closed communication with database')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Closed Database connection')
def run():
    for currency in currency_list:
        update_table(currency)

default_args = {
'owner': 'yurii',
'depends_on_past': False,
'start_date': datetime(2018, 8, 11),
'email': ['airflow@example.com'],
'email_on_failure': ['no_mail@nohost.org'],
'email_on_retry': False,
'retries': 1,
'backfill':False,
}

hourly_currency_dag = DAG('currency_hourly', default_args=default_args, catchup=False, schedule_interval='@hourly')

t1 = PythonOperator(task_id='do_all', python_callable=run, dag=hourly_currency_dag)
t0 = DummyOperator(task_id='do_nothing', dag=hourly_currency_dag)
t1 >> t0
