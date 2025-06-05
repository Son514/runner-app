import requests
import pika
import json
import time
import os

# API endpoint
API_URL = "https://racemap.com/api/data/v1/66bf4318d1c783279d183dd3/current"

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
QUEUE_NAME = "geolocation_queue"

def fetch_geolocation_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def connect_to_rabbitmq():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return None, None

def main():
    while True:
        # Fetch data
        data = fetch_geolocation_data()
        if data:
            # Connect to RabbitMQ
            connection, channel = connect_to_rabbitmq()

            # Extract runners
            starters = data["starters"][:2]
            print(f"Starters: {starters}")

            if channel:
                try:
                    # Publish data to queue
                    channel.basic_publish(
                        exchange="",
                        routing_key=QUEUE_NAME,
                        body=json.dumps(starters),
                        properties=pika.BasicProperties(delivery_mode=2)  # Persistent
                    )
                    print("Data sent to queue")
                except Exception as e:
                    print(f"Error publishing to queue: {e}")
                finally:
                    connection.close()
        else:
            print("No data to send")
        
        # Wait before next fetch
        time.sleep(60)  # Fetch every 60 seconds

if __name__ == "__main__":
    main()