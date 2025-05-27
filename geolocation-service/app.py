from flask import Flask, jsonify
import requests
import logging
import threading
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Racemap API endpoint
RACEMAP_API_URL = "https://racemap.com/api/data/v1/66bf4318d1c783279d183dd3/current"
# Queue microservice endpoint
QUEUE_MICROSERVICE_URL = "http://localhost:5001/enqueue"

def periodic_fetch():
    while True:
        try:
            response = requests.get(RACEMAP_API_URL)
            if response.status_code == 200:
                data = response.json()
                logger.info("Periodic fetch: Successfully fetched data from Racemap API")
                try:
                    queue_response = requests.post(QUEUE_MICROSERVICE_URL, json=data)
                    if queue_response.status_code == 200:
                        logger.info("Periodic fetch: Successfully sent data to queue microservice")
                    else:
                        logger.error(f"Periodic fetch: Failed to send data to queue microservice: {queue_response.status_code}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Periodic fetch: Error sending to queue microservice: {str(e)}")
            else:
                logger.error(f"Periodic fetch: Failed to fetch data from Racemap API: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Periodic fetch: Error connecting to Racemap API: {str(e)}")
        time.sleep(5)

if __name__ == '__main__':
    # Start background thread
    fetch_thread = threading.Thread(target=periodic_fetch, daemon=True)
    fetch_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)