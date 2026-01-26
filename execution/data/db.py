"""
SQLite database operations for chinatea.house.

Provides CRUD operations and queries for all tea-related data.
"""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, TypeVar, Type

from .models import (
    Tea, Category, Subcategory, Region, Teaware, Occasion,
    BrewingMethod, ComparisonPair, PageManifest, BrewingParams, PriceRange
)

T = TypeVar('T')


class Database:
    """SQLite database manager for tea data."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database with schema."""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path) as f:
            schema = f.read()
        with self.connection() as conn:
            conn.executescript(schema)

    @contextmanager
    def connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # =========================================================================
    # CATEGORY OPERATIONS
    # =========================================================================

    def insert_category(self, category: Category) -> None:
        """Insert a new category."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO categories (id, name_en, name_zh, description,
                    oxidation_range_min, oxidation_range_max, color_hex)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                category.id, category.name_en, category.name_zh,
                category.description, category.oxidation_range_min,
                category.oxidation_range_max, category.color_hex
            ))

    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a category by ID."""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            if row:
                return Category(
                    id=row["id"],
                    name_en=row["name_en"],
                    name_zh=row["name_zh"],
                    description=row["description"],
                    oxidation_range_min=row["oxidation_range_min"],
                    oxidation_range_max=row["oxidation_range_max"],
                    color_hex=row["color_hex"]
                )
            return None

    def get_all_categories(self) -> list[Category]:
        """Get all categories."""
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
            return [
                Category(
                    id=row["id"],
                    name_en=row["name_en"],
                    name_zh=row["name_zh"],
                    description=row["description"],
                    oxidation_range_min=row["oxidation_range_min"],
                    oxidation_range_max=row["oxidation_range_max"],
                    color_hex=row["color_hex"]
                )
                for row in rows
            ]

    # =========================================================================
    # SUBCATEGORY OPERATIONS
    # =========================================================================

    def insert_subcategory(self, subcategory: Subcategory) -> None:
        """Insert a new subcategory."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO subcategories (id, category_id, name_en, name_zh, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                subcategory.id, subcategory.category_id, subcategory.name_en,
                subcategory.name_zh, subcategory.description
            ))

    def get_subcategories_by_category(self, category_id: str) -> list[Subcategory]:
        """Get all subcategories for a category."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM subcategories WHERE category_id = ? ORDER BY name_en",
                (category_id,)
            ).fetchall()
            return [
                Subcategory(
                    id=row["id"],
                    category_id=row["category_id"],
                    name_en=row["name_en"],
                    name_zh=row["name_zh"],
                    description=row["description"]
                )
                for row in rows
            ]

    # =========================================================================
    # REGION OPERATIONS
    # =========================================================================

    def insert_region(self, region: Region) -> None:
        """Insert a new region."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO regions (id, parent_id, name_en, name_zh, name_pinyin,
                    region_type, latitude, longitude, elevation_min_m, elevation_max_m,
                    climate, soil_type, terroir_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                region.id, region.parent_id, region.name_en, region.name_zh,
                region.name_pinyin, region.region_type.value, region.latitude,
                region.longitude, region.elevation_min_m, region.elevation_max_m,
                region.climate, region.soil_type, region.terroir_notes
            ))

    def get_region(self, region_id: str) -> Optional[Region]:
        """Get a region by ID."""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM regions WHERE id = ?", (region_id,)
            ).fetchone()
            if row:
                return self._row_to_region(row)
            return None

    def get_regions_by_type(self, region_type: str) -> list[Region]:
        """Get all regions of a specific type."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM regions WHERE region_type = ? ORDER BY name_en",
                (region_type,)
            ).fetchall()
            return [self._row_to_region(row) for row in rows]

    def get_child_regions(self, parent_id: str) -> list[Region]:
        """Get all child regions of a parent."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM regions WHERE parent_id = ? ORDER BY name_en",
                (parent_id,)
            ).fetchall()
            return [self._row_to_region(row) for row in rows]

    def get_all_regions(self) -> list[Region]:
        """Get all regions."""
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM regions ORDER BY name_en").fetchall()
            return [self._row_to_region(row) for row in rows]

    def _row_to_region(self, row: sqlite3.Row) -> Region:
        """Convert database row to Region model."""
        from .models import RegionType
        return Region(
            id=row["id"],
            parent_id=row["parent_id"],
            name_en=row["name_en"],
            name_zh=row["name_zh"],
            name_pinyin=row["name_pinyin"],
            region_type=RegionType(row["region_type"]),
            latitude=row["latitude"],
            longitude=row["longitude"],
            elevation_min_m=row["elevation_min_m"],
            elevation_max_m=row["elevation_max_m"],
            climate=row["climate"],
            soil_type=row["soil_type"],
            terroir_notes=row["terroir_notes"]
        )

    # =========================================================================
    # TEA OPERATIONS
    # =========================================================================

    def insert_tea(self, tea: Tea) -> None:
        """Insert a new tea."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO teas (
                    id, name_en, name_zh, name_pinyin, category_id, subcategory_id,
                    region_id, oxidation_level, roast_level, is_aged, age_years,
                    harvest_season, cultivar, caffeine_level, flavor_primary,
                    flavor_secondary, aroma, body, finish, mouthfeel,
                    brewing_gongfu, brewing_western, brewing_grandpa, brewing_cold,
                    price_budget, price_mid, price_premium, best_for,
                    description_brief, description_full, history, tier, sources
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tea.id, tea.name_en, tea.name_zh, tea.name_pinyin,
                tea.category_id, tea.subcategory_id, tea.region_id,
                tea.oxidation_level,
                tea.roast_level.value if tea.roast_level else None,
                1 if tea.is_aged else 0, tea.age_years,
                tea.harvest_season, tea.cultivar,
                tea.caffeine_level.value if tea.caffeine_level else None,
                json.dumps(tea.flavor_primary),
                json.dumps(tea.flavor_secondary),
                json.dumps(tea.aroma),
                tea.body.value if tea.body else None,
                tea.finish, tea.mouthfeel,
                self._brewing_to_json(tea.brewing_gongfu),
                self._brewing_to_json(tea.brewing_western),
                self._brewing_to_json(tea.brewing_grandpa),
                self._brewing_to_json(tea.brewing_cold),
                self._price_to_json(tea.price_budget),
                self._price_to_json(tea.price_mid),
                self._price_to_json(tea.price_premium),
                json.dumps(tea.best_for),
                tea.description_brief, tea.description_full, tea.history,
                tea.tier, json.dumps(tea.sources)
            ))

            # Insert alternate regions
            for alt_region_id in tea.alternate_region_ids:
                conn.execute("""
                    INSERT OR IGNORE INTO tea_alternate_regions (tea_id, region_id)
                    VALUES (?, ?)
                """, (tea.id, alt_region_id))

            # Note: Similar tea relationships are deferred until all teas exist
            # Use link_similar_teas() after all teas are inserted

    def link_similar_teas(self, tea_id: str, similar_ids: list[str]) -> None:
        """Link similar teas after all teas exist in database."""
        with self.connection() as conn:
            for similar_id in similar_ids:
                # Only insert if similar tea exists
                exists = conn.execute(
                    "SELECT 1 FROM teas WHERE id = ?", (similar_id,)
                ).fetchone()
                if exists:
                    conn.execute("""
                        INSERT OR IGNORE INTO tea_similar (tea_id, similar_tea_id, similarity_score)
                        VALUES (?, ?, 0.7)
                    """, (tea_id, similar_id))

    def get_tea(self, tea_id: str) -> Optional[Tea]:
        """Get a tea by ID."""
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM teas WHERE id = ?", (tea_id,)).fetchone()
            if row:
                return self._row_to_tea(conn, row)
            return None

    def get_teas_by_category(self, category_id: str) -> list[Tea]:
        """Get all teas in a category."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM teas WHERE category_id = ? ORDER BY tier, name_en",
                (category_id,)
            ).fetchall()
            return [self._row_to_tea(conn, row) for row in rows]

    def get_teas_by_region(self, region_id: str) -> list[Tea]:
        """Get all teas from a region."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM teas WHERE region_id = ? ORDER BY tier, name_en",
                (region_id,)
            ).fetchall()
            return [self._row_to_tea(conn, row) for row in rows]

    def get_all_teas(self, tier: Optional[int] = None) -> list[Tea]:
        """Get all teas, optionally filtered by tier."""
        with self.connection() as conn:
            if tier:
                rows = conn.execute(
                    "SELECT * FROM teas WHERE tier = ? ORDER BY name_en", (tier,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM teas ORDER BY tier, name_en").fetchall()
            return [self._row_to_tea(conn, row) for row in rows]

    def get_similar_teas(self, tea_id: str, limit: int = 5) -> list[Tea]:
        """Get similar teas for a given tea."""
        with self.connection() as conn:
            rows = conn.execute("""
                SELECT t.* FROM teas t
                JOIN tea_similar ts ON t.id = ts.similar_tea_id
                WHERE ts.tea_id = ?
                ORDER BY ts.similarity_score DESC
                LIMIT ?
            """, (tea_id, limit)).fetchall()
            return [self._row_to_tea(conn, row) for row in rows]

    def search_teas(self, query: str, limit: int = 20) -> list[Tea]:
        """Search teas by name."""
        with self.connection() as conn:
            pattern = f"%{query}%"
            rows = conn.execute("""
                SELECT * FROM teas
                WHERE name_en LIKE ? OR name_zh LIKE ? OR name_pinyin LIKE ?
                ORDER BY tier, name_en
                LIMIT ?
            """, (pattern, pattern, pattern, limit)).fetchall()
            return [self._row_to_tea(conn, row) for row in rows]

    def _row_to_tea(self, conn: sqlite3.Connection, row: sqlite3.Row) -> Tea:
        """Convert database row to Tea model."""
        from .models import RoastLevel, CaffeineLevel, BodyLevel

        # Get alternate regions
        alt_rows = conn.execute(
            "SELECT region_id FROM tea_alternate_regions WHERE tea_id = ?",
            (row["id"],)
        ).fetchall()
        alternate_region_ids = [r["region_id"] for r in alt_rows]

        # Get similar teas
        sim_rows = conn.execute(
            "SELECT similar_tea_id FROM tea_similar WHERE tea_id = ?",
            (row["id"],)
        ).fetchall()
        similar_tea_ids = [r["similar_tea_id"] for r in sim_rows]

        return Tea(
            id=row["id"],
            name_en=row["name_en"],
            name_zh=row["name_zh"],
            name_pinyin=row["name_pinyin"],
            category_id=row["category_id"],
            subcategory_id=row["subcategory_id"],
            region_id=row["region_id"],
            alternate_region_ids=alternate_region_ids,
            oxidation_level=row["oxidation_level"],
            roast_level=RoastLevel(row["roast_level"]) if row["roast_level"] else None,
            is_aged=bool(row["is_aged"]),
            age_years=row["age_years"],
            harvest_season=row["harvest_season"],
            cultivar=row["cultivar"],
            caffeine_level=CaffeineLevel(row["caffeine_level"]) if row["caffeine_level"] else None,
            flavor_primary=json.loads(row["flavor_primary"]) if row["flavor_primary"] else [],
            flavor_secondary=json.loads(row["flavor_secondary"]) if row["flavor_secondary"] else [],
            aroma=json.loads(row["aroma"]) if row["aroma"] else [],
            body=BodyLevel(row["body"]) if row["body"] else None,
            finish=row["finish"],
            mouthfeel=row["mouthfeel"],
            brewing_gongfu=self._json_to_brewing(row["brewing_gongfu"]),
            brewing_western=self._json_to_brewing(row["brewing_western"]),
            brewing_grandpa=self._json_to_brewing(row["brewing_grandpa"]),
            brewing_cold=self._json_to_brewing(row["brewing_cold"]),
            price_budget=self._json_to_price(row["price_budget"]),
            price_mid=self._json_to_price(row["price_mid"]),
            price_premium=self._json_to_price(row["price_premium"]),
            best_for=json.loads(row["best_for"]) if row["best_for"] else [],
            similar_tea_ids=similar_tea_ids,
            description_brief=row["description_brief"],
            description_full=row["description_full"],
            history=row["history"],
            tier=row["tier"],
            sources=json.loads(row["sources"]) if row["sources"] else []
        )

    def _brewing_to_json(self, params: Optional[BrewingParams]) -> Optional[str]:
        """Convert BrewingParams to JSON string."""
        if params is None:
            return None
        return json.dumps(params.model_dump())

    def _json_to_brewing(self, json_str: Optional[str]) -> Optional[BrewingParams]:
        """Convert JSON string to BrewingParams."""
        if json_str is None:
            return None
        return BrewingParams(**json.loads(json_str))

    def _price_to_json(self, price: Optional[PriceRange]) -> Optional[str]:
        """Convert PriceRange to JSON string."""
        if price is None:
            return None
        return json.dumps(price.model_dump())

    def _json_to_price(self, json_str: Optional[str]) -> Optional[PriceRange]:
        """Convert JSON string to PriceRange."""
        if json_str is None:
            return None
        return PriceRange(**json.loads(json_str))

    # =========================================================================
    # TEAWARE OPERATIONS
    # =========================================================================

    def insert_teaware(self, teaware: Teaware) -> None:
        """Insert a new teaware item."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO teaware (id, name_en, name_zh, teaware_type, materials,
                    origin_region_id, price_range, description, best_for_categories,
                    care_instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                teaware.id, teaware.name_en, teaware.name_zh,
                teaware.teaware_type.value, json.dumps(teaware.materials),
                teaware.origin_region_id, self._price_to_json(teaware.price_range),
                teaware.description, json.dumps(teaware.best_for_categories),
                teaware.care_instructions
            ))

    def get_all_teaware(self) -> list[Teaware]:
        """Get all teaware items."""
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM teaware ORDER BY teaware_type, name_en").fetchall()
            return [self._row_to_teaware(row) for row in rows]

    def _row_to_teaware(self, row: sqlite3.Row) -> Teaware:
        """Convert database row to Teaware model."""
        from .models import TeawareType
        return Teaware(
            id=row["id"],
            name_en=row["name_en"],
            name_zh=row["name_zh"],
            teaware_type=TeawareType(row["teaware_type"]),
            materials=json.loads(row["materials"]) if row["materials"] else [],
            origin_region_id=row["origin_region_id"],
            price_range=self._json_to_price(row["price_range"]),
            description=row["description"],
            best_for_categories=json.loads(row["best_for_categories"]) if row["best_for_categories"] else [],
            care_instructions=row["care_instructions"]
        )

    # =========================================================================
    # OCCASION OPERATIONS
    # =========================================================================

    def insert_occasion(self, occasion: Occasion) -> None:
        """Insert a new occasion."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO occasions (id, name, description, preferred_categories,
                    preferred_attributes, time_of_day, season)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                occasion.id, occasion.name, occasion.description,
                json.dumps(occasion.preferred_categories),
                json.dumps(occasion.preferred_attributes),
                occasion.time_of_day, occasion.season
            ))

    def get_all_occasions(self) -> list[Occasion]:
        """Get all occasions."""
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM occasions ORDER BY name").fetchall()
            return [
                Occasion(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    preferred_categories=json.loads(row["preferred_categories"]) if row["preferred_categories"] else [],
                    preferred_attributes=json.loads(row["preferred_attributes"]) if row["preferred_attributes"] else {},
                    time_of_day=row["time_of_day"],
                    season=row["season"]
                )
                for row in rows
            ]

    # =========================================================================
    # COMPARISON OPERATIONS
    # =========================================================================

    def insert_comparison(self, comparison: ComparisonPair) -> None:
        """Insert a comparison pair."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO comparison_pairs (id, tea_a_id, tea_b_id, comparison_type,
                    is_valid, narrative, key_differences, key_similarities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comparison.id, comparison.tea_a_id, comparison.tea_b_id,
                comparison.comparison_type, 1 if comparison.is_valid else 0,
                comparison.narrative, json.dumps(comparison.key_differences),
                json.dumps(comparison.key_similarities)
            ))

    def get_comparisons_for_tea(self, tea_id: str) -> list[ComparisonPair]:
        """Get all comparisons involving a specific tea."""
        with self.connection() as conn:
            rows = conn.execute("""
                SELECT * FROM comparison_pairs
                WHERE tea_a_id = ? OR tea_b_id = ?
                ORDER BY id
            """, (tea_id, tea_id)).fetchall()
            return [self._row_to_comparison(row) for row in rows]

    def get_all_comparisons(self, valid_only: bool = True) -> list[ComparisonPair]:
        """Get all comparison pairs."""
        with self.connection() as conn:
            if valid_only:
                rows = conn.execute(
                    "SELECT * FROM comparison_pairs WHERE is_valid = 1 ORDER BY id"
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM comparison_pairs ORDER BY id").fetchall()
            return [self._row_to_comparison(row) for row in rows]

    def _row_to_comparison(self, row: sqlite3.Row) -> ComparisonPair:
        """Convert database row to ComparisonPair model."""
        return ComparisonPair(
            id=row["id"],
            tea_a_id=row["tea_a_id"],
            tea_b_id=row["tea_b_id"],
            comparison_type=row["comparison_type"],
            is_valid=bool(row["is_valid"]),
            narrative=row["narrative"],
            key_differences=json.loads(row["key_differences"]) if row["key_differences"] else [],
            key_similarities=json.loads(row["key_similarities"]) if row["key_similarities"] else []
        )

    # =========================================================================
    # PAGE MANIFEST OPERATIONS
    # =========================================================================

    def upsert_page_manifest(self, manifest: PageManifest) -> None:
        """Insert or update a page manifest entry."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO page_manifest (url, template, data_hash, template_hash,
                    status, generated_at, published_at, word_count, internal_links_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    template = excluded.template,
                    data_hash = excluded.data_hash,
                    template_hash = excluded.template_hash,
                    status = excluded.status,
                    generated_at = excluded.generated_at,
                    published_at = excluded.published_at,
                    word_count = excluded.word_count,
                    internal_links_count = excluded.internal_links_count
            """, (
                manifest.url, manifest.template, manifest.data_hash,
                manifest.template_hash, manifest.status, manifest.generated_at,
                manifest.published_at, manifest.word_count, manifest.internal_links_count
            ))

    def get_stale_pages(self, data_hashes: dict[str, str], template_hashes: dict[str, str]) -> list[str]:
        """Get URLs of pages that need regeneration."""
        stale = []
        with self.connection() as conn:
            rows = conn.execute("SELECT url, data_hash, template_hash, template FROM page_manifest").fetchall()
            for row in rows:
                url = row["url"]
                current_data_hash = data_hashes.get(url)
                current_template_hash = template_hashes.get(row["template"])
                if current_data_hash != row["data_hash"] or current_template_hash != row["template_hash"]:
                    stale.append(url)
        return stale

    def get_pages_by_status(self, status: str) -> list[PageManifest]:
        """Get all pages with a specific status."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM page_manifest WHERE status = ?", (status,)
            ).fetchall()
            return [
                PageManifest(
                    url=row["url"],
                    template=row["template"],
                    data_hash=row["data_hash"],
                    template_hash=row["template_hash"],
                    status=row["status"],
                    generated_at=row["generated_at"],
                    published_at=row["published_at"],
                    word_count=row["word_count"],
                    internal_links_count=row["internal_links_count"]
                )
                for row in rows
            ]

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self.connection() as conn:
            stats = {}
            for table in ["categories", "subcategories", "regions", "teas", "teaware", "occasions", "comparison_pairs"]:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[table] = count

            # Tea tier breakdown
            tier_rows = conn.execute("""
                SELECT tier, COUNT(*) as count FROM teas GROUP BY tier
            """).fetchall()
            stats["teas_by_tier"] = {row["tier"]: row["count"] for row in tier_rows}

            # Category breakdown
            cat_rows = conn.execute("""
                SELECT category_id, COUNT(*) as count FROM teas GROUP BY category_id
            """).fetchall()
            stats["teas_by_category"] = {row["category_id"]: row["count"] for row in cat_rows}

            # Page manifest stats
            manifest_rows = conn.execute("""
                SELECT status, COUNT(*) as count FROM page_manifest GROUP BY status
            """).fetchall()
            stats["pages_by_status"] = {row["status"]: row["count"] for row in manifest_rows}

            return stats

    # =========================================================================
    # EXPORT / IMPORT
    # =========================================================================

    def export_to_json(self, output_dir: Path) -> None:
        """Export all data to JSON files for git tracking."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export categories
        categories = self.get_all_categories()
        with open(output_dir / "categories.json", "w") as f:
            json.dump([c.model_dump() for c in categories], f, indent=2)

        # Export regions
        regions = self.get_all_regions()
        with open(output_dir / "regions.json", "w") as f:
            json.dump([r.model_dump() for r in regions], f, indent=2, default=str)

        # Export teas
        teas = self.get_all_teas()
        with open(output_dir / "teas.json", "w") as f:
            json.dump([t.model_dump() for t in teas], f, indent=2, default=str)

        # Export teaware
        teaware = self.get_all_teaware()
        with open(output_dir / "teaware.json", "w") as f:
            json.dump([t.model_dump() for t in teaware], f, indent=2, default=str)

        # Export occasions
        occasions = self.get_all_occasions()
        with open(output_dir / "occasions.json", "w") as f:
            json.dump([o.model_dump() for o in occasions], f, indent=2)

    def import_from_json(self, input_dir: Path) -> None:
        """Import data from JSON files."""
        # Import categories
        cat_file = input_dir / "categories.json"
        if cat_file.exists():
            with open(cat_file) as f:
                for data in json.load(f):
                    try:
                        self.insert_category(Category(**data))
                    except sqlite3.IntegrityError:
                        pass  # Already exists

        # Import regions
        region_file = input_dir / "regions.json"
        if region_file.exists():
            with open(region_file) as f:
                for data in json.load(f):
                    try:
                        self.insert_region(Region(**data))
                    except sqlite3.IntegrityError:
                        pass

        # Import teas (after categories and regions)
        tea_file = input_dir / "teas.json"
        if tea_file.exists():
            with open(tea_file) as f:
                for data in json.load(f):
                    try:
                        self.insert_tea(Tea(**data))
                    except sqlite3.IntegrityError:
                        pass
