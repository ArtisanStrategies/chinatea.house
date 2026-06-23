-- chinatea.house Database Schema
-- SQLite DDL for tea data storage

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================================================
-- CORE ENTITIES
-- ============================================================================

-- Tea categories (green, white, yellow, oolong, black, dark, scented)
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_zh TEXT,
    description TEXT NOT NULL,
    oxidation_range_min REAL NOT NULL DEFAULT 0,
    oxidation_range_max REAL NOT NULL DEFAULT 1,
    color_hex TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Subcategories (e.g., Dancong, Tieguanyin within Oolong)
CREATE TABLE IF NOT EXISTS subcategories (
    id TEXT PRIMARY KEY,
    category_id TEXT NOT NULL REFERENCES categories(id),
    name_en TEXT NOT NULL,
    name_zh TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_subcategories_category ON subcategories(category_id);

-- Geographic regions (hierarchical: country > province > prefecture > county > village/mountain)
CREATE TABLE IF NOT EXISTS regions (
    id TEXT PRIMARY KEY,
    parent_id TEXT REFERENCES regions(id),
    name_en TEXT NOT NULL,
    name_zh TEXT,
    name_pinyin TEXT,
    region_type TEXT NOT NULL CHECK (region_type IN ('country', 'province', 'prefecture', 'county', 'village', 'mountain')),
    latitude REAL,
    longitude REAL,
    elevation_min_m INTEGER,
    elevation_max_m INTEGER,
    climate TEXT,
    soil_type TEXT,
    terroir_notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_regions_parent ON regions(parent_id);
CREATE INDEX IF NOT EXISTS idx_regions_type ON regions(region_type);

-- Teas - the core entity
CREATE TABLE IF NOT EXISTS teas (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_zh TEXT,
    name_pinyin TEXT,

    -- Classification
    category_id TEXT NOT NULL REFERENCES categories(id),
    subcategory_id TEXT REFERENCES subcategories(id),
    region_id TEXT NOT NULL REFERENCES regions(id),

    -- Processing
    oxidation_level REAL CHECK (oxidation_level >= 0 AND oxidation_level <= 1),
    roast_level TEXT CHECK (roast_level IN ('none', 'light', 'medium', 'medium-heavy', 'heavy', 'charcoal')),
    is_aged INTEGER NOT NULL DEFAULT 0,
    age_years INTEGER,
    harvest_season TEXT,
    cultivar TEXT,

    -- Sensory profile
    caffeine_level TEXT CHECK (caffeine_level IN ('very-low', 'low', 'moderate', 'high', 'very-high')),
    flavor_primary TEXT,  -- JSON array
    flavor_secondary TEXT,  -- JSON array
    aroma TEXT,  -- JSON array
    body TEXT CHECK (body IN ('light', 'light-medium', 'medium', 'medium-full', 'full')),
    finish TEXT,
    mouthfeel TEXT,

    -- Brewing parameters (stored as JSON)
    brewing_gongfu TEXT,
    brewing_western TEXT,
    brewing_grandpa TEXT,
    brewing_cold TEXT,

    -- Pricing (USD per 50g, stored as JSON with min/max)
    price_budget TEXT,
    price_mid TEXT,
    price_premium TEXT,

    -- Metadata
    best_for TEXT,  -- JSON array
    description_brief TEXT NOT NULL,
    description_full TEXT,
    history TEXT,

    -- Data quality (1=complete Tier-1, 2=good Tier-2, 3=basic Tier-3)
    tier INTEGER NOT NULL DEFAULT 2 CHECK (tier >= 1 AND tier <= 3),
    sources TEXT,  -- JSON array

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_teas_category ON teas(category_id);
CREATE INDEX IF NOT EXISTS idx_teas_subcategory ON teas(subcategory_id);
CREATE INDEX IF NOT EXISTS idx_teas_region ON teas(region_id);
CREATE INDEX IF NOT EXISTS idx_teas_tier ON teas(tier);

-- Tea alternate regions (many-to-many)
CREATE TABLE IF NOT EXISTS tea_alternate_regions (
    tea_id TEXT NOT NULL REFERENCES teas(id),
    region_id TEXT NOT NULL REFERENCES regions(id),
    PRIMARY KEY (tea_id, region_id)
);

-- Teaware items
CREATE TABLE IF NOT EXISTS teaware (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_zh TEXT,
    teaware_type TEXT NOT NULL CHECK (teaware_type IN ('teapot', 'gaiwan', 'cup', 'pitcher', 'strainer', 'tray', 'kettle', 'scoop', 'pick', 'towel')),
    materials TEXT,  -- JSON array
    origin_region_id TEXT REFERENCES regions(id),
    price_range TEXT,  -- JSON with min/max
    description TEXT NOT NULL,
    best_for_categories TEXT,  -- JSON array
    care_instructions TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_teaware_type ON teaware(teaware_type);

-- Occasions (morning energy, evening relaxation, meditation, etc.)
CREATE TABLE IF NOT EXISTS occasions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    preferred_categories TEXT,  -- JSON array
    preferred_attributes TEXT,  -- JSON object
    time_of_day TEXT,
    season TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Brewing methods (gongfu, western, grandpa, cold brew, etc.)
CREATE TABLE IF NOT EXISTS brewing_methods (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_zh TEXT,
    description TEXT NOT NULL,
    equipment_required TEXT,  -- JSON array
    equipment_optional TEXT,  -- JSON array
    best_for_categories TEXT,  -- JSON array
    steps TEXT,  -- JSON array
    tips TEXT,  -- JSON array
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================================
-- RELATIONSHIP TABLES
-- ============================================================================

-- Tea to occasion mapping
CREATE TABLE IF NOT EXISTS tea_occasions (
    tea_id TEXT NOT NULL REFERENCES teas(id),
    occasion_id TEXT NOT NULL REFERENCES occasions(id),
    relevance_score REAL DEFAULT 1.0,
    PRIMARY KEY (tea_id, occasion_id)
);

CREATE INDEX IF NOT EXISTS idx_tea_occasions_occasion ON tea_occasions(occasion_id);

-- Similar teas (for internal linking)
CREATE TABLE IF NOT EXISTS tea_similar (
    tea_id TEXT NOT NULL REFERENCES teas(id),
    similar_tea_id TEXT NOT NULL REFERENCES teas(id),
    similarity_score REAL NOT NULL DEFAULT 0.5 CHECK (similarity_score >= 0 AND similarity_score <= 1),
    similarity_type TEXT,  -- 'flavor', 'region', 'category', 'price'
    PRIMARY KEY (tea_id, similar_tea_id)
);

CREATE INDEX IF NOT EXISTS idx_tea_similar_similar ON tea_similar(similar_tea_id);

-- Comparison pairs (for vs pages)
CREATE TABLE IF NOT EXISTS comparison_pairs (
    id TEXT PRIMARY KEY,
    tea_a_id TEXT NOT NULL REFERENCES teas(id),
    tea_b_id TEXT NOT NULL REFERENCES teas(id),
    comparison_type TEXT NOT NULL,  -- 'same_category', 'same_region', 'similar_flavor', 'similar_oxidation', 'cross_category'
    relevance_score REAL NOT NULL DEFAULT 0.5 CHECK (relevance_score >= 0 AND relevance_score <= 1),
    is_valid INTEGER NOT NULL DEFAULT 1,
    narrative TEXT,
    key_differences TEXT,  -- JSON array
    key_similarities TEXT,  -- JSON array
    search_volume INTEGER,  -- Estimated monthly searches
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(tea_a_id, tea_b_id)
);

CREATE INDEX IF NOT EXISTS idx_comparison_pairs_tea_a ON comparison_pairs(tea_a_id);
CREATE INDEX IF NOT EXISTS idx_comparison_pairs_tea_b ON comparison_pairs(tea_b_id);

-- ============================================================================
-- BUILD TRACKING
-- ============================================================================

-- Page manifest for incremental builds
CREATE TABLE IF NOT EXISTS page_manifest (
    url TEXT PRIMARY KEY,
    template TEXT NOT NULL,
    data_hash TEXT NOT NULL,
    template_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    published_at TEXT,
    word_count INTEGER DEFAULT 0,
    internal_links_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_page_manifest_status ON page_manifest(status);
CREATE INDEX IF NOT EXISTS idx_page_manifest_template ON page_manifest(template);

-- Build history for analytics
CREATE TABLE IF NOT EXISTS build_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    pages_total INTEGER,
    pages_new INTEGER,
    pages_updated INTEGER,
    pages_unchanged INTEGER,
    duration_seconds REAL,
    incremental INTEGER NOT NULL DEFAULT 1,
    error_count INTEGER DEFAULT 0,
    error_messages TEXT  -- JSON array
);

-- ============================================================================
-- CONTENT TABLES
-- ============================================================================

-- Curated content for pillar pages (AI-generated, human-reviewed)
CREATE TABLE IF NOT EXISTS pillar_content (
    page_type TEXT NOT NULL,  -- 'category', 'region', 'method'
    entity_id TEXT NOT NULL,
    section TEXT NOT NULL,  -- 'intro', 'history', 'characteristics', 'selection', 'brewing'
    content TEXT NOT NULL,
    word_count INTEGER,
    generated_at TEXT,
    reviewed_at TEXT,
    reviewer TEXT,
    PRIMARY KEY (page_type, entity_id, section)
);

-- Comparison narratives for top pairs
CREATE TABLE IF NOT EXISTS comparison_content (
    comparison_id TEXT PRIMARY KEY REFERENCES comparison_pairs(id),
    intro TEXT,
    flavor_comparison TEXT,
    brewing_comparison TEXT,
    price_comparison TEXT,
    verdict TEXT,
    word_count INTEGER,
    generated_at TEXT,
    reviewed_at TEXT
);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Full tea view with category and region names
CREATE VIEW IF NOT EXISTS v_teas_full AS
SELECT
    t.*,
    c.name_en AS category_name,
    c.name_zh AS category_name_zh,
    s.name_en AS subcategory_name,
    r.name_en AS region_name,
    r.name_zh AS region_name_zh,
    pr.name_en AS province_name
FROM teas t
JOIN categories c ON t.category_id = c.id
LEFT JOIN subcategories s ON t.subcategory_id = s.id
JOIN regions r ON t.region_id = r.id
LEFT JOIN regions pr ON r.parent_id = pr.id;

-- Region hierarchy view
CREATE VIEW IF NOT EXISTS v_regions_hierarchy AS
SELECT
    r.id,
    r.name_en,
    r.name_zh,
    r.region_type,
    p.id AS parent_id,
    p.name_en AS parent_name,
    gp.id AS grandparent_id,
    gp.name_en AS grandparent_name
FROM regions r
LEFT JOIN regions p ON r.parent_id = p.id
LEFT JOIN regions gp ON p.parent_id = gp.id;

-- Tea count by category
CREATE VIEW IF NOT EXISTS v_category_stats AS
SELECT
    c.id,
    c.name_en,
    COUNT(t.id) AS tea_count,
    AVG(CASE WHEN t.oxidation_level IS NOT NULL THEN t.oxidation_level END) AS avg_oxidation
FROM categories c
LEFT JOIN teas t ON c.id = t.category_id
GROUP BY c.id;

-- Published pages summary
CREATE VIEW IF NOT EXISTS v_publish_stats AS
SELECT
    template,
    status,
    COUNT(*) AS page_count,
    SUM(word_count) AS total_words,
    AVG(internal_links_count) AS avg_internal_links
FROM page_manifest
GROUP BY template, status;

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS update_categories_timestamp
AFTER UPDATE ON categories
BEGIN
    UPDATE categories SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_teas_timestamp
AFTER UPDATE ON teas
BEGIN
    UPDATE teas SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_regions_timestamp
AFTER UPDATE ON regions
BEGIN
    UPDATE regions SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_teaware_timestamp
AFTER UPDATE ON teaware
BEGIN
    UPDATE teaware SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- ============================================================================
-- PERFORMANCE DATA
-- ============================================================================

-- Google Search Console performance snapshots
CREATE TABLE IF NOT EXISTS page_performance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    query TEXT,
    clicks INTEGER NOT NULL DEFAULT 0,
    impressions INTEGER NOT NULL DEFAULT 0,
    ctr REAL NOT NULL DEFAULT 0.0,
    avg_position REAL NOT NULL DEFAULT 0.0,
    device TEXT,
    country TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(url, snapshot_date, query, device, country)
);

CREATE INDEX IF NOT EXISTS idx_page_performance_url ON page_performance_snapshots(url);
CREATE INDEX IF NOT EXISTS idx_page_performance_date ON page_performance_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_page_performance_query ON page_performance_snapshots(query);
