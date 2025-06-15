from fastapi import FastAPI, WebSocket, Request
import uvicorn

app = FastAPI()

# Store connected WebSocket clients
connected_clients = []

@app.post("/coordinates")
async def receive_coordinates(request: Request):
    # Get raw JSON data
    data = await request.json()
    # Broadcast data to all connected WebSocket clients
    for client in connected_clients:
        await client.send_json(data)
    return {"message": "Data received and broadcasted"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Keep connection alive; no need to process incoming messages
            await websocket.receive_text()
    except Exception:
        connected_clients.remove(websocket)
        await websocket.close()

# Health check endpoint for Kubernetes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)