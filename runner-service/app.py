import pika
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'geolocation_queue'

# Microservice endpoints
MONGODB_MICROSERVICE_URL = 'http://localhost:5002/store'
API_GATEWAY_MICROSERVICE_URL = 'http://localhost:5003/receive'

def callback(ch, method, properties, body):
    try:
        # Parse the message
        data = json.loads(body)
        starters = data['starters'][:10]
        logger.info(f"Received data: {starters}")
        
        # Send data to MongoDB microservice
        try:
            response = requests.post(MONGODB_MICROSERVICE_URL, json=starters)
            if response.status_code == 200:
                logger.info("Successfully sent data to MongoDB microservice")
            else:
                logger.error(f"Failed to send data to MongoDB microservice: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending to MongoDB microservice: {str(e)}")
        
        # Send data to API Gateway microservice
        try:
            response = requests.post(API_GATEWAY_MICROSERVICE_URL, json=starters)
            if response.status_code == 200:
                logger.info("Successfully sent data to API Gateway microservice")
            else:
                logger.error(f"Failed to send data to API Gateway microservice: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending to API Gateway microservice: {str(e)}")
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        
        # Declare queue
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        # Consume messages
        channel.basic_qos(prefetch_count=1)  # Process one message at a time
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
        
        logger.info("Starting consumer. Waiting for messages...")
        channel.start_consuming()
        
    except Exception as e:
        logger.error(f"Consumer error: {str(e)}")
        connection.close()

if __name__ == '__main__':
    main()