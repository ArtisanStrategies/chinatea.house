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
from datetime import datetime, timedelta

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
            raise click.Abort()

        generator.generate_sitemaps()
        generator.generate_robots_txt()
        console.print("  Sitemaps: generated")
        console.print("  Robots: generated")

    except ImportError as e:
        console.print(f"[yellow]Build module not yet implemented: {e}[/yellow]")
        raise click.Abort()


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


@cli.command()
@click.pass_context
def comparisons(ctx):
    """Generate comparison pairs from tea data."""
    db_path = ctx.obj["db_path"]

    if not db_path.exists():
        console.print("[red]Database not found. Run 'init' and seed data first.[/red]")
        raise click.Abort()

    console.print("[blue]Generating comparison pairs...[/blue]")

    try:
        from execution.data.comparisons import generate_comparisons

        count = generate_comparisons(db_path)

        console.print(f"[green]Generated {count} comparison pairs![/green]")

    except Exception as e:
        console.print(f"[red]Error generating comparisons: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option("--research/--no-research", default=True, help="Research new teas")
@click.option("--content/--no-content", default=True, help="Generate content")
@click.option("--build/--no-build", default=True, help="Build site")
@click.option("--publish/--no-publish", default=True, help="Publish pages")
@click.option("--max-teas", default=5, help="Max new teas to research")
@click.option("--max-content", default=10, help="Max content items to generate")
@click.option("--publish-count", default=100, help="Pages to publish")
@click.option("--backend", default="kimi", help="AI backend (anthropic/openrouter/kimi)")
@click.option("--model", default="kimi-k2-0905-preview", help="Model to use")
@click.pass_context
def agent(ctx, research, content, build, publish, max_teas, max_content,
          publish_count, backend, model):
    """Run the autonomous AI agent pipeline."""
    db_path = ctx.obj["db_path"]

    if not db_path.exists():
        console.print("[red]Database not found. Run 'init' and seed data first.[/red]")
        raise click.Abort()

    console.print("[blue]Starting autonomous agent pipeline...[/blue]")
    console.print(f"  Backend: {backend}")
    console.print(f"  Model: {model}")
    console.print(f"  Research: {research} (max {max_teas} teas)")
    console.print(f"  Content: {content} (max {max_content} items)")
    console.print(f"  Build: {build}")
    console.print(f"  Publish: {publish} ({publish_count} pages)")

    try:
        from execution.agent import AutonomousOrchestrator

        orchestrator = AutonomousOrchestrator(
            db_path=db_path,
            output_path=DEFAULT_OUTPUT_PATH,
            backend=backend,
            model=model
        )

        result = orchestrator.run_full_pipeline(
            research_new_teas=research,
            generate_content=content,
            max_new_teas=max_teas,
            max_content_items=max_content,
            build_site=build,
            publish=publish,
            publish_count=publish_count
        )

        console.print(f"\n[green]Pipeline complete![/green]")
        console.print(f"  Duration: {(result.completed_at - result.started_at).total_seconds():.1f}s")
        console.print(f"  Teas researched: {result.teas_researched}")
        console.print(f"  Teas added: {result.teas_added}")
        console.print(f"  Content generated: {result.content_generated}")
        console.print(f"  Pages built: {result.pages_built}")
        console.print(f"  Pages published: {result.pages_published}")

        if result.errors:
            console.print(f"\n[yellow]Errors ({len(result.errors)}):[/yellow]")
            for err in result.errors[:10]:
                console.print(f"  - {err}")

    except ImportError as e:
        console.print(f"[red]Agent module not available: {e}[/red]")
        console.print("[dim]Make sure anthropic package is installed: pip install anthropic[/dim]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Agent error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option("--interval", default=24, help="Hours between runs")
@click.option("--backend", default="kimi", help="AI backend (anthropic/openrouter/kimi)")
@click.option("--model", default="kimi-k2-0905-preview", help="Model to use")
@click.pass_context
def daemon(ctx, interval, backend, model):
    """Run the agent as a continuous daemon."""
    db_path = ctx.obj["db_path"]

    if not db_path.exists():
        console.print("[red]Database not found. Run 'init' and seed data first.[/red]")
        raise click.Abort()

    console.print(f"[blue]Starting daemon mode (interval: {interval}h)[/blue]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")

    try:
        from execution.agent import AutonomousOrchestrator

        orchestrator = AutonomousOrchestrator(
            db_path=db_path,
            output_path=DEFAULT_OUTPUT_PATH,
            backend=backend,
            model=model
        )

        orchestrator.run_daemon(interval_hours=interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]Daemon stopped by user[/yellow]")
    except ImportError as e:
        console.print(f"[red]Agent module not available: {e}[/red]")
        raise click.Abort()


@cli.group()
def gsc():
    """Google Search Console integration commands."""
    pass


@gsc.command("verify-config")
@click.option("--config", "config_path", default=None, help="Path to GSC config file")
def gsc_verify_config(config_path):
    """Show the configured GSC verification tag and settings."""
    from execution.monitor.gsc import load_gsc_config, get_verification_meta

    try:
        cfg = load_gsc_config(Path(config_path) if config_path else None)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise click.Abort()

    console.print("[blue]Google Search Console config[/blue]")
    console.print(f"  Site URL: {cfg.site_url}")
    console.print(f"  Credential type: {cfg.credential_type}")
    console.print(f"  Credentials path: {cfg.credentials_path}")
    if cfg.credentials_path:
        exists = "[green]found[/green]" if cfg.credentials_path.exists() else "[red]missing[/red]"
        console.print(f"  Credentials file: {exists}")

    meta = get_verification_meta(cfg)
    if meta:
        console.print(f"\n[green]Verification tag:[/green]")
        console.print(f"  {meta}")
    else:
        console.print("\n[yellow]No verification_code configured.[/yellow]")
        console.print("  Add it to config/gsc.yaml to render the meta tag.")


@gsc.command("test-connection")
@click.option("--config", "config_path", default=None, help="Path to GSC config file")
def gsc_test_connection(config_path):
    """Test connectivity to the GSC API."""
    from execution.monitor.gsc import load_gsc_config, GoogleSearchConsole

    try:
        cfg = load_gsc_config(Path(config_path) if config_path else None)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise click.Abort()

    console.print(f"[blue]Testing GSC API connection for {cfg.site_url}...[/blue]")
    client = GoogleSearchConsole(cfg)
    result = client.test_connection()

    if result.get("success"):
        console.print("[green]Connection successful![/green]")
        console.print(f"  Site: {result.get('site', {})}")
    else:
        console.print("[red]Connection failed:[/red]")
        console.print(f"  {result.get('error', 'Unknown error')}")
        raise click.Abort()


@gsc.command("fetch-performance")
@click.option("--start-date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD)")
@click.option("--dimensions", default="page,query", help="Comma-separated dimensions")
@click.option("--dry-run", is_flag=True, help="Fetch but do not store")
@click.option("--config", "config_path", default=None, help="Path to GSC config file")
@click.pass_context
def gsc_fetch_performance(ctx, start_date, end_date, dimensions, dry_run, config_path):
    """Fetch search analytics from GSC and store snapshots."""
    from execution.monitor.gsc import (
        load_gsc_config, GoogleSearchConsole, summarize_performance
    )

    db_path = ctx.obj["db_path"]
    if not db_path.exists():
        console.print("[red]Database not found. Run 'init' first.[/red]")
        raise click.Abort()

    try:
        cfg = load_gsc_config(Path(config_path) if config_path else None)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise click.Abort()

    dims = [d.strip() for d in dimensions.split(",") if d.strip()]

    # Mirror the client's default date range so we can tag summary rows.
    effective_end = end_date or (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    effective_start = start_date or (
        datetime.strptime(effective_end, "%Y-%m-%d")
        - timedelta(days=cfg.default_days)
    ).strftime("%Y-%m-%d")

    console.print(f"[blue]Fetching GSC performance data[/blue]")
    console.print(f"  Site: {cfg.site_url}")
    console.print(f"  Dimensions: {', '.join(dims)}")
    console.print(f"  Start: {effective_start}")
    console.print(f"  End: {effective_end}")

    try:
        client = GoogleSearchConsole(cfg)
        rows = client.fetch_all_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=dims,
        )
    except Exception as e:
        console.print(f"[red]Failed to fetch GSC data: {e}[/red]")
        raise click.Abort()

    summary = summarize_performance(rows)
    console.print(f"\n[green]Fetched {len(rows)} rows[/green]")
    console.print(f"  Clicks: {summary['total_clicks']}")
    console.print(f"  Impressions: {summary['total_impressions']}")
    console.print(f"  Avg CTR: {summary['avg_ctr']:.2%}")
    console.print(f"  Avg position: {summary['avg_position']}")

    if dry_run:
        console.print("\n[yellow]Dry run - not storing snapshots.[/yellow]")
        return

    db = Database(db_path)
    snapshots = [row.to_dict() for row in rows]
    default_date = effective_end if "date" not in dims else None
    inserted = db.insert_performance_snapshots(snapshots, default_snapshot_date=default_date)
    console.print(f"\n[green]Stored {inserted} snapshots in database.[/green]")


@gsc.command("submit-sitemap")
@click.option("--sitemap-url", default="https://chinatea.house/sitemap.xml", help="Sitemap URL")
@click.option("--config", "config_path", default=None, help="Path to GSC config file")
def gsc_submit_sitemap(sitemap_url, config_path):
    """Submit a sitemap URL to Google Search Console."""
    from execution.monitor.gsc import load_gsc_config, GoogleSearchConsole

    try:
        cfg = load_gsc_config(Path(config_path) if config_path else None)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise click.Abort()

    client = GoogleSearchConsole(cfg)
    result = client.submit_sitemap(sitemap_url)

    if result.get("success"):
        console.print(f"[green]Submitted sitemap:[/green] {sitemap_url}")
    else:
        console.print(f"[red]Sitemap submission failed:[/red]")
        console.print(f"  {result.get('error', 'Unknown error')}")
        raise click.Abort()


@gsc.command("underperforming")
@click.option("--min-impressions", default=100, help="Minimum impressions threshold")
@click.option("--max-ctr", default=0.02, help="Maximum CTR threshold")
@click.option("--start-date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD)")
@click.option("--limit", default=50, help="Number of results")
@click.pass_context
def gsc_underperforming(ctx, min_impressions, max_ctr, start_date, end_date, limit):
    """List pages with high impressions but low CTR."""
    db_path = ctx.obj["db_path"]
    if not db_path.exists():
        console.print("[red]Database not found.[/red]")
        raise click.Abort()

    db = Database(db_path)
    pages = db.get_underperforming_pages(
        min_impressions=min_impressions,
        max_ctr=max_ctr,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    if not pages:
        console.print("[green]No underperforming pages found.[/green]")
        return

    table = Table(title="Underperforming Pages (CTR Rewrite Candidates)")
    table.add_column("URL", style="cyan")
    table.add_column("Clicks", justify="right")
    table.add_column("Impressions", justify="right")
    table.add_column("CTR", justify="right")
    table.add_column("Position", justify="right")

    for p in pages:
        table.add_row(
            p["url"],
            str(p["clicks"]),
            str(p["impressions"]),
            f"{p['ctr']:.2%}",
            f"{p['avg_position']:.1f}",
        )

    console.print(table)


@cli.command()
@click.pass_context
def gaps(ctx):
    """Show content gaps in the database."""
    db_path = ctx.obj["db_path"]

    if not db_path.exists():
        console.print("[red]Database not found.[/red]")
        raise click.Abort()

    console.print("[blue]Analyzing content gaps...[/blue]")

    try:
        from execution.agent.content import ContentGenerationAgent

        agent = ContentGenerationAgent.__new__(ContentGenerationAgent)
        gaps_data = agent.identify_content_gaps(db_path)

        console.print(f"\n[cyan]Categories without pillar content:[/cyan]")
        for p in gaps_data["pillars_without_content"]:
            console.print(f"  - {p['name']}")

        console.print(f"\n[cyan]Top comparisons without narrative ({len(gaps_data['comparisons_without_narrative'])}):[/cyan]")
        for c in gaps_data["comparisons_without_narrative"][:10]:
            console.print(f"  - {c['tea_a']} vs {c['tea_b']} (score: {c['score']:.2f})")

        console.print(f"\n[cyan]Teas with short descriptions ({len(gaps_data['teas_with_short_descriptions'])}):[/cyan]")
        for t in gaps_data["teas_with_short_descriptions"][:10]:
            console.print(f"  - {t['name']} ({t['current_length']} chars)")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.group()
def indexnow():
    """IndexNow fast-indexing commands."""
    pass


@indexnow.command("generate-key")
@click.option("--output", default="config/indexnow.key", help="Path to save the key")
def indexnow_generate_key(output):
    """Generate and save an IndexNow API key."""
    from execution.monitor.indexnow import generate_key

    key = generate_key()
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(key, encoding="utf-8")
    console.print(f"[green]IndexNow key generated and saved to {output_path}[/green]")
    console.print(f"  Key: {key}")
    console.print("\n[yellow]Important:[/yellow] expose this key at https://chinatea.house/{key}.txt")


@indexnow.command("write-verification")
@click.option("--output", default=str(DEFAULT_OUTPUT_PATH), help="Site output directory")
def indexnow_write_verification(output):
    """Write the IndexNow verification file to the output directory."""
    from execution.monitor.indexnow import get_key, write_key_file

    key = get_key()
    if not key:
        console.print("[red]No IndexNow key found. Run 'indexnow generate-key' first.[/red]")
        raise click.Abort()

    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    verification_path = write_key_file(key, output_path)
    console.print(f"[green]Verification file written:[/green] {verification_path}")


@indexnow.command("ping")
@click.argument("urls", nargs=-1, required=True)
@click.option("--host", default=None, help="Site host (e.g., chinatea.house)")
@click.option("--key", default=None, help="IndexNow key (or set INDEXNOW_KEY)")
def indexnow_ping(urls, host, key):
    """Ping IndexNow with one or more URLs."""
    from execution.monitor.indexnow import ping

    try:
        result = ping(list(urls), key=key, host=host)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise click.Abort()

    if result.get("success"):
        console.print(f"[green]IndexNow ping accepted for {result['urls_submitted']} URLs[/green]")
    else:
        console.print("[red]IndexNow ping failed or was rejected[/red]")

    for r in result.get("results", []):
        status = r.get("status_code")
        ok = "[green]OK[/green]" if r.get("ok") else "[red]FAIL[/red]"
        console.print(f"  {r['endpoint']}: {status} {ok}")
        if r.get("response"):
            console.print(f"    {r['response'][:200]}")


@cli.command()
@click.option("--prod", is_flag=True, help="Deploy to production (vs preview)")
@click.option("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output directory to deploy")
@click.pass_context
def deploy(ctx, prod, output):
    """Deploy site to Cloudflare Pages."""
    output_path = Path(output)

    if not output_path.exists():
        console.print(f"[red]Output directory not found: {output_path}[/red]")
        console.print("[dim]Run 'build' first to generate the site.[/dim]")
        raise click.Abort()

    console.print(f"[blue]Deploying to Cloudflare Pages...[/blue]")
    console.print(f"  Environment: {'Production' if prod else 'Preview'}")
    console.print(f"  Source: {output_path}")

    try:
        from execution.deploy.cloudflare import CloudflareDeployer

        deployer = CloudflareDeployer(output_path)

        if not deployer.check_wrangler():
            console.print("[red]Wrangler CLI not installed.[/red]")
            console.print("[dim]Install with: npm install -g wrangler[/dim]")
            console.print("[dim]Then login with: wrangler login[/dim]")
            raise click.Abort()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Deploying...", total=None)

            if prod:
                result = deployer.publish()
            else:
                result = deployer.preview()

            progress.update(task, completed=True)

        if result.get("success"):
            console.print(f"\n[green]Deployment successful![/green]")
            if result.get("url"):
                console.print(f"  URL: {result['url']}")
        else:
            console.print(f"\n[red]Deployment failed:[/red]")
            console.print(f"  {result.get('error', 'Unknown error')}")
            raise click.Abort()

    except ImportError as e:
        console.print(f"[red]Deploy module error: {e}[/red]")
        raise click.Abort()


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
