"""
AI content generation using Claude API.

Generates pillar page content and comparison narratives.
"""

import json
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from execution.data.db import Database


class ContentGenerator:
    """Generates AI content for pillar pages and comparisons."""

    def __init__(self, db: "Database", api_key: Optional[str] = None):
        self.db = db
        self.api_key = api_key
        self._client = None

    @property
    def client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("Anthropic API key required for content generation")
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        return self._client

    def generate_category_content(self, category_id: str) -> dict:
        """Generate comprehensive content for a category pillar page."""
        category = self.db.get_category(category_id)
        if not category:
            raise ValueError(f"Category not found: {category_id}")

        teas = self.db.get_teas_by_category(category_id)
        subcategories = self.db.get_subcategories_by_category(category_id)

        prompt = self._build_category_prompt(category, teas, subcategories)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_content_response(response.content[0].text)

    def generate_comparison_narrative(
        self,
        tea_a_id: str,
        tea_b_id: str
    ) -> dict:
        """Generate comparison narrative for two teas."""
        tea_a = self.db.get_tea(tea_a_id)
        tea_b = self.db.get_tea(tea_b_id)

        if not tea_a or not tea_b:
            raise ValueError(f"Tea not found: {tea_a_id} or {tea_b_id}")

        category_a = self.db.get_category(tea_a.category_id)
        category_b = self.db.get_category(tea_b.category_id)

        prompt = self._build_comparison_prompt(tea_a, tea_b, category_a, category_b)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_comparison_response(response.content[0].text)

    def generate_region_content(self, region_id: str) -> dict:
        """Generate comprehensive content for a region pillar page."""
        region = self.db.get_region(region_id)
        if not region:
            raise ValueError(f"Region not found: {region_id}")

        teas = self.db.get_teas_by_region(region_id)
        child_regions = self.db.get_child_regions(region_id)

        prompt = self._build_region_prompt(region, teas, child_regions)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_content_response(response.content[0].text)

    def _build_category_prompt(self, category, teas, subcategories) -> str:
        """Build prompt for category content generation."""
        tea_names = [t.name_en for t in teas[:20]]
        sub_names = [s.name_en for s in subcategories]

        return f"""Write comprehensive, SEO-optimized content for a Chinese tea category page about {category.name_en} ({category.name_zh if category.name_zh else ''}).

Category Description: {category.description}
Oxidation Range: {category.oxidation_range_min * 100:.0f}%-{category.oxidation_range_max * 100:.0f}%
Subcategories: {', '.join(sub_names) if sub_names else 'None'}
Example Teas: {', '.join(tea_names)}

Generate the following sections in JSON format:
{{
    "intro": "2-3 paragraph introduction (300-400 words)",
    "history": "Historical background (200-300 words)",
    "processing": "How this tea category is processed (200-300 words)",
    "flavor_profile": "Common flavor characteristics (150-200 words)",
    "health_benefits": "Potential health benefits with disclaimers (150-200 words)",
    "brewing_tips": "General brewing recommendations (150-200 words)",
    "buying_guide": "What to look for when buying (150-200 words)",
    "faq": [
        {{"question": "...", "answer": "..."}},
        {{"question": "...", "answer": "..."}}
    ]
}}

Guidelines:
- Write for tea enthusiasts and curious beginners
- Be accurate and cite specific characteristics
- Avoid generic filler content
- Include specific tea names when relevant
- Use engaging, informative tone
- Include Chinese terms where appropriate with pinyin
"""

    def _build_comparison_prompt(self, tea_a, tea_b, category_a, category_b) -> str:
        """Build prompt for comparison content generation."""
        return f"""Write a detailed comparison between two Chinese teas:

Tea A: {tea_a.name_en} ({tea_a.name_zh if tea_a.name_zh else ''})
- Category: {category_a.name_en if category_a else tea_a.category_id}
- Region: {tea_a.region_id}
- Primary Flavors: {', '.join(tea_a.flavor_primary) if tea_a.flavor_primary else 'Various'}
- Oxidation: {tea_a.oxidation_level * 100 if tea_a.oxidation_level else '?'}%
- Body: {tea_a.body.value if tea_a.body else 'Medium'}
- Description: {tea_a.description_brief}

Tea B: {tea_b.name_en} ({tea_b.name_zh if tea_b.name_zh else ''})
- Category: {category_b.name_en if category_b else tea_b.category_id}
- Region: {tea_b.region_id}
- Primary Flavors: {', '.join(tea_b.flavor_primary) if tea_b.flavor_primary else 'Various'}
- Oxidation: {tea_b.oxidation_level * 100 if tea_b.oxidation_level else '?'}%
- Body: {tea_b.body.value if tea_b.body else 'Medium'}
- Description: {tea_b.description_brief}

Generate comparison content in JSON format:
{{
    "verdict": "2-3 sentence summary of key differences and which to choose when (50-80 words)",
    "flavor_comparison": "Detailed flavor comparison (100-150 words)",
    "brewing_comparison": "How brewing differs (80-100 words)",
    "price_comparison": "Value considerations (50-80 words)",
    "key_differences": ["difference 1", "difference 2", "difference 3"],
    "key_similarities": ["similarity 1", "similarity 2"]
}}

Guidelines:
- Be specific about flavor differences
- Recommend which tea for which occasions
- Maintain objectivity - both teas have merits
- Help readers make informed choices
"""

    def _build_region_prompt(self, region, teas, child_regions) -> str:
        """Build prompt for region content generation."""
        tea_names = [t.name_en for t in teas[:15]]
        child_names = [r.name_en for r in child_regions]

        return f"""Write comprehensive content for a Chinese tea region page about {region.name_en} ({region.name_zh if region.name_zh else ''}).

Region Type: {region.region_type.value}
Terroir: {region.terroir_notes if region.terroir_notes else 'Varied terrain'}
Climate: {region.climate if region.climate else 'Subtropical/varied'}
Elevation: {region.elevation_min_m or '?'}-{region.elevation_max_m or '?'}m
Sub-regions: {', '.join(child_names) if child_names else 'None'}
Famous Teas: {', '.join(tea_names)}

Generate content in JSON format:
{{
    "intro": "Introduction to the tea region (200-300 words)",
    "history": "Tea cultivation history (200-250 words)",
    "terroir": "Detailed terroir characteristics (150-200 words)",
    "famous_teas": "Overview of notable teas (150-200 words)",
    "visiting": "Brief tourism info if applicable (100-150 words)",
    "faq": [
        {{"question": "...", "answer": "..."}},
        {{"question": "...", "answer": "..."}}
    ]
}}

Guidelines:
- Highlight what makes this region unique
- Connect terroir to tea characteristics
- Include specific geographical details
- Mention notable tea gardens or mountains
"""

    def _parse_content_response(self, response_text: str) -> dict:
        """Parse JSON response from content generation."""
        # Try to extract JSON from response
        try:
            # Handle potential markdown code blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError) as e:
            return {"raw_content": response_text, "parse_error": str(e)}

    def _parse_comparison_response(self, response_text: str) -> dict:
        """Parse comparison response."""
        return self._parse_content_response(response_text)

    def batch_generate_comparisons(
        self,
        comparison_ids: list[str],
        output_file: Path
    ) -> dict:
        """Generate narratives for multiple comparisons and save to file."""
        results = {}
        errors = []

        comparisons = self.db.get_all_comparisons()
        comp_map = {c.id: c for c in comparisons}

        for comp_id in comparison_ids:
            comp = comp_map.get(comp_id)
            if not comp:
                errors.append(f"Comparison not found: {comp_id}")
                continue

            try:
                narrative = self.generate_comparison_narrative(
                    comp.tea_a_id,
                    comp.tea_b_id
                )
                results[comp_id] = narrative
            except Exception as e:
                errors.append(f"{comp_id}: {str(e)}")

        # Save results
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump({
                "generated_at": str(Path(__file__).stat().st_mtime),
                "count": len(results),
                "narratives": results,
                "errors": errors
            }, f, indent=2)

        return {"generated": len(results), "errors": len(errors)}


def load_curated_content(content_dir: Path) -> dict:
    """Load curated/generated content from JSON files."""
    content = {
        "pillars": {},
        "comparisons": {},
    }

    pillar_file = content_dir / "pillar_content.json"
    if pillar_file.exists():
        with open(pillar_file) as f:
            content["pillars"] = json.load(f)

    comparison_file = content_dir / "comparison_narratives.json"
    if comparison_file.exists():
        with open(comparison_file) as f:
            data = json.load(f)
            content["comparisons"] = data.get("narratives", {})

    return content
