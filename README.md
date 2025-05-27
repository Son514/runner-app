Real-Time Runner App
A real-time running app that fetches geolocation data from the Racemap API, processes it through a microservices architecture, and displays runner locations on a Mapbox map using a Vue.js frontend.
Project Structure

GeolocationMicroservice: Fetches data from Racemap API.
QueueMicroservice: Publishes data to RabbitMQ.
RunnerMicroservice: Consumes RabbitMQ messages and sends to MongoDB and API Gateway.
MongoDBMicroservice: Stores data in MongoDB.
APIGatewayMicroservice: Broadcasts data via WebSocket.
frontend: Vue.js app displaying data on a Mapbox map.

Setup

Install Python 3.8+, Node.js, RabbitMQ, MongoDB.
Set up virtual environments and install dependencies for each microservice.
Install Vue.js dependencies in frontend/runner-app.
Configure Mapbox token in frontend/runner-app/.env.
Run microservices and the Vue.js app.

Running

Start MongoDB and RabbitMQ:net start MongoDB
net start RabbitMQ

Run each microservice in separate Command Prompts:cd GeolocationMicroservice && venv\Scripts\activate && python app.py
cd QueueMicroservice && venv\Scripts\activate && python queue_service.py
cd RunnerMicroservice && venv\Scripts\activate && python runner_service.py
cd MongoDBMicroservice && venv\Scripts\activate && python mongodb_service.py
cd APIGatewayMicroservice && venv\Scripts\activate && python api_gateway_service.py

Run the Vue.js app:cd frontend\runner-app && npm run serve

Access the app at http://localhost:8080.

Testing

Use Postman to send a GET request to http://localhost:5000/geolocation.
Verify runner locations on the Mapbox map at http://localhost:8080.

Dependencies

Python: Flask, requests, pika, pymongo, websockets
Node.js: Vue.js, mapbox-gl
