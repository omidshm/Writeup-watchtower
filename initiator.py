
import os
from rich.console import Console
from rich.table import Table

console = Console()

# List of filenames
filenames = ["tags.txt", "youtube_channels.txt", "rss_feeds.txt"]

# Table to display file status
table = Table(title="File Creation Status")

table.add_column("Filename", style="cyan", no_wrap=True)
table.add_column("Status", style="green")

# Iterate over the list of filenames
for filename in filenames:
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            pass  # Create an empty file
        table.add_row(filename, "[bold green]Created[/bold green]")
    else:
        table.add_row(filename, "[bold red]Already Exists[/bold red]")

# Print the table
console.print(table)

console.print("[green][+][/green] [bold magenta]Files checked and created if they didn't exist.[/bold magenta]")

