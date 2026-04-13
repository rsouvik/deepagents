import argparse
import asyncio
import os
import sys

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()


POSTGRES_SYSTEM_PROMPT = """
You are a SQL assistant connected to a PostgreSQL database via MCP tools.

Rules:
- Use PostgreSQL syntax only.
- Never use SQLite-specific objects or syntax such as `sqlite_master`, `PRAGMA`, or `AUTOINCREMENT`.
- For table discovery, use PostgreSQL metadata patterns when needed, e.g. `information_schema.tables` with `table_schema = 'public'`.
- Prefer schema-aware exploration first, then run precise queries.
""".strip()

async def create_sql_deep_agent() -> object:
    """Create and return a text-to-SQL Deep Agent"""

    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Initialize model used for tool selection and SQL generation.
    model = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)

    client = MultiServerMCPClient({
        "database": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://xxxx:xxxx:5432/sleep_metrics"],
            "transport": "stdio",
        }
    })

    db_tools = await client.get_tools()

    # Create the Deep Agent with MCP database tools.
    agent = create_deep_agent(
        model=model,  # Claude Sonnet 4.5 with temperature=0
        system_prompt=POSTGRES_SYSTEM_PROMPT,
        memory=["./AGENTS.md"],  # Agent identity and general instructions
        skills=[
            "./skills/"
        ],  # Specialized workflows (query-writing, schema-exploration)
        tools=db_tools,  # SQL database tools
        subagents=[],  # No subagents needed
        backend=FilesystemBackend(root_dir=base_dir),  # Persistent file storage

    )

    return agent

async def main() -> None:
    """Main entry point for the SQL Deep Agent CLI"""
    parser = argparse.ArgumentParser(
        description="Text-to-SQL Deep Agent powered by LangChain Deep Agents and Claude Sonnet 4.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "What are the top 5 best-selling artists?"
  python agent.py "Which employee generated the most revenue by country?"
  python agent.py "How many customers are from Canada?"
        """,
    )
    parser.add_argument(
        "question",
        type=str,
        help="Natural language question to answer using the Chinook database",
    )

    args = parser.parse_args()

    # Display the question
    console.print(
        Panel(f"[bold cyan]Question:[/bold cyan] {args.question}", border_style="cyan")
    )
    console.print()

    # Create the agent
    console.print("[dim]Creating SQL Deep Agent...[/dim]")
    agent = await create_sql_deep_agent()

    # Invoke the agent
    console.print("[dim]Processing query...[/dim]\n")

    try:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": args.question}]}
        )

        # Extract and display the final answer
        final_message = result["messages"][-1]
        answer = (
            final_message.content
            if hasattr(final_message, "content")
            else str(final_message)
        )

        console.print(
            Panel(f"[bold green]Answer:[/bold green]\n\n{answer}", border_style="green")
        )

    except Exception as e:
        console.print(
            Panel(f"[bold red]Error:[/bold red]\n\n{str(e)}", border_style="red")
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())