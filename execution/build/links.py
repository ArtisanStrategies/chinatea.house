"""
Internal linking logic for chinatea.house.

Builds contextual links for SEO and navigation following these rules:
- Every page links UP to parent (tea -> category -> hub)
- Hubs link DOWN to all children
- Teas link ACROSS to similar teas (3-5 links)
- Cross-pillar: tea <-> region <-> teaware
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from execution.data.db import Database


class InternalLinkBuilder:
    """Builds internal link structures for pages."""

    def __init__(self, db: "Database"):
        self.db = db
        self._category_cache = None
        self._region_cache = None
        self._teaware_cache = None
        self._tea_cache = None
        self._comparison_cache = None
        self._comparisons_by_tea_cache = None

    @property
    def categories(self):
        """Cached category lookup."""
        if self._category_cache is None:
            cats = self.db.get_all_categories()
            self._category_cache = {c.id: c for c in cats}
        return self._category_cache

    @property
    def regions(self):
        """Cached region lookup."""
        if self._region_cache is None:
            regs = self.db.get_all_regions()
            self._region_cache = {r.id: r for r in regs}
        return self._region_cache

    @property
    def teas(self):
        """Cached tea lookup by ID."""
        if self._tea_cache is None:
            teas = self.db.get_all_teas()
            self._tea_cache = {t.id: t for t in teas}
        return self._tea_cache

    @property
    def comparisons(self):
        """Cached comparison lookup by ID."""
        if self._comparison_cache is None:
            comps = self.db.get_all_comparisons(valid_only=True)
            self._comparison_cache = {c.id: c for c in comps}
        return self._comparison_cache

    @property
    def comparisons_by_tea(self):
        """Cached mapping of tea ID -> list of comparison objects."""
        if self._comparisons_by_tea_cache is None:
            mapping: dict[str, list] = {}
            for comp in self.comparisons.values():
                mapping.setdefault(comp.tea_a_id, []).append(comp)
                mapping.setdefault(comp.tea_b_id, []).append(comp)
            self._comparisons_by_tea_cache = mapping
        return self._comparisons_by_tea_cache

    @property
    def teaware(self):
        """Cached teaware lookup."""
        if self._teaware_cache is None:
            items = self.db.get_all_teaware()
            self._teaware_cache = {t.id: t for t in items}
        return self._teaware_cache

    def get_tea_links(self, tea) -> dict:
        """Get all internal links for a tea detail page."""
        category = self.categories.get(tea.category_id)
        region = self.regions.get(tea.region_id)

        # UP links (to parents)
        parent_links = []
        if category:
            parent_links.append({
                "url": f"/category/{category.id}/",
                "label": f"All {category.name_en}"
            })
        if region:
            parent_links.append({
                "url": f"/region/{region.id}/",
                "label": f"Teas from {region.name_en}"
            })
            # Add province if different
            if region.parent_id and region.parent_id in self.regions:
                province = self.regions[region.parent_id]
                parent_links.append({
                    "url": f"/region/{province.id}/",
                    "label": f"{province.name_en} Province"
                })

        # ACROSS links (similar teas)
        similar_teas = self.db.get_similar_teas(tea.id, limit=5)

        # Cross-pillar links
        cross_links = self._get_cross_pillar_links(tea, category, region)

        # Recommended teaware based on category
        recommended_teaware = self._get_recommended_teaware(category)

        return {
            "parent_links": parent_links,
            "similar_teas": similar_teas,
            "cross_links": cross_links,
            "recommended_teaware": recommended_teaware,
        }

    def get_category_links(self, category) -> dict:
        """Get all internal links for a category pillar page."""
        # DOWN links (to teas)
        teas = self.db.get_teas_by_category(category.id)

        # Organize teas by subcategory
        subcategories = self.db.get_subcategories_by_category(category.id)
        teas_by_subcategory = {}
        for sub in subcategories:
            teas_by_subcategory[sub.id] = [t for t in teas if t.subcategory_id == sub.id]

        # Get regions that produce this category
        regions = []
        teas_by_region = {}
        for tea in teas:
            if tea.region_id not in teas_by_region:
                teas_by_region[tea.region_id] = []
                if tea.region_id in self.regions:
                    regions.append(self.regions[tea.region_id])
            teas_by_region[tea.region_id].append(tea)

        # ACROSS links to other categories
        other_categories = [c for c in self.categories.values() if c.id != category.id]

        # Cross-pillar links
        cross_links = [
            {"url": "/brewing/", "label": "Brewing Guides"},
            {"url": "/best-tea-for/", "label": "Best Tea For..."},
            {"url": "/teaware/", "label": "Essential Teaware"},
        ]

        # Recommended occasions
        occasions = self.db.get_all_occasions()
        recommended = [o for o in occasions if category.id in o.preferred_categories]

        return {
            "teas": teas,
            "subcategories": subcategories,
            "teas_by_subcategory": teas_by_subcategory,
            "regions": regions,
            "teas_by_region": teas_by_region,
            "other_categories": other_categories,
            "cross_links": cross_links,
            "recommended_occasions": recommended,
            "parent_links": [{"url": "/category/", "label": "All Categories"}],
        }

    def get_region_links(self, region) -> dict:
        """Get all internal links for a region pillar page."""
        # Parent region
        parent_region = None
        if region.parent_id and region.parent_id in self.regions:
            parent_region = self.regions[region.parent_id]

        # Child regions
        child_regions = self.db.get_child_regions(region.id)

        # Sibling regions
        sibling_regions = []
        if region.parent_id:
            siblings = self.db.get_child_regions(region.parent_id)
            sibling_regions = [r for r in siblings if r.id != region.id]

        # Teas from this region
        teas = self.db.get_teas_by_region(region.id)

        # Also get teas from child regions
        for child in child_regions:
            teas.extend(self.db.get_teas_by_region(child.id))

        # Organize by category
        teas_by_category = {}
        categories_in_region = []
        for tea in teas:
            if tea.category_id not in teas_by_category:
                teas_by_category[tea.category_id] = []
                if tea.category_id in self.categories:
                    categories_in_region.append(self.categories[tea.category_id])
            teas_by_category[tea.category_id].append(tea)

        # Organize by sub-region
        teas_by_subregion = {}
        for child in child_regions:
            child_teas = self.db.get_teas_by_region(child.id)
            if child_teas:
                teas_by_subregion[child.id] = child_teas

        # Cross-pillar links
        cross_links = [
            {"url": "/category/", "label": "Tea Categories"},
            {"url": "/brewing/", "label": "Brewing Guides"},
        ]

        parent_links = [{"url": "/region/", "label": "All Regions"}]
        if parent_region:
            parent_links.append({
                "url": f"/region/{parent_region.id}/",
                "label": parent_region.name_en
            })

        return {
            "parent_region": parent_region,
            "child_regions": child_regions,
            "sibling_regions": sibling_regions,
            "teas": teas,
            "teas_by_category": teas_by_category,
            "teas_by_subregion": teas_by_subregion,
            "categories_in_region": categories_in_region,
            "cross_links": cross_links,
            "parent_links": parent_links,
        }

    def get_comparison_links(self, tea_a, tea_b) -> dict:
        """Get internal links for a comparison page using cached data."""
        # Related comparisons (other comparisons involving these teas)
        comps_a = self.comparisons_by_tea.get(tea_a.id, [])
        comps_b = self.comparisons_by_tea.get(tea_b.id, [])

        related = []
        seen = set()
        for comp in comps_a + comps_b:
            if comp.id not in seen and not (
                (comp.tea_a_id == tea_a.id and comp.tea_b_id == tea_b.id) or
                (comp.tea_a_id == tea_b.id and comp.tea_b_id == tea_a.id)
            ):
                # Load the tea objects for display from cache
                other_a = self.teas.get(comp.tea_a_id)
                other_b = self.teas.get(comp.tea_b_id)
                if other_a and other_b:
                    related.append({
                        "tea_a": other_a,
                        "tea_b": other_b,
                        "comparison": comp
                    })
                    seen.add(comp.id)

        cross_links = [
            {"url": f"/tea/{tea_a.id}/", "label": f"About {tea_a.name_en}"},
            {"url": f"/tea/{tea_b.id}/", "label": f"About {tea_b.name_en}"},
            {"url": "/compare/", "label": "More Comparisons"},
        ]

        return {
            "related_comparisons": related[:6],
            "cross_links": cross_links,
            "parent_links": [{"url": "/compare/", "label": "Tea Comparisons"}],
        }

    def _get_cross_pillar_links(self, tea, category, region) -> list:
        """Generate cross-pillar links for a tea."""
        links = []

        # Link to brewing guide for this category
        if category:
            links.append({
                "url": f"/brewing/{category.id}/",
                "label": f"How to Brew {category.name_en}"
            })

        # Link to occasions
        if tea.best_for:
            for occasion_id in tea.best_for[:2]:
                links.append({
                    "url": f"/best-tea-for/{occasion_id}/",
                    "label": f"Best Tea for {occasion_id.replace('-', ' ').title()}"
                })

        # Comparison links
        similar = self.db.get_similar_teas(tea.id, limit=2)
        for sim in similar:
            links.append({
                "url": f"/compare/{tea.id}-vs-{sim.id}/",
                "label": f"{tea.name_en} vs {sim.name_en}"
            })

        return links[:6]

    def _get_recommended_teaware(self, category) -> list:
        """Get recommended teaware for a category."""
        if not category:
            return []

        recommended = []
        for item in self.teaware.values():
            if category.id in item.best_for_categories:
                recommended.append(item)

        return recommended[:3]
