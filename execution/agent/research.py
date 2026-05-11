"""
AI-powered tea research agent.

Uses Claude/OpenRouter to research and generate data for new tea varieties,
expanding the database autonomously.
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
class ResearchResult:
    """Result of tea research."""
    tea_id: str
    tea_data: dict
    sources: list[str]
    confidence: float
    needs_review: bool


class TeaResearchAgent:
    """
    AI agent that researches new tea varieties.

    Can use either Claude (Anthropic) or OpenRouter as backend.
    """

    RESEARCH_PROMPT = """You are a Chinese tea expert. Research and provide detailed data for the tea variety: {tea_name}

Provide a JSON response with the following structure:
{{
    "id": "slug-format-id",
    "name_en": "English Name",
    "name_zh": "中文名",
    "name_pinyin": "Pīnyīn with tones",
    "category_id": "green|white|yellow|oolong|black|dark|scented",
    "subcategory_id": "optional subcategory slug",
    "region_id": "region slug from known regions",
    "oxidation_level": 0.0-1.0,
    "roast_level": "none|light|medium|medium-heavy|heavy|charcoal (for oolongs)",
    "harvest_season": "spring|summer|autumn|winter",
    "cultivar": "cultivar name if known",
    "caffeine_level": "very-low|low|moderate|high|very-high",
    "flavor_primary": ["3-5 primary flavors"],
    "flavor_secondary": ["2-4 secondary flavors"],
    "aroma": ["2-4 aroma descriptors"],
    "body": "light|light-medium|medium|medium-full|full",
    "finish": "description of aftertaste",
    "mouthfeel": "description of texture",
    "brewing_gongfu": {{
        "water_temp_c": 70-100,
        "leaf_ratio_g_per_100ml": 3-8,
        "first_steep_seconds": 10-60,
        "subsequent_steep_seconds": 8-45,
        "steep_increment_seconds": 3-15,
        "num_steeps": 3-15,
        "rinse_recommended": true|false
    }},
    "price_budget": {{"min_usd_per_50g": X, "max_usd_per_50g": Y}},
    "price_mid": {{"min_usd_per_50g": X, "max_usd_per_50g": Y}},
    "price_premium": {{"min_usd_per_50g": X, "max_usd_per_50g": Y}},
    "best_for": ["occasion-slug-1", "occasion-slug-2"],
    "similar_tea_ids": ["tea-slug-1", "tea-slug-2"],
    "description_brief": "2-3 sentence description",
    "tier": 1|2|3,
    "history": "Optional historical background",
    "sources": ["source1", "source2"]
}}

Known regions include: west-lake, dongting, huangshan, wuyi-mountains, anxi, fuding,
phoenix-mountain, yunnan, menghai, yiwu, qimen, alishan, dong-ding, etc.

Known occasions: morning-energy, afternoon-focus, evening-relaxation, meditation,
digestion, guests, summer-cooling, winter-warming, daily-drinking, special-occasion

Be accurate and factual. If uncertain about a field, omit it rather than guess.
Return ONLY valid JSON, no markdown formatting."""

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

    def research_tea(self, tea_name: str) -> ResearchResult:
        """Research a tea variety and return structured data."""
        prompt = self.RESEARCH_PROMPT.format(tea_name=tea_name)

        if self.backend == "anthropic":
            response = self._query_anthropic(prompt)
        else:
            response = self._query_openai_compat(prompt)

        # Parse response
        try:
            # Clean up response if needed
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]

            data = json.loads(response)
            sources = data.pop("sources", [])

            return ResearchResult(
                tea_id=data.get("id", tea_name.lower().replace(" ", "-")),
                tea_data=data,
                sources=sources,
                confidence=0.8 if data.get("tier") == 1 else 0.6,
                needs_review=data.get("tier", 3) >= 2
            )
        except json.JSONDecodeError as e:
            return ResearchResult(
                tea_id=tea_name.lower().replace(" ", "-"),
                tea_data={"error": str(e), "raw_response": response},
                sources=[],
                confidence=0.0,
                needs_review=True
            )

    def _query_anthropic(self, prompt: str) -> str:
        """Query Claude via Anthropic API."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _query_openai_compat(self, prompt: str) -> str:
        """Query via OpenAI-compatible API (OpenRouter, Kimi, etc.)."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        return response.choices[0].message.content

    def identify_missing_teas(self, db_path: Path) -> list[str]:
        """
        Identify famous teas that are missing from our database.

        Returns a list of tea names to research.
        """
        import sqlite3

        # List of well-known Chinese teas to check
        famous_teas = [
            # China's Ten Famous Teas
            "Xi Hu Longjing", "Dongting Biluochun", "Huangshan Maofeng",
            "Lu'an Guapian", "Xinyang Maojian", "Qimen Hongcha",
            "Da Hong Pao", "Tie Guan Yin", "Junshan Yinzhen", "Bai Hao Yinzhen",

            # Additional famous teas
            "Taiping Houkui", "Mengding Ganlu", "Enshi Yulu", "Guzhu Zisun",
            "Fenghuang Dancong", "Wuyi Shui Xian", "Wuyi Rou Gui",
            "Dongfang Meiren", "Li Shan Oolong", "Shan Lin Xi",
            "Jin Jun Mei", "Zhengshan Xiaozhong", "Dianhong Jin Hao",
            "Yiwu Sheng Pu-erh", "Bingdao Pu-erh", "Lao Banzhang",
            "Bai Mudan", "Shou Mei", "Gongmei",
            "Liu Bao", "Fu Zhuan", "Anhua Hei Cha",
            "Mo Li Hua Cha", "Gui Hua Cha", "Ju Hua Cha",

            # Regional specialties
            "Mengku Da Xue Shan", "Nannuo Mountain Pu-erh",
            "Bulang Shan Pu-erh", "Jingmai Shan Pu-erh",
            "Muzha Tie Guan Yin", "Wenshan Baozhong",
            "Mi Lan Xiang Dancong", "Ya Shi Xiang Dancong",
            "Laoshan Green", "Rizhao Green",
            "Taiwan Ruby Red", "Sun Moon Lake Black"
        ]

        # Get existing tea names from database
        conn = sqlite3.connect(db_path)
        existing = set()
        try:
            cursor = conn.execute("SELECT name_en FROM teas")
            for row in cursor:
                existing.add(row[0].lower())
        finally:
            conn.close()

        # Find missing ones
        missing = []
        for tea in famous_teas:
            if tea.lower() not in existing:
                # Check for partial matches
                found = False
                for ex in existing:
                    if tea.lower() in ex or ex in tea.lower():
                        found = True
                        break
                if not found:
                    missing.append(tea)

        return missing

    def batch_research(
        self,
        tea_names: list[str],
        max_teas: int = 10,
        delay_seconds: float = 1.0
    ) -> list[ResearchResult]:
        """Research multiple teas with rate limiting."""
        import time

        results = []
        for i, name in enumerate(tea_names[:max_teas]):
            print(f"Researching {i+1}/{min(len(tea_names), max_teas)}: {name}")
            result = self.research_tea(name)
            results.append(result)

            if i < len(tea_names) - 1:
                time.sleep(delay_seconds)

        return results
