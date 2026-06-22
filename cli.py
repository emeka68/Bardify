#!/usr/bin/env python3
"""
Shakespeare Translator — CLI Tool

Transform modern English into Shakespearean English from the command line.

Usage:
    shakespeare "Hello, how are you?"
    echo "Hey, what's up?" | shakespeare
    shakespeare --file input.txt
    shakespeare --interactive
"""

import click
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from transformer import transformer
from config import settings


@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0", prog_name="shakespeare")
@click.pass_context
def cli(ctx):
    """🎭 Shakespeare Translator — Transform modern English into Shakespearean English"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("text", required=False)
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    help="Read input from file",
)
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    default="-",
    help="Write output to file (default: stdout)",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Interactive mode (read from stdin line by line)",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Quiet mode (output only transformed text)",
)
@click.option(
    "-t",
    "--show-tokens",
    is_flag=True,
    help="Show token usage",
)
def transform(text, file, output, interactive, quiet, show_tokens):
    """Transform modern English to Shakespearean English"""
    
    try:
        if interactive:
            _interactive_mode(output, quiet, show_tokens)
        elif file:
            _file_mode(file, output, quiet, show_tokens)
        elif text:
            _single_mode(text, output, quiet, show_tokens)
        else:
            _stdin_mode(output, quiet, show_tokens)
    
    except KeyboardInterrupt:
        click.echo("\n\n⚰️  Interrupted. Farewell!", err=True)
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


def _single_mode(text, output, quiet, show_tokens):
    """Transform a single text string"""
    click.echo("⏳ Transforming...", err=True)
    
    result = transformer.transform(text)
    
    if result.get("error"):
        click.echo(f"❌ Error: {result['error']}", err=True)
        sys.exit(1)
    
    if not quiet:
        click.echo(f"📝 Original:\n{result['original']}\n", file=output)
        click.echo("🎭 Shakespearean:\n" + "=" * 50, file=output)
    
    click.echo(result["transformed"], file=output)
    
    if not quiet:
        click.echo("=" * 50, file=output)
    
    if show_tokens and result.get("usage"):
        click.echo(
            f"\n📊 Tokens: {result['usage']['total_tokens']} "
            f"(input: {result['usage']['input_tokens']}, "
            f"output: {result['usage']['output_tokens']})",
            err=True
        )


def _stdin_mode(output, quiet, show_tokens):
    """Read from stdin (pipe support)"""
    text = click.get_text_stream("stdin").read().strip()
    
    if not text:
        click.echo("❌ No input provided", err=True)
        sys.exit(1)
    
    _single_mode(text, output, quiet, show_tokens)


def _file_mode(file, output, quiet, show_tokens):
    """Transform text from a file"""
    text = file.read().strip()
    
    if not text:
        click.echo("❌ File is empty", err=True)
        sys.exit(1)
    
    _single_mode(text, output, quiet, show_tokens)


def _interactive_mode(output, quiet, show_tokens):
    """Interactive mode: read from stdin line by line"""
    click.echo("🎭 Shakespeare Translator — Interactive Mode", err=True)
    click.echo("Enter text to transform (Ctrl+C to exit):\n", err=True)
    
    while True:
        try:
            text = click.prompt("→")
            
            if not text.strip():
                continue
            
            result = transformer.transform(text)
            
            if result.get("error"):
                click.echo(f"❌ {result['error']}", err=True)
                continue
            
            click.echo(f"← {result['transformed']}")
            
            if show_tokens and result.get("usage"):
                click.echo(
                    f"   (Tokens: {result['usage']['total_tokens']})",
                    err=True
                )
        
        except KeyboardInterrupt:
            click.echo("\n\n⚰️  Farewell!", err=True)
            break


@cli.command()
def config():
    """Show configuration"""
    if not settings.validate():
        click.echo("❌ Configuration validation failed", err=True)
        sys.exit(1)
    
    settings.summary()


@cli.command()
def version():
    """Show version and dependencies"""
    click.echo("🎭 Shakespeare Translator v1.0.0")
    click.echo("\nDependencies:")
    click.echo("  • FastAPI/Uvicorn (backend)")
    click.echo("  • Anthropic Claude API (AI)")
    click.echo("  • Click (CLI)")
    click.echo("  • Python 3.8+")
    click.echo("\nBuilt by Nnaemeka Duru (@SirTivaa)")


@cli.command()
def examples():
    """Show usage examples"""
    examples_text = """
🎭 Shakespeare Translator — Usage Examples

1. Single text:
   shakespeare "Hey, what's up?"

2. From stdin (pipe):
   echo "Hello world" | shakespeare

3. From file:
   shakespeare --file input.txt

4. To file:
   shakespeare "Hello" --output output.txt

5. Interactive mode:
   shakespeare --interactive

6. Quiet mode (output only):
   shakespeare "Hey" --quiet

7. Show token usage:
   shakespeare "Hello" --show-tokens

8. Batch from file:
   cat input.txt | shakespeare

9. Chain with other commands:
   fortune | shakespeare

10. Show config:
    shakespeare config
    """
    click.echo(examples_text)


if __name__ == "__main__":
    cli()
