"""
CLI entry point for chinatea.house static site generator.

Usage:
    python -m execution.cli [command] [options]

Commands:
    init        Initialize the database
    validate    Validate data integrity
    stats       Show database statistics
    build       Generate static pages
    publish     Publish pages according to drip schedule
    export      Export data to JSON
    import      Import data from JSON
"""

import sys
from pathlib import Path
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from execution.data.db import Database
from execution.data.validate import DataValidator

console = Console()

# Default paths
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "canonical" / "tea.db"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "output"
DEFAULT_EXPORT_PATH = PROJECT_ROOT / "data" / "canonical" / "exports"


@click.group()
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
@click.pass_context
def cli(ctx, db):
    """Chinese Tea House - Static Site Generator"""
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = Path(db)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize the database with schema."""
    db_path = ctx.obj["db_path"]
    console.print(f"[blue]Initializing database at {db_path}[/blue]")

    try:
        db = Database(db_path)
        console.print("[green]Database initialized successfully![/green]")

        # Show empty stats
        stats = db.get_stats()
        console.print(f"Tables created: {len(stats)} entities tracked")
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate data integrity."""
    db_path = ctx.obj["db_path"]

    if not db_path.exists():
        console.print("[red]Database not found. Run 'init' first.[/red]")
        raise click.Abort()

    console.print("[blue]Running data validation...[/blue]")

    db = Database(db_path)
    validator = DataValidator(db)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Validating...", total=None)

        results = validator.validate_all()

        progress.update(task, completed=True)

    # Display results
    if results["errors"]:
        console.print(f"\n[red]Found {len(results['errors'])} errors:[/red]")
        for error in results["errors"]:
            console.print(f"  - {error}")
    else:
        console.print("\n[green]No errors found![/green]")

    if results["warnings"]:
        console.print(f"\n[yellow]Found {len(results['warnings'])} warnings:[/yellow]")
        for warning in results["warnings"]:
            console.print(f"  - {warning}")

    console.print(f"\n[blue]Validation complete:[/blue]")
    console.print(f"  Entities checked: {results['entities_checked']}")
    console.print(f"  Relationships verified: {results['relationships_verified']}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show database statistics."""
    db_path = ctx.obj["db_path"]

    if not db_path.exists():
        console.print("[red]Database not found. Run 'init' first.[/red]")
        raise click.Abort()

    db = Database(db_path)
    stats = db.get_stats()

    # Main entity counts table
    table = Table(title="Database Statistics")
    table.add_column("Entity", style="cyan")
    table.add_column("Count", justify="right", style="green")

    for entity, count in stats.items():
        if isinstance(count, int):
            table.add_row(entity.replace("_", " ").title(), str(count))

    console.print(table)

    # Tea tier breakdown
    if stats.get("teas_by_tier"):
        tier_table = Table(title="Teas by Tier")
        tier_table.add_column("Tier", style="cyan")
        tier_table.add_column("Count", justify="right", style="green")
        tier_table.add_column("Description", style="dim")

        tier_desc = {1: "Complete data", 2: "Good data", 3: "Basic data"}
        for tier, count in sorted(stats["teas_by_tier"].items()):
            tier_table.add_row(str(tier), str(count), tier_desc.get(tier, ""))

        console.print(tier_table)

    # Tea category breakdown
    if stats.get("teas_by_category"):
        cat_table = Table(title="Teas by Category")
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count", justify="right", style="green")

        for cat, count in sorted(stats["teas_by_category"].items()):
            cat_table.add_row(cat.title(), str(count))

        console.print(cat_table)

    # Page status breakdown
    if stats.get("pages_by_status"):
        page_table = Table(title="Pages by Status")
        page_table.add_column("Status", style="cyan")
        page_table.add_column("Count", justify="right", style="green")

        for status, count in stats["pages_by_status"].items():
            page_table.add_row(status.title(), str(count))

        console.print(page_table)


@cli.command()
@click.option("--incremental/--full", default=True, help="Incremental or full rebuild")
@click.option("--limit", default=0, help="Limit number of pages (0 = no limit)")
@click.option("--template", default=None, help="Only build specific template type")
@click.option("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output directory")
@click.pass_context
def build(ctx, incremental, limit, template, output):
    """Generate static pages."""
    db_path = ctx.obj["db_path"]
    output_path = Path(output)

    if not db_path.exists():
        console.print("[red]Database not found. Run 'init' and seed data first.[/red]")
        raise click.Abort()

    console.print(f"[blue]Building site...[/blue]")
    console.print(f"  Mode: {'Incremental' if incremental else 'Full'}")
    console.print(f"  Output: {output_path}")
    if limit:
        console.print(f"  Limit: {limit} pages")
    if template:
        console.print(f"  Template: {template}")

    try:
        from execution.build.generator import SiteGenerator

        db = Database(db_path)
        generator = SiteGenerator(db, output_path)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating pages...", total=None)

            result = generator.build(
                incremental=incremental,
                limit=limit if limit else None,
                template_filter=template
            )

            progress.update(task, completed=True)

        console.print(f"\n[green]Build complete![/green]")
        console.print(f"  Pages generated: {result['pages_generated']}")
        console.print(f"  Pages skipped: {result['pages_skipped']}")
        console.print(f"  Duration: {result['duration_seconds']:.2f}s")

        if result.get("errors"):
            console.print(f"\n[red]Errors: {len(result['errors'])}[/red]")
            for error in result["errors"][:10]:
                console.print(f"  - {error}")

    except ImportError as e:
        console.print(f"[yellow]Build module not yet implemented: {e}[/yellow]")


@cli.command()
@click.option("--drip/--all", default=True, help="Use drip schedule or publish all")
@click.option("--dry-run", is_flag=True, help="Show what would be published")
@click.option("--count", default=100, help="Number of pages to publish in drip mode")
@click.pass_context
def publish(ctx, drip, dry_run, count):
    """Publish pages according to drip schedule."""
    db_path = ctx.obj["db_path"]

    if not db_path.exists():
        console.print("[red]Database not found.[/red]")
        raise click.Abort()

    console.print(f"[blue]Publishing pages...[/blue]")
    console.print(f"  Mode: {'Drip' if drip else 'All'}")
    if drip:
        console.print(f"  Count: {count}")
    if dry_run:
        console.print(f"  [yellow]Dry run - no changes will be made[/yellow]")

    try:
        from execution.publish.drip import DripPublisher

        db = Database(db_path)
        publisher = DripPublisher(db)

        if drip:
            pages = publisher.get_next_batch(count)
        else:
            pages = publisher.get_all_pending()

        if dry_run:
            console.print(f"\n[blue]Would publish {len(pages)} pages:[/blue]")
            for page in pages[:20]:
                console.print(f"  - {page}")
            if len(pages) > 20:
                console.print(f"  ... and {len(pages) - 20} more")
        else:
            result = publisher.publish(pages)
            console.print(f"\n[green]Published {result['published']} pages[/green]")

    except ImportError as e:
        console.print(f"[yellow]Publish module not yet implemented: {e}[/yellow]")


@cli.command("export")
@click.option("--output", default=str(DEFAULT_EXPORT_PATH), help="Export directory")
@click.pass_context
def export_data(ctx, output):
    """Export data to JSON files."""
    db_path = ctx.obj["db_path"]
    output_path = Path(output)

    if not db_path.exists():
        console.print("[red]Database not found.[/red]")
        raise click.Abort()

    console.print(f"[blue]Exporting data to {output_path}[/blue]")

    db = Database(db_path)
    db.export_to_json(output_path)

    console.print("[green]Export complete![/green]")


@cli.command("import")
@click.option("--input", "input_dir", default=str(DEFAULT_EXPORT_PATH), help="Import directory")
@click.pass_context
def import_data(ctx, input_dir):
    """Import data from JSON files."""
    db_path = ctx.obj["db_path"]
    input_path = Path(input_dir)

    if not input_path.exists():
        console.print(f"[red]Import directory not found: {input_path}[/red]")
        raise click.Abort()

    console.print(f"[blue]Importing data from {input_path}[/blue]")

    db = Database(db_path)
    db.import_from_json(input_path)

    console.print("[green]Import complete![/green]")

    # Show new stats
    stats = db.get_stats()
    console.print(f"  Categories: {stats.get('categories', 0)}")
    console.print(f"  Regions: {stats.get('regions', 0)}")
    console.print(f"  Teas: {stats.get('teas', 0)}")


@cli.command()
@click.pass_context
def seed(ctx):
    """Seed database with initial data."""
    db_path = ctx.obj["db_path"]

    console.print("[blue]Seeding database with initial data...[/blue]")

    try:
        from execution.data.seed import seed_database

        db = Database(db_path)
        result = seed_database(db)

        console.print(f"[green]Seeding complete![/green]")
        console.print(f"  Categories: {result.get('categories', 0)}")
        console.print(f"  Subcategories: {result.get('subcategories', 0)}")
        console.print(f"  Regions: {result.get('regions', 0)}")
        console.print(f"  Teas: {result.get('teas', 0)}")
        console.print(f"  Occasions: {result.get('occasions', 0)}")
        console.print(f"  Teaware: {result.get('teaware', 0)}")

    except ImportError as e:
        console.print(f"[yellow]Seed module not yet implemented: {e}[/yellow]")


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
