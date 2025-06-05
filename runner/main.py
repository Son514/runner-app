import pika
import json
import os
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
QUEUE_NAME = "geolocation_queue"

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        logger.info(f"Received data: {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def connect_to_rabbitmq():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        logger.info("Connected to RabbitMQ")
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error connecting to RabbitMQ: {e}")
        return None, None

def main():
    while True:
        connection, channel = connect_to_rabbitmq()
        if channel:
            try:
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
                logger.info("Waiting for messages...")
                channel.start_consuming()
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")
            finally:
                connection.close()
                logger.info("Connection closed")
        time.sleep(5)  # Retry connection after 5 seconds if failed
        logger.info("Retrying connection...")

if __name__ == "__main__":
    main()