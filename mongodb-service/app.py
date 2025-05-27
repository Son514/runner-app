from flask import Flask, request, jsonify
from pymongo import MongoClient
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection parameters
MONGO_URI = 'mongodb://localhost:27017'
DATABASE_NAME = 'runner_db'
COLLECTION_NAME = 'geolocation_data'

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route('/store', methods=['POST'])
def store_data():
    try:
        data = request.get_json()
        if not data:
            logger.error("No data provided in request")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400

        # Expect an array of objects
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            logger.error("Data must be an array of JSON objects")
            return jsonify({
                "status": "error",
                "message": "Data must be an array of JSON objects"
            }), 400

        # Insert multiple documents into MongoDB
        result = collection.insert_many(data)
        logger.info(f"Inserted {len(result.inserted_ids)} documents.")

        return jsonify({
            "status": "success",
            "message": f"Inserted {len(result.inserted_ids)} documents",
            "inserted_ids": [str(_id) for _id in result.inserted_ids]
        }), 200

    except Exception as e:
        logger.error(f"Error storing data in MongoDB: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error storing data: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)