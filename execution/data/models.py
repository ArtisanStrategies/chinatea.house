"""
Pydantic models for chinatea.house data entities.

These models define the structure for all tea-related data, ensuring
type safety and validation throughout the application.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TeaCategory(str, Enum):
    """The seven main categories of Chinese tea."""
    GREEN = "green"
    WHITE = "white"
    YELLOW = "yellow"
    OOLONG = "oolong"
    BLACK = "black"
    DARK = "dark"  # Includes pu-erh
    SCENTED = "scented"  # Jasmine, osmanthus, etc.


class RoastLevel(str, Enum):
    """Roast levels for oolong and some other teas."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    MEDIUM_HEAVY = "medium-heavy"
    HEAVY = "heavy"
    CHARCOAL = "charcoal"


class CaffeineLevel(str, Enum):
    """Relative caffeine content."""
    VERY_LOW = "very-low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very-high"


class BodyLevel(str, Enum):
    """Tea body/mouthfeel intensity."""
    LIGHT = "light"
    LIGHT_MEDIUM = "light-medium"
    MEDIUM = "medium"
    MEDIUM_FULL = "medium-full"
    FULL = "full"


class RegionType(str, Enum):
    """Geographic hierarchy levels."""
    COUNTRY = "country"
    PROVINCE = "province"
    PREFECTURE = "prefecture"
    COUNTY = "county"
    VILLAGE = "village"
    MOUNTAIN = "mountain"


class TeawareType(str, Enum):
    """Types of tea brewing vessels and equipment."""
    TEAPOT = "teapot"
    GAIWAN = "gaiwan"
    CUP = "cup"
    PITCHER = "pitcher"
    STRAINER = "strainer"
    TRAY = "tray"
    KETTLE = "kettle"
    SCOOP = "scoop"
    PICK = "pick"
    TOWEL = "towel"


class BrewingParams(BaseModel):
    """Brewing parameters for a tea preparation method."""
    water_temp_c: int = Field(ge=60, le=100, description="Water temperature in Celsius")
    water_temp_f: Optional[int] = Field(default=None, ge=140, le=212, description="Water temperature in Fahrenheit (auto-calculated)")
    leaf_ratio_g_per_100ml: float = Field(ge=1, le=15, description="Grams of tea per 100ml water")
    first_steep_seconds: int = Field(ge=5, le=300, description="First steep duration in seconds")
    subsequent_steep_seconds: int = Field(ge=5, le=600, description="Subsequent steep duration")
    steep_increment_seconds: int = Field(ge=0, le=60, default=5, description="Time added per steep")
    num_steeps: int = Field(ge=1, le=20, description="Expected number of steeps")
    rinse_recommended: bool = Field(default=False, description="Whether to rinse leaves first")

    @field_validator("water_temp_f", mode="before")
    @classmethod
    def calculate_fahrenheit(cls, v, info):
        """Auto-calculate Fahrenheit if not provided."""
        if v is None and "water_temp_c" in info.data:
            return int(info.data["water_temp_c"] * 9 / 5 + 32)
        return v


class PriceRange(BaseModel):
    """Price range for a tea quality tier."""
    min_usd_per_50g: float = Field(ge=0, description="Minimum price per 50g in USD")
    max_usd_per_50g: float = Field(ge=0, description="Maximum price per 50g in USD")


class Category(BaseModel):
    """A main tea category (e.g., Green, Oolong)."""
    id: str = Field(pattern=r"^[a-z]+$", description="Slug identifier")
    name_en: str = Field(min_length=1, max_length=50)
    name_zh: Optional[str] = Field(default=None, max_length=20)
    description: str = Field(min_length=10, max_length=2000)
    oxidation_range_min: float = Field(ge=0, le=1, description="Minimum oxidation level")
    oxidation_range_max: float = Field(ge=0, le=1, description="Maximum oxidation level")
    color_hex: Optional[str] = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


class Subcategory(BaseModel):
    """A subcategory within a main category (e.g., Dancong within Oolong)."""
    id: str = Field(pattern=r"^[a-z0-9-]+$", description="Slug identifier")
    category_id: str = Field(description="Parent category ID")
    name_en: str = Field(min_length=1, max_length=100)
    name_zh: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=1000)


class Region(BaseModel):
    """A geographic region where tea is grown."""
    id: str = Field(pattern=r"^[a-z0-9-]+$", description="Slug identifier")
    parent_id: Optional[str] = Field(default=None, description="Parent region ID")
    name_en: str = Field(min_length=1, max_length=100)
    name_zh: Optional[str] = Field(default=None, max_length=50)
    name_pinyin: Optional[str] = Field(default=None, max_length=100)
    region_type: RegionType
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    elevation_min_m: Optional[int] = Field(default=None, ge=0, le=6000)
    elevation_max_m: Optional[int] = Field(default=None, ge=0, le=6000)
    climate: Optional[str] = Field(default=None, max_length=200)
    soil_type: Optional[str] = Field(default=None, max_length=200)
    terroir_notes: Optional[str] = Field(default=None, max_length=1000)
    famous_teas: list[str] = Field(default_factory=list)


class Tea(BaseModel):
    """A specific tea variety."""
    id: str = Field(pattern=r"^[a-z0-9-]+$", description="Slug identifier (e.g., da-hong-pao)")
    name_en: str = Field(min_length=1, max_length=200, description="English name")
    name_zh: Optional[str] = Field(default=None, max_length=50, description="Chinese characters")
    name_pinyin: Optional[str] = Field(default=None, max_length=100, description="Pinyin romanization")

    # Classification
    category_id: str = Field(description="Main category (green, oolong, etc.)")
    subcategory_id: Optional[str] = Field(default=None, description="Subcategory ID")
    region_id: str = Field(description="Primary growing region")
    alternate_region_ids: list[str] = Field(default_factory=list)

    # Processing characteristics
    oxidation_level: Optional[float] = Field(default=None, ge=0, le=1, description="0-1 scale")
    roast_level: Optional[RoastLevel] = Field(default=None)
    is_aged: bool = Field(default=False)
    age_years: Optional[int] = Field(default=None, ge=0)
    harvest_season: Optional[str] = Field(default=None, description="e.g., 'spring', 'autumn'")
    cultivar: Optional[str] = Field(default=None, max_length=100)

    # Sensory profile
    caffeine_level: Optional[CaffeineLevel] = Field(default=None)
    flavor_primary: list[str] = Field(default_factory=list, max_length=5)
    flavor_secondary: list[str] = Field(default_factory=list, max_length=10)
    aroma: list[str] = Field(default_factory=list, max_length=5)
    body: Optional[BodyLevel] = Field(default=None)
    finish: Optional[str] = Field(default=None, max_length=200)
    mouthfeel: Optional[str] = Field(default=None, max_length=200)

    # Brewing
    brewing_gongfu: Optional[BrewingParams] = Field(default=None)
    brewing_western: Optional[BrewingParams] = Field(default=None)
    brewing_grandpa: Optional[BrewingParams] = Field(default=None)
    brewing_cold: Optional[BrewingParams] = Field(default=None)

    # Pricing (USD per 50g)
    price_budget: Optional[PriceRange] = Field(default=None)
    price_mid: Optional[PriceRange] = Field(default=None)
    price_premium: Optional[PriceRange] = Field(default=None)

    # Metadata
    best_for: list[str] = Field(default_factory=list, description="Use cases/occasions")
    similar_tea_ids: list[str] = Field(default_factory=list)
    description_brief: str = Field(min_length=50, max_length=500)
    description_full: Optional[str] = Field(default=None, max_length=5000)
    history: Optional[str] = Field(default=None, max_length=2000)

    # Data quality
    tier: int = Field(ge=1, le=3, default=2, description="1=complete, 2=good, 3=basic")
    sources: list[str] = Field(default_factory=list)


class Teaware(BaseModel):
    """A piece of tea brewing equipment."""
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    name_en: str = Field(min_length=1, max_length=100)
    name_zh: Optional[str] = Field(default=None, max_length=50)
    teaware_type: TeawareType
    materials: list[str] = Field(default_factory=list)
    origin_region_id: Optional[str] = Field(default=None)
    price_range: Optional[PriceRange] = Field(default=None)
    description: str = Field(min_length=10, max_length=2000)
    best_for_categories: list[str] = Field(default_factory=list)
    care_instructions: Optional[str] = Field(default=None, max_length=1000)


class Occasion(BaseModel):
    """A tea drinking occasion or use case."""
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=10, max_length=1000)
    preferred_categories: list[str] = Field(default_factory=list)
    preferred_attributes: dict = Field(default_factory=dict)
    time_of_day: Optional[str] = Field(default=None)
    season: Optional[str] = Field(default=None)


class BrewingMethod(BaseModel):
    """A tea brewing method/style."""
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    name_en: str = Field(min_length=1, max_length=100)
    name_zh: Optional[str] = Field(default=None, max_length=50)
    description: str = Field(min_length=10, max_length=2000)
    equipment_required: list[str] = Field(default_factory=list)
    equipment_optional: list[str] = Field(default_factory=list)
    best_for_categories: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)


class ComparisonPair(BaseModel):
    """A pair of teas to compare."""
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    tea_a_id: str
    tea_b_id: str
    comparison_type: str = Field(description="e.g., 'similar', 'contrast', 'regional'")
    is_valid: bool = Field(default=True)
    narrative: Optional[str] = Field(default=None, max_length=5000)
    key_differences: list[str] = Field(default_factory=list)
    key_similarities: list[str] = Field(default_factory=list)


class PageManifest(BaseModel):
    """Tracking record for a generated page."""
    url: str = Field(description="Relative URL path")
    template: str = Field(description="Template name used")
    data_hash: str = Field(description="Hash of input data")
    template_hash: str = Field(description="Hash of template")
    status: str = Field(description="draft, published, archived")
    generated_at: str = Field(description="ISO timestamp")
    published_at: Optional[str] = Field(default=None)
    word_count: int = Field(default=0)
    internal_links_count: int = Field(default=0)
