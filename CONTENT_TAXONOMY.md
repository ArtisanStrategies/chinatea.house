# Content Taxonomy: chinatea.house

## Hub/Spoke Architecture

```
                                    ┌─────────────────┐
                                    │   HOMEPAGE      │
                                    │ chinatea.house  │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
            ┌───────▼───────┐       ┌───────▼───────┐       ┌───────▼───────┐
            │  TEA TYPES    │       │   REGIONS     │       │   LEARN       │
            │   (hub)       │       │    (hub)      │       │    (hub)      │
            └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
                    │                       │                       │
        ┌───────────┼───────────┐          ...                     ...
        │           │           │
   ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
   │ Green   │ │ Oolong  │ │ Pu-erh  │  ← Category Pillars
   │ (pillar)│ │ (pillar)│ │ (pillar)│
   └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │
   ┌────▼────┐     ...         ...
   │Longjing │                          ← Tea Detail Pages (satellites)
   │Biluochun│
   │Maofeng  │
   └─────────┘
```

---

## Level 0: Homepage

**URL:** `/`
**Purpose:** Site entry, navigation hub, featured content
**Links to:** All Level 1 hubs

---

## Level 1: Primary Hubs

### Hub 1: Tea Types (`/tea/`)
**Purpose:** Entry point to tea categories
**Content:** Overview of 6+1 tea types, how they differ, what to try first

**Links to:**
- `/tea/green/` — Green tea pillar
- `/tea/white/` — White tea pillar
- `/tea/yellow/` — Yellow tea pillar
- `/tea/oolong/` — Oolong tea pillar
- `/tea/black/` — Black (red) tea pillar
- `/tea/dark/` — Dark tea (pu-erh) pillar
- `/tea/scented/` — Scented/flavored tea pillar

### Hub 2: Regions (`/regions/`)
**Purpose:** Geographic exploration of tea origins
**Content:** Overview of tea-producing provinces, famous mountains

**Links to:**
- `/regions/yunnan/` — Yunnan province pillar
- `/regions/fujian/` — Fujian province pillar
- `/regions/zhejiang/` — Zhejiang province pillar
- `/regions/anhui/` — Anhui province pillar
- `/regions/guangdong/` — Guangdong province pillar
- `/regions/sichuan/` — Sichuan province pillar
- `/regions/taiwan/` — Taiwan pillar
- (etc.)

### Hub 3: Learn (`/learn/`)
**Purpose:** Educational content hub
**Content:** Starting points for different learning paths

**Links to:**
- `/learn/beginners/` — Beginner's guide pillar
- `/learn/brewing/` — Brewing methods pillar
- `/learn/gongfu/` — Gongfu ceremony pillar
- `/learn/teaware/` — Teaware guide pillar
- `/learn/tasting/` — How to taste tea pillar
- `/learn/storage/` — Tea storage pillar
- `/learn/history/` — History of Chinese tea pillar

### Hub 4: Compare (`/compare/`)
**Purpose:** Comparison content hub
**Content:** How to compare teas, featured comparisons

**Links to:**
- `/compare/oolong/` — Oolong comparisons index
- `/compare/puerh/` — Pu-erh comparisons index
- `/compare/green/` — Green tea comparisons index
- (Individual comparison pages)

### Hub 5: Teaware (`/teaware/`)
**Purpose:** Equipment and accessories
**Content:** Overview of teaware types, what you need

**Links to:**
- `/teaware/gaiwan/` — Gaiwan guide pillar
- `/teaware/yixing/` — Yixing teapot pillar
- `/teaware/cups/` — Tea cups guide
- `/teaware/accessories/` — Accessories guide

---

## Level 2: Category Pillars

### Tea Type Pillars (7 pages)

**URL pattern:** `/tea/[category]/`
**Word count:** 2,000-3,000 words
**Content structure:**
1. What is [category] tea?
2. How [category] tea is made (processing)
3. Flavor profile overview
4. Famous [category] teas (top 10)
5. Regions known for [category]
6. How to brew [category] tea
7. Health benefits
8. Buying guide
9. FAQ

**Example:** `/tea/oolong/`
- Links UP to: `/tea/`
- Links DOWN to: All oolong variety pages
- Links ACROSS to: `/learn/brewing/`, `/compare/oolong/`

### Region Pillars (~15 pages)

**URL pattern:** `/regions/[province]/`
**Word count:** 1,500-2,500 words
**Content structure:**
1. Overview of [province] tea history
2. Climate and terroir
3. Famous tea-producing areas
4. Signature teas from [province]
5. Notable tea mountains
6. Visiting tea country (if applicable)

**Example:** `/regions/fujian/`
- Links UP to: `/regions/`
- Links DOWN to: Wuyi, Anxi, Fuding sub-region pages
- Links ACROSS to: Relevant tea variety pages

### Learning Pillars (~10 pages)

**URL pattern:** `/learn/[topic]/`
**Word count:** 2,000-3,000 words
**Content:** Comprehensive guides on brewing, tasting, teaware, etc.

---

## Level 3: Sub-Category Pages

### Tea Sub-Categories

**URL pattern:** `/tea/[category]/[subcategory]/`
**Word count:** 1,000-1,500 words

**Examples:**
- `/tea/oolong/wuyi/` — Wuyi rock oolongs
- `/tea/oolong/anxi/` — Anxi oolongs
- `/tea/oolong/phoenix/` — Phoenix (dancong) oolongs
- `/tea/oolong/taiwan/` — Taiwanese oolongs
- `/tea/dark/sheng/` — Raw pu-erh
- `/tea/dark/shou/` — Ripe pu-erh

### Region Sub-Areas

**URL pattern:** `/regions/[province]/[area]/`
**Word count:** 800-1,200 words

**Examples:**
- `/regions/yunnan/xishuangbanna/` — Xishuangbanna tea region
- `/regions/fujian/wuyi-mountains/` — Wuyi Mountain detail
- `/regions/zhejiang/west-lake/` — West Lake (Longjing origin)

---

## Level 4: Individual Tea Pages (Satellites)

### Tea Variety Pages (~600 pages)

**URL pattern:** `/tea/[category]/[tea-name]/`
**Word count:** 600-1,000 words
**Template-driven:** Yes (with variable insertion)

**Content structure:**
1. Overview (2-3 sentences)
2. Quick facts table (origin, category, oxidation, caffeine)
3. Flavor profile
4. How to brew (with specific parameters)
5. What to look for when buying
6. Similar teas (internal links)
7. Where to buy (future affiliate/e-commerce)

**Examples:**
- `/tea/oolong/da-hong-pao/`
- `/tea/oolong/tieguanyin/`
- `/tea/green/longjing/`
- `/tea/dark/lao-ban-zhang/`

### Brewing Guide Pages (~3,000 pages)

**URL pattern:** `/tea/[category]/[tea-name]/brewing/` or `/brew/[tea-name]-[method]/`
**Word count:** 400-600 words
**Template-driven:** Yes

**Content structure:**
1. Quick reference table (temp, ratio, time)
2. Gongfu method
3. Western method
4. Tips for this specific tea
5. Common mistakes

**Examples:**
- `/tea/oolong/da-hong-pao/brewing/`
- `/brew/longjing-gongfu/`
- `/brew/shou-puerh-western/`

---

## Level 5: Comparison Pages (Satellites)

### Tea vs Tea Pages (~15,000 pages)

**URL pattern:** `/compare/[tea-a]-vs-[tea-b]/`
**Word count:** 500-800 words
**Template-driven:** Yes

**Content structure:**
1. Quick comparison table
2. Origins compared
3. Flavor profiles compared
4. Brewing differences
5. Price comparison
6. Which should you try?
7. FAQ (2-3 questions)

**Pairing logic:**
- Same category comparisons (da hong pao vs shui xian)
- Cross-category comparisons (tieguanyin vs longjing)
- Famous pairs (sheng vs shou puerh)
- Never: nonsensical pairs (random green vs random black)

**Examples:**
- `/compare/da-hong-pao-vs-tieguanyin/`
- `/compare/longjing-vs-biluochun/`
- `/compare/sheng-puerh-vs-shou-puerh/`

---

## Level 5: Occasion/Benefit Pages (Satellites)

### Best Tea For Pages (~2,000 pages)

**URL pattern:** `/best/tea-for-[occasion]/` or `/best/[category]-for-[occasion]/`
**Word count:** 600-900 words
**Template-driven:** Yes

**Content structure:**
1. Why [occasion] matters for tea choice
2. Top 5 recommendations (with links)
3. What to avoid
4. Brewing tips for [occasion]

**Examples:**
- `/best/tea-for-focus/`
- `/best/tea-for-sleep/`
- `/best/tea-for-digestion/`
- `/best/oolong-for-beginners/`
- `/best/puerh-for-weight-loss/`

---

## Level 5: Informational Pages (Satellites)

### [Tea] + Attribute Pages (~6,000 pages)

**URL patterns:**
- `/tea/[category]/[tea]/caffeine/`
- `/tea/[category]/[tea]/benefits/`
- `/tea/[category]/[tea]/price-guide/`
- `/tea/[category]/[tea]/storage/`

**Word count:** 300-500 words
**Template-driven:** Yes

---

## Teaware Pages

### Teaware Type Pages (~50 pages)

**URL pattern:** `/teaware/[type]/`
**Word count:** 800-1,200 words

**Examples:**
- `/teaware/gaiwan/`
- `/teaware/yixing/`
- `/teaware/cha-hai/`
- `/teaware/tea-pets/`

### Teaware + Tea Pairing Pages (~500 pages)

**URL pattern:** `/teaware/[type]/for-[tea-category]/`
**Word count:** 400-600 words
**Template-driven:** Yes

**Examples:**
- `/teaware/yixing/for-puerh/`
- `/teaware/gaiwan/for-oolong/`

---

## Internal Linking Strategy

### Vertical Links (Hub → Spoke)
- Every page links UP to its parent
- Every hub/pillar links DOWN to its children

### Horizontal Links (Spoke ↔ Spoke)
- Tea pages link to related teas (same category, same region)
- Comparison pages link to both teas being compared
- Brewing pages link to the main tea page
- Occasion pages link to all recommended teas

### Cross-Pillar Links
- Tea pages link to relevant region pages
- Region pages link to teas from that region
- Teaware pages link to teas they're suited for
- Learning pages link to relevant examples

### Link Density Targets
- Pillar pages: 20-50 internal links
- Satellite pages: 5-15 internal links
- No orphan pages (every page reachable from navigation)

---

## Page Count Summary

| Level | Type | Count |
|-------|------|-------|
| 0 | Homepage | 1 |
| 1 | Primary hubs | 5 |
| 2 | Category pillars | ~35 |
| 3 | Sub-category pages | ~100 |
| 4 | Individual tea pages | ~600 |
| 4 | Brewing guide pages | ~3,000 |
| 5 | Comparison pages | ~15,000 |
| 5 | Occasion/benefit pages | ~2,000 |
| 5 | Attribute pages | ~6,000 |
| - | Teaware pages | ~550 |
| - | Region detail pages | ~200 |

**Total estimated pages:** ~27,500 (conservative) to ~75,000+ (with full expansion)

---

## Template Requirements

| Template | Usage | Variables |
|----------|-------|-----------|
| `pillar.html` | Category/learning pillars | title, content, children[], related[] |
| `tea-detail.html` | Individual teas | tea{}, brewing{}, similar[], buy_links[] |
| `comparison.html` | Tea vs tea | tea_a{}, tea_b{}, comparison{} |
| `occasion.html` | Best for X | occasion{}, recommendations[], tips |
| `attribute.html` | Caffeine/benefits/price | tea{}, attribute_type, data{} |
| `brewing.html` | Brewing guides | tea{}, methods[], tips[] |
| `teaware.html` | Equipment pages | item{}, suitable_teas[], care{} |
| `region.html` | Geographic pages | region{}, teas[], subregions[] |
