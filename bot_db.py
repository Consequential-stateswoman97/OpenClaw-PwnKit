import json
import os
import tempfile
import threading
from typing import Dict, Any

DB_FILE = "bots_db.json"
db_lock = threading.Lock()

def load_bots() -> Dict[str, Dict[str, Any]]:
    with db_lock:
        if not os.path.exists(DB_FILE):
            return {}
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_bot(target_id: str, webhook_url: str, secret_key: str, metadata: dict = None):
    with db_lock:
        bots = {}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    bots = json.load(f)
            except:
                pass
        
        bots[target_id] = {
            "webhook_url": webhook_url,
            "secret_key": secret_key,
            "metadata": metadata or {},
            "status": "alive"
        }
        
        # 原子写入防止文件损坏
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(DB_FILE)) or '.')
        with os.fdopen(fd, 'w', encoding="utf-8") as f:
            json.dump(bots, f, indent=4)
        os.replace(tmp_path, DB_FILE)

def remove_bot(target_id: str):
    with db_lock:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                bots = json.load(f)
            if target_id in bots:
                del bots[target_id]
                fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(DB_FILE)) or '.')
                with os.fdopen(fd, 'w', encoding="utf-8") as f:
                    json.dump(bots, f, indent=4)
                os.replace(tmp_path, DB_FILE)