import pika
import json
import os
import logging
import time
import pymongo
from pymongo.errors import ConnectionFailure

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
QUEUE_NAME = "geolocation_queue"

# MongoDB connection parameters
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost:30003")
MONGODB_URI = f"mongodb://{MONGODB_HOST}"

def connect_to_mongodb():
    try:
        client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test connection
        logger.info("Connected")
        return client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"MongoDB error: {e}")
        return None

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

def callback(ch, method, properties, body, db):
    try:
        data = json.loads(body)
        logger.info(f"Received data: {data}")
        if db is not None:
            # Store data in MongoDB
            db.testcollection.insert_many(data)
            logger.info("Data stored in MongoDB")
        else:
            logger.warning("No MongoDB connection, data not stored")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    mongodb_client = None
    db = None
    while True:
        # Connect to MongoDB
        if not mongodb_client:
            mongodb_client = connect_to_mongodb()
            if mongodb_client:
                db = mongodb_client["testdb"]  # Use or create database
            else:
                logger.warning("MongoDB not connected, continuing without DB")

        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq()
        if channel:
            try:
                channel.basic_qos(prefetch_count=1)
                # Pass the MongoDB database to the callback
                channel.basic_consume(
                    queue=QUEUE_NAME,
                    on_message_callback=lambda ch, method, props, body: callback(ch, method, props, body, db)
                )
                logger.info("Waiting for messages...")
                channel.start_consuming()
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")
            finally:
                if connection:
                    connection.close()
                    logger.info("RabbitMQ connection closed")
        else:
            logger.warning("RabbitMQ not connected, retrying...")

        # If MongoDB connection failed, reset to retry
        if mongodb_client and not mongodb_client.admin.command('ping'):
            logger.warning("MongoDB connection lost, will retry")
            mongodb_client.close()
            mongodb_client = None
            db = None

        time.sleep(5)  # Retry after 5 seconds if failed
        logger.info("Retrying connections...")

if __name__ == "__main__":
    main()