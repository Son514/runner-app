import pika
import json
import os
import logging
import time
import pymongo
from pymongo.errors import ConnectionFailure
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
QUEUE_NAME = "geolocation_queue"

# MongoDB connection parameters
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost:30003")
MONGODB_URI = f"mongodb://{MONGODB_HOST}"

# FastAPI endpoint
FASTAPI_URL = "http://api-gateway:81/coordinates"

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
            logger.info(f"data after insertion: {data}")
        else:
            logger.warning("No MongoDB connection, data not stored")
        
        # Send data to FastAPI
        try:
            response = requests.post(FASTAPI_URL, json=json.loads(body))
            if response.status_code == 200:
                logger.info("Data sent to FastAPI")
            else:
                logger.error(f"Failed to send data to FastAPI: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error sending data to FastAPI: {e}")
        
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
                db = mongodb_client["testdb"]
            else:
                logger.warning("MongoDB not connected, continuing without DB")

        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq()
        if channel:
            try:
                channel.basic_qos(prefetch_count=1)
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

        # Check MongoDB connection
        if mongodb_client:
            try:
                mongodb_client.admin.command('ping')
            except:
                logger.warning("MongoDB connection lost, will retry")
                mongodb_client.close()
                mongodb_client = None
                db = None

        time.sleep(5)
        logger.info("Retrying connections...")

if __name__ == "__main__":
    main()