# Data Acquisition Plan: chinatea.house

## Overview

We need structured data to power 50,000+ pages. This plan outlines how we'll acquire, structure, and maintain that data.

**Core principle:** Build once, generate many. A well-structured tea database enables automatic generation of:
- Individual tea pages
- Comparison pages (tea A vs tea B)
- Brewing guides
- Occasion/benefit pages
- Regional pages

---

## Data Schema (Target State)

### Primary Entity: Tea

```json
{
  "id": "da-hong-pao",
  "name": {
    "english": "Da Hong Pao",
    "chinese": "大红袍",
    "pinyin": "dà hóng páo",
    "aliases": ["Big Red Robe", "DHP"]
  },
  "category": "oolong",
  "subcategory": "wuyi-rock",
  "oxidation_level": 0.7,
  "roast_level": "medium-heavy",
  "caffeine_level": "medium-high",
  "region": {
    "country": "china",
    "province": "fujian",
    "area": "wuyi-mountains",
    "specific": "zhengyan-core"
  },
  "flavor_profile": {
    "primary": ["roasted", "mineral", "stone-fruit"],
    "secondary": ["cocoa", "caramel", "orchid"],
    "body": "full",
    "finish": "long"
  },
  "brewing": {
    "gongfu": {
      "temp_c": 95,
      "ratio_g_per_100ml": 6,
      "first_steep_seconds": 10,
      "steep_increment": 5,
      "max_steeps": 8
    },
    "western": {
      "temp_c": 90,
      "ratio_g_per_250ml": 3,
      "steep_minutes": 3
    }
  },
  "price_range": {
    "budget_usd_per_50g": [5, 15],
    "mid_usd_per_50g": [15, 40],
    "premium_usd_per_50g": [40, 150],
    "collector_usd_per_50g": [150, null]
  },
  "best_for": ["after-meals", "cold-weather", "meditation", "connoisseurs"],
  "similar_teas": ["shui-xian", "rou-gui", "bei-dou"],
  "description_brief": "The most famous Wuyi rock oolong, known for its mineral 'rock rhyme' and complex roasted character.",
  "history": "Legend traces Da Hong Pao to the Ming Dynasty...",
  "sourcing_notes": "True zhengyan (core mountain) DHP is rare; most commercial versions are excellent but from outer mountain areas.",
  "metadata": {
    "created": "2024-01-15",
    "updated": "2024-01-20",
    "sources": ["babelcarp", "yunnan-sourcing", "white2tea"],
    "confidence": 0.9
  }
}
```

### Secondary Entities

**Region:**
```json
{
  "id": "wuyi-mountains",
  "name": { "english": "Wuyi Mountains", "chinese": "武夷山" },
  "parent": "fujian",
  "type": "mountain-range",
  "famous_for": ["rock-oolong", "yan-cha"],
  "terroir": "Rocky cliffs, mineral-rich soil, misty climate",
  "notable_teas": ["da-hong-pao", "rou-gui", "shui-xian", "bei-dou"],
  "sub_areas": ["zhengyan-core", "banyan-half-rock", "waishan-outer"]
}
```

**Teaware:**
```json
{
  "id": "yixing-zisha",
  "name": { "english": "Yixing Purple Clay Teapot", "chinese": "宜兴紫砂壶" },
  "type": "teapot",
  "materials": ["zisha-clay"],
  "best_for_categories": ["oolong", "dark", "black"],
  "care_instructions": "...",
  "price_range": { "budget": [20, 50], "mid": [50, 200], "premium": [200, 1000] }
}
```

**Brewing Method:**
```json
{
  "id": "gongfu",
  "name": { "english": "Gongfu Style", "chinese": "功夫茶" },
  "equipment_required": ["gaiwan-or-teapot", "cha-hai", "cups"],
  "equipment_optional": ["tea-tray", "tea-tools", "kettle"],
  "general_principles": "High leaf ratio, short steeps, multiple infusions",
  "suitable_for": ["oolong", "dark", "black", "white-aged"]
}
```

**Occasion/Benefit:**
```json
{
  "id": "focus",
  "type": "occasion",
  "name": "Mental Focus",
  "description": "Teas that promote alertness and concentration",
  "preferred_attributes": {
    "caffeine_level": ["medium", "medium-high", "high"],
    "l_theanine": "present",
    "flavor_profile": "not-too-relaxing"
  },
  "recommended_teas": ["gyokuro", "longjing", "tieguanyin", "young-sheng"],
  "teas_to_avoid": ["chamomile", "aged-shou", "heavily-roasted"]
}
```

---

## Data Sources

### Source 1: Babelcarp (Tea Terminology Dictionary)

**What it provides:**
- Chinese-English tea terminology
- Tea names with characters and pinyin
- Processing terms
- Regional names

**Acquisition method:**
- Parse website content
- Structure into terminology database

**Output:** `data/raw/babelcarp_terms.json`

**Legal consideration:** Educational use, attribution provided. Fair use for terminology.

---

### Source 2: Vendor Catalogs

**Primary vendors:**
- Yunnan Sourcing (largest pu-erh catalog)
- white2tea (curated pu-erh/oolong)
- Crimson Lotus (pu-erh specialist)
- Taiwan Sourcing (Taiwanese oolong)
- Essence of Tea (aged teas)
- Mei Leaf (accessible education focus)

**What they provide:**
- Tea names and categorization
- Origin information
- Flavor descriptions (for reference, not copying)
- Brewing parameters
- Price points

**Acquisition method:**
- Manual review and data extraction
- Use as reference for our original descriptions
- DO NOT copy product descriptions verbatim

**Output:** `data/raw/vendor_reference.json`

**Legal consideration:** Extract facts (names, origins, parameters), write original descriptions. Facts are not copyrightable.

---

### Source 3: Wikipedia / Baidu Baike

**What they provide:**
- Tea variety lists
- Historical information
- Regional information
- Processing descriptions

**Acquisition method:**
- Parse structured data (infoboxes, lists)
- Use as research starting point
- Verify and expand with other sources

**Output:** `data/raw/wiki_teas.json`

**Legal consideration:** CC-licensed content, attribute appropriately.

---

### Source 4: Academic Sources

**What they provide:**
- Chemical composition data (caffeine, catechins, etc.)
- Health benefit evidence
- Processing science
- Regional tea surveys

**Key sources:**
- Journal of Agricultural and Food Chemistry
- Food Chemistry
- Chinese tea research institutes

**Acquisition method:**
- Manual research for pillar content
- Extract verifiable data points
- Cite sources properly

**Output:** `data/raw/academic_data.json`

---

### Source 5: Manual Curation (Your Expertise)

**What you provide:**
- Quality tiers and recommendations
- Tasting notes and descriptions
- Sourcing guidance
- Personal experience data

**Acquisition method:**
- Structured input forms/templates
- Review and approval of generated content
- Ongoing enrichment

**Output:** `data/curated/expert_notes.json`

---

### Source 6: Community Knowledge (Reddit, Forums)

**What they provide:**
- Common questions (FAQ fodder)
- Community recommendations
- Price expectations
- Vendor reviews

**Acquisition method:**
- Read and synthesize (no scraping)
- Use for keyword ideas and content gaps
- Reference community consensus

**Legal consideration:** Inspiration only, no direct copying of user content.

---

## Data Pipeline

### Phase 1: Core Taxonomy (Week 1-2)

**Goal:** Build the skeleton—categories, subcategories, regions, without full detail.

```
Step 1: Define category hierarchy
  /tea/
    /green/ (7 subcategories)
    /white/ (4 subcategories)
    /yellow/ (2 subcategories)
    /oolong/ (6 subcategories)
    /black/ (5 subcategories)
    /dark/ (3 subcategories)
    /scented/ (4 subcategories)

Step 2: Define region hierarchy
  /regions/
    /yunnan/ (8 sub-areas)
    /fujian/ (6 sub-areas)
    /zhejiang/ (3 sub-areas)
    ... etc

Step 3: Define entity relationships
  - tea → category (many-to-one)
  - tea → region (many-to-one, some many-to-many)
  - tea → similar_teas (many-to-many)
  - tea → occasions (many-to-many)
  - teaware → suitable_categories (many-to-many)
```

**Output:** `data/canonical/taxonomy.json`

---

### Phase 2: Tea Entity Population (Week 2-4)

**Goal:** Populate 600+ individual tea records.

**Process:**
1. Start with "famous teas" lists (Ten Famous Teas, etc.)
2. Expand with vendor catalog teas
3. Add regional specialties
4. Fill in data fields progressively

**Prioritization:**
- Tier 1 (Week 2): Top 50 most-searched teas
- Tier 2 (Week 3): Next 150 well-known teas
- Tier 3 (Week 4): Remaining 400+ teas

**Quality gates:**
- Every tea must have: name, category, region, brief description
- 80% should have: brewing parameters, flavor profile
- 50% should have: price range, sourcing notes

---

### Phase 3: Relationship Mapping (Week 4-5)

**Goal:** Build the connections that power comparison and recommendation pages.

**Similarity matrix:**
- Define which teas are comparable (same category, similar profile)
- Generate valid comparison pairs
- Exclude nonsensical comparisons

**Occasion mapping:**
- Map teas to occasions/benefits
- Use attribute matching + manual curation
- Generate "best tea for X" candidate lists

**Regional connections:**
- Link teas to origin regions
- Link regions to parent regions
- Enable geographic navigation

---

### Phase 4: Content Generation Inputs (Week 5-6)

**Goal:** Prepare data structures that feed directly into templates.

**For each tea, generate:**
```json
{
  "tea_id": "da-hong-pao",
  "page_data": {
    "title": "Da Hong Pao Tea: Complete Guide to Big Red Robe Oolong",
    "meta_description": "Everything about Da Hong Pao...",
    "h1": "Da Hong Pao (Big Red Robe)",
    "quick_facts": {...},
    "body_sections": [...],
    "internal_links": [...],
    "schema_markup": {...}
  }
}
```

**For each comparison pair:**
```json
{
  "comparison_id": "da-hong-pao-vs-tieguanyin",
  "tea_a": "da-hong-pao",
  "tea_b": "tieguanyin",
  "comparison_data": {
    "title": "Da Hong Pao vs Tieguanyin: Which Oolong Should You Try?",
    "comparison_table": {...},
    "key_differences": [...],
    "recommendation": "..."
  }
}
```

---

## Data Validation

### Schema Validation

Every record must pass JSON schema validation:
- Required fields present
- Field types correct
- Enum values valid
- Relationships reference existing entities

### Quality Validation

Automated checks:
- No duplicate tea IDs
- All referenced teas exist
- All referenced regions exist
- Brewing temps in valid range (60-100°C)
- Price ranges logical (budget < mid < premium)

Manual review:
- Spot-check descriptions for accuracy
- Verify brewing parameters against sources
- Review AI-generated content for hallucinations

### Uniqueness Validation

For template-generated pages:
- Calculate text similarity between pages in same template family
- Flag pages with >40% similarity to neighbors
- Require differentiation (more data points, longer descriptions)

---

## Data Maintenance

### Update Triggers

| Trigger | Action |
|---------|--------|
| New tea discovered | Add to database, generate pages |
| Price changes | Update price_range fields |
| New vendor | Add to sourcing_notes |
| Error reported | Investigate, correct, log |
| Seasonal | Update "best for season" attributes |

### Versioning

- Git version control for all data files
- Changelog for significant updates
- Ability to rollback data changes

### Enrichment Roadmap

**Month 1-3:** Core data complete
**Month 4-6:** Add depth (history, sourcing notes, expert commentary)
**Month 7-12:** Add UGC layer (user tasting notes, reviews)
**Year 2:** Add vendor/product database for e-commerce

---

## File Structure

```
/data/
├── raw/                          # Source data (reference only)
│   ├── babelcarp_terms.json
│   ├── vendor_reference.json
│   ├── wiki_teas.json
│   └── academic_data.json
│
├── canonical/                    # Processed, structured data
│   ├── taxonomy.json             # Category/region hierarchy
│   ├── teas.json                 # All tea entities
│   ├── regions.json              # All region entities
│   ├── teaware.json              # All teaware entities
│   ├── occasions.json            # Occasion/benefit entities
│   ├── methods.json              # Brewing method entities
│   └── relationships.json        # Cross-entity mappings
│
├── generated/                    # Template-ready data
│   ├── pages/
│   │   ├── tea_pages.json
│   │   ├── comparison_pages.json
│   │   ├── occasion_pages.json
│   │   └── brewing_pages.json
│   └── sitemaps/
│       └── url_manifest.json
│
├── curated/                      # Human-reviewed content
│   ├── expert_notes.json
│   ├── featured_content.json
│   └── overrides.json            # Manual corrections
│
└── cache/                        # Temporary/computed data
    ├── similarity_matrix.json
    └── link_graph.json
```

---

## Execution Scripts

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `parse_babelcarp.py` | Extract terminology | Babelcarp website | `raw/babelcarp_terms.json` |
| `build_taxonomy.py` | Create hierarchy | Manual input + research | `canonical/taxonomy.json` |
| `populate_teas.py` | Create tea records | Multiple sources | `canonical/teas.json` |
| `map_relationships.py` | Build connections | `canonical/*.json` | `canonical/relationships.json` |
| `generate_page_data.py` | Prepare for templates | `canonical/*.json` | `generated/pages/*.json` |
| `validate_data.py` | Quality checks | `canonical/*.json` | Validation report |
| `diff_data.py` | Detect changes | Old vs new canonical | Change manifest |

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tea entities | 600+ | Count of `canonical/teas.json` |
| Data completeness | >80% fields populated | Validation script |
| Validation pass rate | 100% | `validate_data.py` |
| Comparison pairs | 15,000+ valid | `relationships.json` |
| Zero duplicates | 0 | Deduplication check |
| Source attribution | 100% | Metadata audit |
