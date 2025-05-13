from datetime import datetime
from airflow import DAG #type: ignore
from airflow.operators.python import PythonOperator #type: ignore
import json
import requests #type: ignore
from kafka import KafkaProducer #type: ignore
import time

default_arg = {
    'owner' : 'copter',
    'start_date': datetime(2023,10,1, 12, 00)
}
def api_url():
    url = f'http://api.exchangeratesapi.io/v1/latest?access_key=YOUR_APIKEY' #Replace your API key
    res = requests.get(url)
    res = res.json()
    return res


        
def stream_data():
    import logging
    from kafka import KafkaProducer
    import json
    import time

    # Kafka Producers
    producer = KafkaProducer(bootstrap_servers=['broker1:29092'], max_block_ms=5000)
    
    # Initialize current_rate_JPY as an empty dictionary
    current_rate_JPY = {}
    
    try:
        data = api_url()  # Call the api_url function, which already returns a dictionary
        if data.get('success', False):  # Check if the API response indicates success
            if 'error' not in data:
                rates = data['rates']
                jpy_rate = rates['JPY']  # Get the JPY rate from the API
                
                # Convert all rates to be based on JPY
                for currency, rate in rates.items():
                    current_rate_JPY[currency] = rate / jpy_rate
                
                print(f"Current exchange rates based on JPY: {current_rate_JPY}")
            else:
                print(f"Error: {data['error']['info']}")
        else:
            print(f"Failed to fetch data")
        producer.send('currency_from_API', json.dumps(current_rate_JPY).encode('utf-8'))
        logging.info('Currency data sent to Kafka')
    except Exception as e:
        logging.error(f"An error occurred: {e}")

                

with DAG('currency_pipeline',
         default_args=default_arg,
         schedule_interval='@daily', # run the DAG daily
         catchup=False) as dag:
    
    steaming_task = PythonOperator(
        task_id='streaming_data',
        python_callable=stream_data)
