from flask import Flask, jsonify, request
import asyncio
import websockets
import json
import logging
from threading import Thread

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for latest data
latest_data = None

# Set to store WebSocket clients
connected_clients = set()

async def websocket_handler(websocket):
    global connected_clients
    try:
        # Register client
        connected_clients.add(websocket)
        logger.info("WebSocket client connected")
        
        # Keep connection open
        async for message in websocket:
            pass  # No client messages expected for now
        
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket client disconnected")
    finally:
        connected_clients.remove(websocket)

async def broadcast_data(data):
    global connected_clients
    if connected_clients:
        # Convert data to JSON string
        message = json.dumps(data)
        # Send to all connected clients
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )
        logger.info("Broadcasted data to WebSocket clients")

@app.route('/receive', methods=['POST'])
def receive_data():
    global latest_data
    try:
        data = request.get_json()
        if not data:
            logger.error("No data provided in request")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # Store the latest data
        latest_data = data
        logger.info("Data received and stored in API Gateway")
        
        # Broadcast to WebSocket clients
        asyncio.run(broadcast_data(data))
        
        return jsonify({
            "status": "success",
            "message": "Data received successfully"
        }), 200

    except Exception as e:
        logger.error(f"Error receiving data: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error receiving data: {str(e)}"
        }), 500

@app.route('/data', methods=['GET'])
def get_data():
    try:
        if latest_data is None:
            logger.warning("No data available")
            return jsonify({
                "status": "error",
                "message": "No data available"
            }), 404
        
        logger.info("Returning latest data")
        return jsonify({
            "status": "success",
            "data": latest_data
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving data: {str(e)}"
        }), 500

def start_websocket_server():
    async def run_server():
        async with websockets.serve(websocket_handler, "0.0.0.0", 8765):
            await asyncio.Future()  # run forever

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_server())

if __name__ == '__main__':
    # Start WebSocket server in a separate thread
    websocket_thread = Thread(target=start_websocket_server)
    websocket_thread.daemon = True
    websocket_thread.start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=False)