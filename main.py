import sys
sys.stdout.reconfigure(encoding='utf-8')

import typer
from app import agent

app = typer.Typer()

@app.command()
def main(url: str = typer.Option(..., "--url", help="Public URL to generate Launch Kit from")):
    try:
        output_path = agent.run(url)
        print("✓ Launch Kit generated successfully")
        print(f"✓ File: {output_path}")
    except Exception as e:
        print(f"Failed to generate Launch Kit: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
