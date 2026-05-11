"""
Autonomous pipeline orchestrator.

Coordinates all AI agents and the build/publish pipeline
for fully autonomous operation.
"""

import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .research import TeaResearchAgent
from .content import ContentGenerationAgent


@dataclass
class PipelineResult:
    """Result of a pipeline run."""
    started_at: datetime
    completed_at: Optional[datetime] = None
    teas_researched: int = 0
    teas_added: int = 0
    content_generated: int = 0
    comparisons_generated: int = 0
    pages_built: int = 0
    pages_published: int = 0
    errors: list = field(default_factory=list)


class AutonomousOrchestrator:
    """
    Main orchestrator for autonomous site operation.

    Coordinates:
    1. Tea research and data expansion
    2. Content generation for pillars and comparisons
    3. Comparison pair generation
    4. Site build
    5. Drip publishing

    Can run as a daemon or single execution.
    """

    def __init__(
        self,
        db_path: Path,
        output_path: Path,
        backend: str = "anthropic",
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None
    ):
        self.db_path = db_path
        self.output_path = output_path

        # Initialize agents
        self.research_agent = TeaResearchAgent(
            backend=backend,
            model=model,
            api_key=api_key
        )
        self.content_agent = ContentGenerationAgent(
            backend=backend,
            model=model,
            api_key=api_key
        )

    def run_full_pipeline(
        self,
        research_new_teas: bool = True,
        generate_content: bool = True,
        max_new_teas: int = 5,
        max_content_items: int = 10,
        build_site: bool = True,
        publish: bool = True,
        publish_count: int = 100
    ) -> PipelineResult:
        """
        Run the complete autonomous pipeline.

        Args:
            research_new_teas: Whether to research and add new teas
            generate_content: Whether to generate pillar/comparison content
            max_new_teas: Maximum new teas to research per run
            max_content_items: Maximum content items to generate per run
            build_site: Whether to rebuild the site
            publish: Whether to run drip publishing
            publish_count: Number of pages to publish

        Returns:
            PipelineResult with statistics
        """
        result = PipelineResult(started_at=datetime.now())

        try:
            # Step 1: Research new teas
            if research_new_teas:
                print("\n=== Phase 1: Tea Research ===")
                self._research_teas(result, max_new_teas)

            # Step 2: Generate comparison pairs
            print("\n=== Phase 2: Comparison Generation ===")
            self._generate_comparisons(result)

            # Step 3: Generate content
            if generate_content:
                print("\n=== Phase 3: Content Generation ===")
                self._generate_content(result, max_content_items)

            # Step 4: Build site
            if build_site:
                print("\n=== Phase 4: Site Build ===")
                self._build_site(result)

            # Step 5: Publish
            if publish:
                print("\n=== Phase 5: Publishing ===")
                self._publish_pages(result, publish_count)

        except Exception as e:
            result.errors.append(f"Pipeline error: {str(e)}")

        result.completed_at = datetime.now()
        return result

    def _research_teas(self, result: PipelineResult, max_teas: int):
        """Research and add new teas."""
        try:
            # Find missing teas
            missing = self.research_agent.identify_missing_teas(self.db_path)
            print(f"Found {len(missing)} potentially missing teas")

            if not missing:
                print("No missing teas found")
                return

            # Research up to max_teas
            results = self.research_agent.batch_research(
                missing[:max_teas],
                max_teas=max_teas,
                delay_seconds=2.0  # Rate limiting
            )

            result.teas_researched = len(results)

            # Add to database
            for res in results:
                if res.confidence > 0.5 and "error" not in res.tea_data:
                    try:
                        self._insert_researched_tea(res.tea_data)
                        result.teas_added += 1
                        print(f"  Added: {res.tea_data.get('name_en', res.tea_id)}")
                    except Exception as e:
                        result.errors.append(f"Failed to add {res.tea_id}: {e}")

        except Exception as e:
            result.errors.append(f"Research error: {str(e)}")

    def _generate_comparisons(self, result: PipelineResult):
        """Generate comparison pairs."""
        try:
            from ..data.comparisons import generate_comparisons
            count = generate_comparisons(self.db_path)
            result.comparisons_generated = count
            print(f"Generated {count} comparison pairs")
        except Exception as e:
            result.errors.append(f"Comparison generation error: {str(e)}")

    def _generate_content(self, result: PipelineResult, max_items: int):
        """Generate pillar and comparison content."""
        try:
            gaps = self.content_agent.identify_content_gaps(self.db_path)

            items_generated = 0

            # Generate pillar content
            for pillar in gaps["pillars_without_content"][:3]:
                if items_generated >= max_items:
                    break
                print(f"  Generating pillar content for: {pillar['name']}")
                content = self.content_agent.generate_pillar_content(pillar['name'])
                if "error" not in content.sections:
                    self._save_pillar_content(pillar['id'], content)
                    items_generated += 1
                time.sleep(2)  # Rate limiting

            # Generate comparison narratives for top pairs
            for comp in gaps["comparisons_without_narrative"][:max_items - items_generated]:
                if items_generated >= max_items:
                    break
                print(f"  Generating comparison: {comp['tea_a']} vs {comp['tea_b']}")
                # Get tea data
                tea_a = self._get_tea(comp['tea_a'])
                tea_b = self._get_tea(comp['tea_b'])
                if tea_a and tea_b:
                    content = self.content_agent.generate_comparison_content(tea_a, tea_b)
                    if "error" not in content.sections:
                        self._save_comparison_content(comp['id'], content)
                        items_generated += 1
                time.sleep(2)

            result.content_generated = items_generated

        except Exception as e:
            result.errors.append(f"Content generation error: {str(e)}")

    def _build_site(self, result: PipelineResult):
        """Build the static site."""
        try:
            from ..data.db import Database
            from ..build.generator import SiteGenerator

            db = Database(self.db_path)
            generator = SiteGenerator(db, self.output_path)
            build_result = generator.build(incremental=True)

            result.pages_built = build_result.get('pages_generated', 0)
            print(f"Built {result.pages_built} pages")

        except Exception as e:
            result.errors.append(f"Build error: {str(e)}")

    def _publish_pages(self, result: PipelineResult, count: int):
        """Publish pages via drip schedule."""
        try:
            from ..data.db import Database
            from ..publish.drip import DripPublisher

            db = Database(self.db_path)
            publisher = DripPublisher(db)

            pages = publisher.get_next_batch(count)
            if pages:
                publish_result = publisher.publish(pages)
                result.pages_published = publish_result.get('published', 0)
                print(f"Published {result.pages_published} pages")
            else:
                print("No pages ready to publish")

        except Exception as e:
            result.errors.append(f"Publish error: {str(e)}")

    def _insert_researched_tea(self, tea_data: dict):
        """Insert a researched tea into the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Extract fields
            fields = [
                'id', 'name_en', 'name_zh', 'name_pinyin',
                'category_id', 'subcategory_id', 'region_id',
                'oxidation_level', 'roast_level', 'harvest_season', 'cultivar',
                'caffeine_level', 'body', 'finish', 'mouthfeel',
                'description_brief', 'tier', 'history', 'is_aged', 'age_years'
            ]

            # JSON fields (similar_tea_ids handled via tea_similar table, not here)
            json_fields = ['flavor_primary', 'flavor_secondary', 'aroma',
                          'brewing_gongfu', 'brewing_western',
                          'price_budget', 'price_mid', 'price_premium',
                          'best_for']

            values = {}
            for f in fields:
                if f in tea_data:
                    values[f] = tea_data[f]

            for f in json_fields:
                if f in tea_data:
                    values[f] = json.dumps(tea_data[f])

            columns = list(values.keys())
            placeholders = ['?' for _ in columns]

            sql = f"""
                INSERT INTO teas ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """

            conn.execute(sql, list(values.values()))
            conn.commit()

        finally:
            conn.close()

    def _save_pillar_content(self, category_id: str, content):
        """Save generated pillar content to database."""
        conn = sqlite3.connect(self.db_path)
        try:
            for section_name, section_content in content.sections.items():
                conn.execute("""
                    INSERT OR REPLACE INTO pillar_content
                    (page_type, entity_id, section, content, word_count, generated_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    'category',
                    category_id,
                    section_name,
                    section_content,
                    len(section_content.split())
                ))
            conn.commit()
        finally:
            conn.close()

    def _save_comparison_content(self, comparison_id: str, content):
        """Save generated comparison content to database."""
        conn = sqlite3.connect(self.db_path)
        try:
            sections = content.sections
            conn.execute("""
                INSERT OR REPLACE INTO comparison_content
                (comparison_id, intro, flavor_comparison, brewing_comparison,
                 price_comparison, verdict, word_count, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                comparison_id,
                sections.get('intro', ''),
                sections.get('flavor_comparison', ''),
                sections.get('brewing_comparison', ''),
                sections.get('price_comparison', ''),
                sections.get('verdict', ''),
                content.word_count
            ))
            conn.commit()
        finally:
            conn.close()

    def _get_tea(self, name: str) -> Optional[dict]:
        """Get tea data by name."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM teas WHERE name_en = ? OR id = ?",
                (name, name.lower().replace(" ", "-"))
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def run_daemon(
        self,
        interval_hours: float = 24,
        research_new_teas: bool = True,
        generate_content: bool = True
    ):
        """
        Run as a daemon, executing the pipeline periodically.

        Args:
            interval_hours: Hours between runs
            research_new_teas: Whether to research new teas each run
            generate_content: Whether to generate content each run
        """
        print(f"Starting autonomous daemon (interval: {interval_hours}h)")

        while True:
            print(f"\n{'='*60}")
            print(f"Pipeline run started at {datetime.now().isoformat()}")
            print(f"{'='*60}")

            result = self.run_full_pipeline(
                research_new_teas=research_new_teas,
                generate_content=generate_content
            )

            # Print summary
            duration = (result.completed_at - result.started_at).total_seconds()
            print(f"\n{'='*60}")
            print("Pipeline Summary:")
            print(f"  Duration: {duration:.1f}s")
            print(f"  Teas researched: {result.teas_researched}")
            print(f"  Teas added: {result.teas_added}")
            print(f"  Content generated: {result.content_generated}")
            print(f"  Pages built: {result.pages_built}")
            print(f"  Pages published: {result.pages_published}")
            if result.errors:
                print(f"  Errors: {len(result.errors)}")
                for err in result.errors[:5]:
                    print(f"    - {err}")
            print(f"{'='*60}")

            # Sleep until next run
            print(f"\nSleeping for {interval_hours} hours...")
            time.sleep(interval_hours * 3600)
