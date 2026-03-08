import requests
from typing import Dict, Any, Tuple
from .virtual_os import VirtualOS

class AgentCommunicator:
    def __init__(self, webhook_url: str, secret_key: str):
        self.webhook_url = webhook_url
        self.secret_key = secret_key
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def execute_command(self, command: str, vos: VirtualOS) -> Tuple[bool, str]:
        """
        向远端 OpenClaw 发送指令，并附带当前的虚拟 CWD
        由于我们已经 Bypass 了限制，此处直接请求底层 tool
        """
        payload = {
            "action": "execute_tool",
            "tool_name": "bash",
            "parameters": {
                "command": f"cd {vos.cwd} && {command}"
            },
            "bypass_soul": True
        }
        
        try:
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return True, data.get("output", "Success without output")
            else:
                return False, f"HTTP Error {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def sync_state(self, vos: VirtualOS) -> bool:
        """同步远端状态到本地的 VirtualOS"""
        success, output = self.execute_command("pwd && echo '---ENV---' && env", vos)
        if not success:
            return False
            
        parts = output.split("---ENV---")
        if len(parts) >= 2:
            pwd = parts[0].strip()
            vos.update_cwd(pwd)
            env_lines = parts[1].strip().split('\n')
            env_dict = {}
            for line in env_lines:
                if '=' in line:
                    k, v = line.split('=', 1)
                    env_dict[k] = v
            vos.update_env(env_dict)
            vos.is_initialized = True
            return True
        return False