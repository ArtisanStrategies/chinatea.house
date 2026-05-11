"""
Auto-generation of tea comparison pairs.
Creates meaningful comparisons based on shared attributes, categories, and regions.
"""

from dataclasses import dataclass
from typing import Optional
import sqlite3
from pathlib import Path


@dataclass
class ComparisonPair:
    tea_a_id: str
    tea_b_id: str
    comparison_type: str  # same_category, same_region, similar_flavor, price_tier, etc.
    relevance_score: float  # 0-1, higher = more interesting comparison


class ComparisonGenerator:
    """Generates meaningful tea comparison pairs automatically."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def generate_all_pairs(self) -> list[ComparisonPair]:
        """Generate all meaningful comparison pairs."""
        pairs = []

        # Get all teas
        with self.connection() as conn:
            teas = conn.execute("""
                SELECT t.id, t.name_en, t.category_id, t.subcategory_id,
                       t.region_id, t.oxidation_level, t.caffeine_level,
                       t.flavor_primary, t.body
                FROM teas t
            """).fetchall()

        tea_list = [dict(t) for t in teas]

        # Generate pairs using different strategies
        pairs.extend(self._same_category_pairs(tea_list))
        pairs.extend(self._same_region_pairs(tea_list))
        pairs.extend(self._similar_oxidation_pairs(tea_list))
        pairs.extend(self._similar_flavor_pairs(tea_list))
        pairs.extend(self._cross_category_pairs(tea_list))

        # Deduplicate and sort by relevance
        seen = set()
        unique_pairs = []
        for pair in pairs:
            key = tuple(sorted([pair.tea_a_id, pair.tea_b_id]))
            if key not in seen:
                seen.add(key)
                unique_pairs.append(pair)

        unique_pairs.sort(key=lambda p: p.relevance_score, reverse=True)
        return unique_pairs

    def _same_category_pairs(self, teas: list[dict]) -> list[ComparisonPair]:
        """Compare teas within the same category."""
        pairs = []
        by_category = {}

        for tea in teas:
            cat = tea['category_id']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tea)

        for category, category_teas in by_category.items():
            for i, tea_a in enumerate(category_teas):
                for tea_b in category_teas[i+1:]:
                    # Higher score if same subcategory
                    score = 0.7
                    if tea_a.get('subcategory_id') == tea_b.get('subcategory_id'):
                        score = 0.85

                    pairs.append(ComparisonPair(
                        tea_a_id=tea_a['id'],
                        tea_b_id=tea_b['id'],
                        comparison_type='same_category',
                        relevance_score=score
                    ))

        return pairs

    def _same_region_pairs(self, teas: list[dict]) -> list[ComparisonPair]:
        """Compare teas from the same region."""
        pairs = []
        by_region = {}

        for tea in teas:
            region = tea['region_id']
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(tea)

        for region, region_teas in by_region.items():
            for i, tea_a in enumerate(region_teas):
                for tea_b in region_teas[i+1:]:
                    # Higher score if different categories (more interesting)
                    score = 0.6
                    if tea_a['category_id'] != tea_b['category_id']:
                        score = 0.8

                    pairs.append(ComparisonPair(
                        tea_a_id=tea_a['id'],
                        tea_b_id=tea_b['id'],
                        comparison_type='same_region',
                        relevance_score=score
                    ))

        return pairs

    def _similar_oxidation_pairs(self, teas: list[dict]) -> list[ComparisonPair]:
        """Compare teas with similar oxidation levels across categories."""
        pairs = []

        # Group by oxidation bands
        oxidation_bands = {
            'minimal': (0, 0.15),
            'light': (0.15, 0.35),
            'medium': (0.35, 0.65),
            'heavy': (0.65, 0.85),
            'full': (0.85, 1.0)
        }

        by_band = {band: [] for band in oxidation_bands}

        for tea in teas:
            ox = tea.get('oxidation_level')
            if ox is None:
                continue
            for band, (low, high) in oxidation_bands.items():
                if low <= ox <= high:
                    by_band[band].append(tea)
                    break

        for band, band_teas in by_band.items():
            for i, tea_a in enumerate(band_teas):
                for tea_b in band_teas[i+1:]:
                    # Only interesting if different categories
                    if tea_a['category_id'] == tea_b['category_id']:
                        continue

                    pairs.append(ComparisonPair(
                        tea_a_id=tea_a['id'],
                        tea_b_id=tea_b['id'],
                        comparison_type='similar_oxidation',
                        relevance_score=0.65
                    ))

        return pairs

    def _similar_flavor_pairs(self, teas: list[dict]) -> list[ComparisonPair]:
        """Compare teas with overlapping flavor profiles."""
        pairs = []

        for i, tea_a in enumerate(teas):
            flavors_a = set((tea_a.get('flavor_primary') or '').split(','))
            flavors_a = {f.strip().lower() for f in flavors_a if f.strip()}

            if not flavors_a:
                continue

            for tea_b in teas[i+1:]:
                flavors_b = set((tea_b.get('flavor_primary') or '').split(','))
                flavors_b = {f.strip().lower() for f in flavors_b if f.strip()}

                if not flavors_b:
                    continue

                # Calculate Jaccard similarity
                intersection = len(flavors_a & flavors_b)
                union = len(flavors_a | flavors_b)

                if union > 0 and intersection >= 2:
                    similarity = intersection / union
                    # More interesting if different categories
                    bonus = 0.1 if tea_a['category_id'] != tea_b['category_id'] else 0

                    pairs.append(ComparisonPair(
                        tea_a_id=tea_a['id'],
                        tea_b_id=tea_b['id'],
                        comparison_type='similar_flavor',
                        relevance_score=min(0.5 + similarity * 0.4 + bonus, 0.95)
                    ))

        return pairs

    def _cross_category_pairs(self, teas: list[dict]) -> list[ComparisonPair]:
        """Generate interesting cross-category comparisons."""
        pairs = []

        # Interesting cross-category comparisons
        interesting_combos = [
            ('green', 'white'),      # Light, fresh teas
            ('oolong', 'black'),     # Oxidation spectrum
            ('dark', 'black'),       # Fermentation comparison
            ('green', 'yellow'),     # Processing difference
            ('oolong', 'white'),     # Fujian teas often
        ]

        by_category = {}
        for tea in teas:
            cat = tea['category_id']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tea)

        for cat_a, cat_b in interesting_combos:
            teas_a = by_category.get(cat_a, [])
            teas_b = by_category.get(cat_b, [])

            for tea_a in teas_a:
                for tea_b in teas_b:
                    # Boost if same region
                    score = 0.55
                    if tea_a.get('region_id') == tea_b.get('region_id'):
                        score = 0.75

                    pairs.append(ComparisonPair(
                        tea_a_id=tea_a['id'],
                        tea_b_id=tea_b['id'],
                        comparison_type='cross_category',
                        relevance_score=score
                    ))

        return pairs

    def save_pairs_to_db(self, pairs: list[ComparisonPair]) -> int:
        """Save generated pairs to database."""
        with self.connection() as conn:
            # Clear existing auto-generated pairs
            conn.execute("DELETE FROM comparison_pairs WHERE is_valid = 1")

            inserted = 0
            for pair in pairs:
                try:
                    conn.execute("""
                        INSERT INTO comparison_pairs
                        (id, tea_a_id, tea_b_id, comparison_type, relevance_score, is_valid)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (
                        f"{pair.tea_a_id}-vs-{pair.tea_b_id}",
                        pair.tea_a_id,
                        pair.tea_b_id,
                        pair.comparison_type,
                        pair.relevance_score
                    ))
                    inserted += 1
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    pass

            conn.commit()
            return inserted


def generate_comparisons(db_path: Path) -> int:
    """Generate and save all comparison pairs."""
    generator = ComparisonGenerator(db_path)
    pairs = generator.generate_all_pairs()
    return generator.save_pairs_to_db(pairs)
