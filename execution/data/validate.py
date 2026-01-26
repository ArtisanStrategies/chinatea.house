"""
Data validation for chinatea.house.

Validates data integrity, relationships, and completeness.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import Database


class DataValidator:
    """Validates data integrity in the tea database."""

    def __init__(self, db: "Database"):
        self.db = db
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.entities_checked = 0
        self.relationships_verified = 0

    def validate_all(self) -> dict:
        """Run all validation checks."""
        self.errors = []
        self.warnings = []
        self.entities_checked = 0
        self.relationships_verified = 0

        self._validate_categories()
        self._validate_regions()
        self._validate_teas()
        self._validate_comparisons()
        self._validate_cross_references()

        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "entities_checked": self.entities_checked,
            "relationships_verified": self.relationships_verified,
            "valid": len(self.errors) == 0
        }

    def _validate_categories(self) -> None:
        """Validate category data."""
        categories = self.db.get_all_categories()
        self.entities_checked += len(categories)

        expected_ids = {"green", "white", "yellow", "oolong", "black", "dark", "scented"}
        actual_ids = {c.id for c in categories}

        missing = expected_ids - actual_ids
        if missing:
            self.errors.append(f"Missing required categories: {missing}")

        for cat in categories:
            if cat.oxidation_range_min > cat.oxidation_range_max:
                self.errors.append(
                    f"Category {cat.id}: oxidation_range_min ({cat.oxidation_range_min}) > "
                    f"oxidation_range_max ({cat.oxidation_range_max})"
                )

            if len(cat.description) < 50:
                self.warnings.append(
                    f"Category {cat.id}: description is short ({len(cat.description)} chars)"
                )

    def _validate_regions(self) -> None:
        """Validate region hierarchy."""
        regions = self.db.get_all_regions()
        self.entities_checked += len(regions)

        region_ids = {r.id for r in regions}

        # Check for orphan regions (parent doesn't exist)
        for region in regions:
            if region.parent_id and region.parent_id not in region_ids:
                self.errors.append(
                    f"Region {region.id}: parent '{region.parent_id}' not found"
                )
                continue

            self.relationships_verified += 1

            # Validate hierarchy rules
            if region.parent_id:
                parent = self.db.get_region(region.parent_id)
                if parent:
                    valid_children = {
                        "country": ["province"],
                        "province": ["prefecture", "county", "mountain"],
                        "prefecture": ["county", "village", "mountain"],
                        "county": ["village", "mountain"],
                    }
                    allowed = valid_children.get(parent.region_type.value, [])
                    if region.region_type.value not in allowed:
                        self.warnings.append(
                            f"Region {region.id}: type '{region.region_type.value}' "
                            f"unusual under parent type '{parent.region_type.value}'"
                        )

        # Check China exists as root
        china = self.db.get_region("china")
        if not china:
            self.errors.append("Missing root region: china")

    def _validate_teas(self) -> None:
        """Validate tea data completeness."""
        teas = self.db.get_all_teas()
        self.entities_checked += len(teas)

        category_ids = {c.id for c in self.db.get_all_categories()}
        region_ids = {r.id for r in self.db.get_all_regions()}

        for tea in teas:
            # Check foreign keys
            if tea.category_id not in category_ids:
                self.errors.append(
                    f"Tea {tea.id}: category '{tea.category_id}' not found"
                )
            else:
                self.relationships_verified += 1

            if tea.region_id not in region_ids:
                self.errors.append(
                    f"Tea {tea.id}: region '{tea.region_id}' not found"
                )
            else:
                self.relationships_verified += 1

            # Tier-specific completeness checks
            if tea.tier == 1:
                self._validate_tier1_tea(tea)
            elif tea.tier == 2:
                self._validate_tier2_tea(tea)

            # Oxidation level consistency
            if tea.oxidation_level is not None and tea.category_id in category_ids:
                cat = self.db.get_category(tea.category_id)
                if cat:
                    if not (cat.oxidation_range_min <= tea.oxidation_level <= cat.oxidation_range_max):
                        self.warnings.append(
                            f"Tea {tea.id}: oxidation {tea.oxidation_level} outside "
                            f"category range [{cat.oxidation_range_min}, {cat.oxidation_range_max}]"
                        )

    def _validate_tier1_tea(self, tea) -> None:
        """Validate Tier-1 tea has complete data."""
        required_fields = [
            ("name_zh", "Chinese name"),
            ("oxidation_level", "oxidation level"),
            ("caffeine_level", "caffeine level"),
            ("body", "body"),
            ("brewing_gongfu", "gongfu brewing params"),
        ]

        for field, label in required_fields:
            if getattr(tea, field) is None:
                self.warnings.append(f"Tier-1 tea {tea.id}: missing {label}")

        if len(tea.flavor_primary) < 2:
            self.warnings.append(
                f"Tier-1 tea {tea.id}: needs more primary flavors "
                f"(has {len(tea.flavor_primary)})"
            )

        if len(tea.description_brief) < 100:
            self.warnings.append(
                f"Tier-1 tea {tea.id}: description too short "
                f"({len(tea.description_brief)} chars)"
            )

    def _validate_tier2_tea(self, tea) -> None:
        """Validate Tier-2 tea has adequate data."""
        if not tea.flavor_primary:
            self.warnings.append(f"Tier-2 tea {tea.id}: no primary flavors")

        if len(tea.description_brief) < 50:
            self.warnings.append(
                f"Tier-2 tea {tea.id}: description very short "
                f"({len(tea.description_brief)} chars)"
            )

    def _validate_comparisons(self) -> None:
        """Validate comparison pairs."""
        comparisons = self.db.get_all_comparisons(valid_only=False)
        self.entities_checked += len(comparisons)

        tea_ids = {t.id for t in self.db.get_all_teas()}

        for comp in comparisons:
            if comp.tea_a_id not in tea_ids:
                self.errors.append(
                    f"Comparison {comp.id}: tea_a '{comp.tea_a_id}' not found"
                )
            else:
                self.relationships_verified += 1

            if comp.tea_b_id not in tea_ids:
                self.errors.append(
                    f"Comparison {comp.id}: tea_b '{comp.tea_b_id}' not found"
                )
            else:
                self.relationships_verified += 1

            if comp.tea_a_id == comp.tea_b_id:
                self.errors.append(
                    f"Comparison {comp.id}: cannot compare tea to itself"
                )

    def _validate_cross_references(self) -> None:
        """Validate cross-entity references."""
        teas = self.db.get_all_teas()
        tea_ids = {t.id for t in teas}

        # Check similar tea references
        for tea in teas:
            for similar_id in tea.similar_tea_ids:
                if similar_id not in tea_ids:
                    self.warnings.append(
                        f"Tea {tea.id}: similar tea '{similar_id}' not found"
                    )
                elif similar_id == tea.id:
                    self.warnings.append(
                        f"Tea {tea.id}: references itself as similar"
                    )
                else:
                    self.relationships_verified += 1

        # Check category has teas
        categories = self.db.get_all_categories()
        for cat in categories:
            teas_in_cat = self.db.get_teas_by_category(cat.id)
            if not teas_in_cat:
                self.warnings.append(f"Category {cat.id}: has no teas")

        # Check provinces have teas
        provinces = self.db.get_regions_by_type("province")
        for province in provinces:
            # Get all teas in this province or child regions
            teas_in_province = self.db.get_teas_by_region(province.id)
            child_regions = self.db.get_child_regions(province.id)
            for child in child_regions:
                teas_in_province.extend(self.db.get_teas_by_region(child.id))

            if not teas_in_province:
                self.warnings.append(f"Province {province.id}: has no teas")


def validate_single_tea(tea_data: dict) -> tuple[bool, list[str]]:
    """Validate a single tea entity before insertion."""
    from .models import Tea
    errors = []

    try:
        Tea(**tea_data)
    except Exception as e:
        errors.append(f"Validation error: {e}")
        return False, errors

    # Additional business logic validations
    if tea_data.get("tier") == 1:
        required = ["name_zh", "oxidation_level", "caffeine_level"]
        for field in required:
            if not tea_data.get(field):
                errors.append(f"Tier-1 tea requires {field}")

    return len(errors) == 0, errors
