import typer
from pathlib import Path
from app import agent

app = typer.Typer()

@app.command()
def main(url: str = typer.Option(..., "--url", help="Public URL to generate launch kit from")):
    try:
        output_path = agent.run(url)
        print(f"✓ Launch Kit generated successfully")
        print(f"✓ File: {output_path}")
    except Exception as e:
        print(f"Failed to generate launch kit: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
