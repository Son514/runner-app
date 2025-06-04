from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Model for incoming coordinates
class Coordinates(BaseModel):
    latitude: float
    longitude: float

# Store connected WebSocket clients
connected_clients = []

@app.post("/coordinates")
async def receive_coordinates(coords: Coordinates):
    # Broadcast coordinates to all connected WebSocket clients
    for client in connected_clients:
        await client.send_json({"latitude": coords.latitude, "longitude": coords.longitude})
    return {"message": "Coordinates received and broadcasted"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Keep connection alive; no need to process incoming messages for this example
            await websocket.receive_text()
    except Exception:
        connected_clients.remove(websocket)
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)