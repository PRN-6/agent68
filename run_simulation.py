import uvicorn
import sys
import os

# Add backend directory to sys.path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

if __name__ == "__main__":
    print("=" * 60)
    print("PROJECT GENESIS: Autonomous AI Society Simulation Engine")
    print("Inhabiting 25 generative agents in a continuous virtual world.")
    print("Server running on: http://127.0.0.1:8000")
    print("WebSocket stream: ws://127.0.0.1:8000/ws/simulation")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
