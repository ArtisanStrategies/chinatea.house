"""
AI-powered content generation agent.

Generates high-quality content for pillar pages and comparisons.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None


@dataclass
class GeneratedContent:
    """Generated content result."""
    entity_type: str  # 'pillar', 'comparison', 'tea'
    entity_id: str
    sections: dict[str, str]
    word_count: int
    needs_review: bool


class ContentGenerationAgent:
    """
    AI agent that generates content for the site.

    Handles pillar pages, comparison narratives, and tea descriptions.
    """

    PILLAR_PROMPT = """You are writing content for a Chinese tea educational website.

Write engaging, SEO-friendly content for the {category_name} tea category page.

Include these sections:
1. **Introduction** (150-200 words): What is {category_name} tea? Brief overview.
2. **History** (200-300 words): Origins and cultural significance in China.
3. **Processing** (150-200 words): How {category_name} tea is made.
4. **Characteristics** (150-200 words): Key flavor profiles, appearance, aroma.
5. **Health Benefits** (100-150 words): Traditional and researched benefits.
6. **How to Choose** (100-150 words): Tips for selecting quality tea.
7. **Brewing Guide** (150-200 words): Basic brewing recommendations.

Use a conversational but authoritative tone. Include specific examples.
Target audience: Western tea enthusiasts, beginners to intermediate.

Return as JSON:
{{
    "intro": "...",
    "history": "...",
    "processing": "...",
    "characteristics": "...",
    "health_benefits": "...",
    "how_to_choose": "...",
    "brewing_guide": "..."
}}"""

    COMPARISON_PROMPT = """You are writing a comparison article for a Chinese tea website.

Compare these two teas:
- **{tea_a_name}** ({tea_a_category}): {tea_a_desc}
- **{tea_b_name}** ({tea_b_category}): {tea_b_desc}

Write an engaging comparison covering:
1. **Introduction** (50-100 words): Why compare these teas?
2. **Flavor Comparison** (150-200 words): Detailed taste profiles side by side.
3. **Brewing Comparison** (100-150 words): How brewing differs.
4. **Price & Value** (75-100 words): Value proposition of each.
5. **Verdict** (50-75 words): When to choose each tea.

Target audience: Tea enthusiasts deciding between these options.

Return as JSON:
{{
    "intro": "...",
    "flavor_comparison": "...",
    "brewing_comparison": "...",
    "price_comparison": "...",
    "verdict": "..."
}}"""

    TEA_DESCRIPTION_PROMPT = """You are writing a product description for {tea_name} ({tea_category}).

Region: {region}
Flavor profile: {flavors}
Oxidation: {oxidation}%

Write a compelling 150-250 word description that:
- Opens with a memorable hook about this tea
- Describes the sensory experience (aroma, taste, mouthfeel)
- Mentions traditional significance or unique characteristics
- Suggests ideal drinking occasions

Target: Western tea enthusiasts.

Return ONLY the description text, no JSON formatting."""

    def __init__(
        self,
        backend: str = "anthropic",
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None
    ):
        self.backend = backend
        self.model = model

        if backend == "anthropic":
            if anthropic is None:
                raise ImportError("anthropic package not installed")
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        elif backend == "openrouter":
            if openai is None:
                raise ImportError("openai package not installed")
            self.client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key or os.getenv("OPENROUTER_API_KEY")
            )
        elif backend == "kimi":
            if openai is None:
                raise ImportError("openai package not installed")
            resolved_api_key = api_key or os.getenv("KIMI_API_KEY")
            if not resolved_api_key:
                raise ValueError("KIMI_API_KEY is required for the kimi backend")
            self.client = openai.OpenAI(
                base_url="https://api.moonshot.ai/v1",
                api_key=resolved_api_key
            )
            # Default to kimi-k2-turbo-preview if no model specified
            if model == "claude-sonnet-4-20250514":
                self.model = "kimi-k2-0905-preview"
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def generate_pillar_content(self, category_name: str) -> GeneratedContent:
        """Generate content for a category pillar page."""
        prompt = self.PILLAR_PROMPT.format(category_name=category_name)
        response = self._query(prompt)

        try:
            response = self._clean_json(response)
            sections = json.loads(response)
            word_count = sum(len(s.split()) for s in sections.values())

            return GeneratedContent(
                entity_type="pillar",
                entity_id=category_name.lower().replace(" ", "-"),
                sections=sections,
                word_count=word_count,
                needs_review=word_count < 800
            )
        except json.JSONDecodeError:
            return GeneratedContent(
                entity_type="pillar",
                entity_id=category_name.lower().replace(" ", "-"),
                sections={"error": "Failed to parse", "raw": response},
                word_count=0,
                needs_review=True
            )

    def generate_comparison_content(
        self,
        tea_a: dict,
        tea_b: dict
    ) -> GeneratedContent:
        """Generate narrative content for a comparison page."""
        prompt = self.COMPARISON_PROMPT.format(
            tea_a_name=tea_a.get("name_en", "Tea A"),
            tea_a_category=tea_a.get("category_id", "unknown"),
            tea_a_desc=tea_a.get("description_brief", "A Chinese tea."),
            tea_b_name=tea_b.get("name_en", "Tea B"),
            tea_b_category=tea_b.get("category_id", "unknown"),
            tea_b_desc=tea_b.get("description_brief", "A Chinese tea.")
        )

        response = self._query(prompt)

        try:
            response = self._clean_json(response)
            sections = json.loads(response)
            word_count = sum(len(s.split()) for s in sections.values())

            return GeneratedContent(
                entity_type="comparison",
                entity_id=f"{tea_a.get('id', 'a')}-vs-{tea_b.get('id', 'b')}",
                sections=sections,
                word_count=word_count,
                needs_review=word_count < 300
            )
        except json.JSONDecodeError:
            return GeneratedContent(
                entity_type="comparison",
                entity_id=f"{tea_a.get('id', 'a')}-vs-{tea_b.get('id', 'b')}",
                sections={"error": "Failed to parse", "raw": response},
                word_count=0,
                needs_review=True
            )

    def generate_tea_description(self, tea: dict) -> str:
        """Generate an enhanced description for a tea."""
        flavors = ", ".join(tea.get("flavor_primary", [])[:4])
        oxidation = int((tea.get("oxidation_level", 0.5) or 0.5) * 100)

        prompt = self.TEA_DESCRIPTION_PROMPT.format(
            tea_name=tea.get("name_en", "Tea"),
            tea_category=tea.get("category_id", "tea"),
            region=tea.get("region_id", "China"),
            flavors=flavors or "complex",
            oxidation=oxidation
        )

        return self._query(prompt)

    def identify_content_gaps(self, db_path: Path) -> dict:
        """
        Identify content gaps in the database.

        Returns dict with lists of entities needing content.
        """
        import sqlite3

        gaps = {
            "pillars_without_content": [],
            "comparisons_without_narrative": [],
            "teas_with_short_descriptions": []
        }

        conn = sqlite3.connect(db_path)
        try:
            # Categories without pillar content
            cursor = conn.execute("""
                SELECT c.id, c.name_en
                FROM categories c
                LEFT JOIN pillar_content pc
                    ON pc.page_type = 'category' AND pc.entity_id = c.id
                WHERE pc.entity_id IS NULL
            """)
            for row in cursor:
                gaps["pillars_without_content"].append({
                    "id": row[0], "name": row[1]
                })

            # Top comparisons without narrative
            cursor = conn.execute("""
                SELECT cp.id, t1.name_en, t2.name_en, cp.relevance_score
                FROM comparison_pairs cp
                JOIN teas t1 ON cp.tea_a_id = t1.id
                JOIN teas t2 ON cp.tea_b_id = t2.id
                LEFT JOIN comparison_content cc ON cp.id = cc.comparison_id
                WHERE cc.comparison_id IS NULL
                    AND cp.relevance_score > 0.7
                ORDER BY cp.relevance_score DESC
                LIMIT 100
            """)
            for row in cursor:
                gaps["comparisons_without_narrative"].append({
                    "id": row[0],
                    "tea_a": row[1],
                    "tea_b": row[2],
                    "score": row[3]
                })

            # Teas with short descriptions
            cursor = conn.execute("""
                SELECT id, name_en, description_brief
                FROM teas
                WHERE length(description_brief) < 100
            """)
            for row in cursor:
                gaps["teas_with_short_descriptions"].append({
                    "id": row[0],
                    "name": row[1],
                    "current_length": len(row[2]) if row[2] else 0
                })

        finally:
            conn.close()

        return gaps

    def _query(self, prompt: str) -> str:
        """Query the AI backend."""
        if self.backend == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        else:
            # OpenAI-compatible APIs (OpenRouter, Kimi, etc.)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.choices[0].message.content

    def _clean_json(self, text: str) -> str:
        """Clean up JSON response that might have markdown formatting."""
        text = text.strip()
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]
        return text.strip()
