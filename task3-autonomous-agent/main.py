"""
Interactive Console CLI for Task 3: Multi-Tool Autonomous AI Agent.
Part of the AI Innovation Studio suite.
Features Rich audit traces, sequential tool orchestration, and sandbox boundaries.
"""

import os
import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from agent import AutonomousAgent, AgentRunResult


console = Console()


def render_audit_trace(result: AgentRunResult):
    """Format and display the agent's action-and-observation execution trace."""
    console.print()
    table = Table(
        title=f"🔍 Auditable ReAct Execution Trace ({result.total_steps} steps)",
        show_header=True,
        header_style="bold cyan",
        border_style="bright_blue",
    )

    table.add_column("Step", justify="center", style="bold white", width=6)
    table.add_column("Selected Tool", style="bold magenta", width=22)
    table.add_column("Arguments", style="yellow", width=28)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Latency", justify="right", style="cyan", width=10)
    table.add_column("Observation Excerpt", style="green")

    for ev in result.events:
        status_color = "[bold green]PASS[/bold green]" if ev.status == "SUCCESS" else "[bold red]FAIL[/bold red]"
        arg_str = ", ".join(f"{k}='{v}'" for k, v in ev.tool_args.items())
        table.add_row(
            str(ev.step),
            ev.tool_name,
            arg_str[:26] + ("..." if len(arg_str) > 26 else ""),
            status_color,
            f"{ev.duration_ms:.1f}ms",
            ev.observation[:65] + ("..." if len(ev.observation) > 65 else ""),
        )

    console.print(table)
    console.print()

    # Final Answer Panel
    panel = Panel(
        Markdown(result.final_answer),
        title=f"[bold cyan]🎯 Final Agent Response[/bold cyan] ([dim]{result.provider_used} • {result.total_duration_ms:.1f}ms[/dim])",
        border_style="magenta",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def main():
    parser = argparse.ArgumentParser(description="Multi-Tool Autonomous AI Agent CLI")
    parser.add_argument("--query", "-q", type=str, help="Question or task to run through the agent")
    parser.add_argument("--steps", "-s", type=int, default=6, help="Maximum execution steps (default: 6)")
    parser.add_argument("--provider", "-p", type=str, default="auto", choices=["auto", "gemini", "openai", "offline"], help="LLM Provider")

    args = parser.parse_args()

    agent = AutonomousAgent(provider=args.provider, max_steps=args.steps)

    console.print(Panel(
        "[bold cyan]AI INNOVATION STUDIO[/bold cyan] • [bold magenta]Task 3: Autonomous Multi-Tool Agent[/bold magenta]\n"
        "[dim]Tools: DuckDuckGo Search | AST Safe Calculator | Sandboxed File Reader[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))

    if args.query:
        console.print(f"[bold yellow]Executing Query:[/bold yellow] {args.query}")
        result = agent.run(args.query)
        render_audit_trace(result)
    else:
        # Interactive mode
        console.print("[dim]Type your multi-step compound query or type 'exit' to quit.[/dim]")
        console.print("[dim]Examples:\n - Read system_specs.json and calculate total cluster RAM.\n - Read quarterly_earnings.txt and calculate annual revenue.\n - Search DuckDuckGo for latest Python version features.[/dim]\n")

        while True:
            try:
                user_input = console.input("[bold green]Agent Prompt > [/bold green]").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    console.print("[bold yellow]Exiting agent console. Goodbye![/bold yellow]")
                    break

                with console.status("[cyan]Agent reasoning and executing tools...[/cyan]"):
                    result = agent.run(user_input)

                render_audit_trace(result)
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted.[/yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")


if __name__ == "__main__":
    main()
