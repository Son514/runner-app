import pika
import json
import os

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
QUEUE_NAME = "geolocation_queue"

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"Received data: {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def connect_to_rabbitmq():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return None, None

def main():
    while True:
        connection, channel = connect_to_rabbitmq()
        if channel:
            try:
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
                print("Waiting for messages...")
                channel.start_consuming()
            except Exception as e:
                print(f"Error in consumer: {e}")
            finally:
                connection.close()
        time.sleep(5)  # Retry connection after 5 seconds if failed

if __name__ == "__main__":
    main()