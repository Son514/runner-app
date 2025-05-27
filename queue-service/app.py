from flask import Flask, request, jsonify
import pika
import json
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'geolocation_queue'

def publish_to_queue(data):
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        
        # Declare queue
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        logger.info("Message published to queue")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Failed to publish to queue: {str(e)}")
        return False

@app.route('/enqueue', methods=['POST'])
def enqueue():
    try:
        data = request.get_json()
        if not data:
            logger.error("No data provided in request")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # Publish to RabbitMQ
        if publish_to_queue(data):
            return jsonify({
                "status": "success",
                "message": "Data enqueued successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to enqueue data"
            }), 500

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error processing request: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)