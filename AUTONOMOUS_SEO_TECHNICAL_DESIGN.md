# Autonomous SEO System Technical Design

## Overview

This document describes the technical design for a mostly autonomous onsite SEO system for `chinatea.house`.

The system has six major subsystems:

- research acquisition
- canonical graph management
- page-system orchestration
- structured content generation
- interlinking and cluster graph generation
- publish, refresh, prune, and performance feedback

The core design decision is:

`sources -> claims -> canonical graph -> page candidates -> content modules -> rendered pages -> performance feedback`

The production database is no longer treated as a hand-edited store. It is the output of a controlled pipeline.

---

## Goals

- autonomously expand and repair the tea knowledge graph
- generate only pages that deserve to exist
- use LLMs only inside strict, validated boundaries
- make internal linking systematic and query-aware
- continuously refresh winners and retire weak inventory

---

## Non-Goals

- unrestricted autonomous browsing and publishing without safeguards
- using LLMs as a direct replacement for canonical truth
- generating pages from freeform article prompts
- solving offsite SEO or authority acquisition

---

## System Architecture

## Logical Flow

1. discover candidate entities and missing fields
2. fetch and snapshot source documents
3. extract atomic claims from documents
4. reconcile claims into canonical entities
5. validate and score entities
6. generate page candidates from active page systems
7. score candidate pages
8. generate structured content modules
9. generate interlink graph
10. render and publish selected pages
11. ingest performance data
12. refresh, rewrite, or prune pages based on outcomes

## Main Runtime Components

- `ResearchOrchestrator`
- `SourceFetcher`
- `ClaimExtractor`
- `EntityReconciler`
- `EntityValidator`
- `PageSystemRegistry`
- `PageCandidateScorer`
- `ContentModuleGenerator`
- `InterlinkingEngine`
- `PublishManager`
- `RefreshManager`
- `PruneManager`
- `PerformanceIngestor`

---

## Data Model

## Existing Production Entities

The current repo already has core entities such as:

- categories
- subcategories
- regions
- teas
- occasions
- teaware
- brewing methods
- comparison pairs

These remain the canonical graph used by renderers.

## New Research Tables

### `source_documents`

Purpose:

- store fetched source snapshots and metadata

Suggested fields:

- `id`
- `source_type`
- `source_domain`
- `canonical_url`
- `fetched_at`
- `content_hash`
- `raw_path`
- `title`
- `language`
- `http_status`
- `is_active`

### `entity_candidates`

Purpose:

- hold proposed new entities or entity refresh tasks

Suggested fields:

- `id`
- `entity_type`
- `candidate_key`
- `discovery_source`
- `display_name`
- `status`
- `priority`
- `created_at`
- `updated_at`

Statuses:

- `new`
- `fetching`
- `extracting`
- `reconciling`
- `validated`
- `rejected`
- `promoted`

### `entity_claims`

Purpose:

- store atomic evidence-backed claims per field

Suggested fields:

- `id`
- `candidate_id`
- `entity_type`
- `entity_key`
- `field_name`
- `field_value_json`
- `value_type`
- `source_document_id`
- `evidence_excerpt`
- `extractor_model`
- `extractor_confidence`
- `created_at`

### `entity_aliases`

Purpose:

- normalize name variants and merge duplicate discovery paths

Suggested fields:

- `id`
- `entity_type`
- `canonical_entity_id`
- `alias_text`
- `alias_type`
- `confidence`

### `entity_quality`

Purpose:

- record publishability and confidence

Suggested fields:

- `entity_type`
- `entity_id`
- `overall_score`
- `source_count`
- `field_coverage_score`
- `conflict_score`
- `freshness_score`
- `publishable`
- `updated_at`

### `entity_versions`

Purpose:

- keep a version history of canonical entities

Suggested fields:

- `id`
- `entity_type`
- `entity_id`
- `version_number`
- `payload_json`
- `derived_from_claims_json`
- `created_at`

## New Page-System Tables

### `page_candidates`

Purpose:

- persist proposed URLs before generation and publish

Suggested fields:

- `id`
- `page_family`
- `url`
- `entity_refs_json`
- `query_intent`
- `cluster_id`
- `candidate_score`
- `eligibility_status`
- `publish_status`
- `created_at`
- `updated_at`

### `page_quality`

Purpose:

- persist multi-factor scoring

Suggested fields:

- `page_candidate_id`
- `intent_fit_score`
- `data_coverage_score`
- `uniqueness_score`
- `utility_score`
- `link_support_score`
- `serp_packaging_score`
- `overall_score`
- `scored_at`

### `link_graph`

Purpose:

- persist generated internal links and link reasons

Suggested fields:

- `source_url`
- `target_url`
- `link_type`
- `anchor_text`
- `score`
- `reason`
- `generated_at`

### `page_performance_snapshots`

Purpose:

- store URL-level performance over time

Suggested fields:

- `url`
- `snapshot_date`
- `impressions`
- `clicks`
- `ctr`
- `avg_position`
- `sessions`
- `engaged_sessions`
- `conversions`

---

## Research Acquisition Design

## Candidate Discovery

Inputs:

- known source lists
- source sitemaps and category pages
- references inside existing entities
- gaps found in comparisons, regions, or content modules
- missing field reports from validators

Outputs:

- new `entity_candidates`
- new refresh tasks for stale entities

Rules:

- deduplicate by normalized name and alias table
- prioritize entities that unlock many page candidates
- prioritize entities that appear in high-value regions or categories

## Source Fetching

Responsibilities:

- fetch source pages or documents
- store raw content snapshot
- normalize text extraction
- assign source trust weight

Source metadata should include:

- domain
- source type
- source trust tier
- extraction quality

## Claim Extraction

Responsibilities:

- use an LLM to extract field-level claims
- attach source, evidence snippet, and confidence to each claim

Important constraint:

- the extractor returns field claims, not a fully assembled `Tea`

Example claims:

- `category_id = oolong`
- `region_id = wuyi-mountains`
- `flavor_primary includes mineral`
- `brewing_gongfu.water_temp_c = 95`

## Entity Reconciliation

Responsibilities:

- merge claims into a canonical entity candidate
- resolve aliases
- choose best field values
- compute per-field confidence

Resolution rules:

- deterministic rules first
- trust-weighted voting across sources
- LLM-assisted resolution only for ambiguous text normalization
- existing higher-confidence production facts are not overwritten by weaker evidence

## Entity Validation

Responsibilities:

- validate against Pydantic schema
- validate cross-field consistency
- validate minimum source thresholds
- validate category and region compatibility
- validate completeness for page eligibility

Outputs:

- publishable entity
- held entity
- rejected entity

---

## Page-System Design

## Page-System Interface

Each page family implements:

- `discover_candidates(db) -> list[PageCandidate]`
- `evaluate_eligibility(candidate, db) -> EligibilityResult`
- `build_content_inputs(candidate, db) -> dict`
- `generate_modules(candidate, inputs) -> ModuleSet`
- `build_links(candidate, db) -> list[LinkEdge]`
- `render_context(candidate, modules, links, db) -> dict`
- `refresh_policy(candidate, performance) -> RefreshDecision`
- `prune_policy(candidate, performance) -> PruneDecision`

## Core Page Families

### `tea_detail_v2`

Entity refs:

- tea
- category
- region
- linked occasions
- linked comparisons

### `comparison_v2`

Entity refs:

- tea A
- tea B
- comparison type
- audience intent

### `brewing_intent`

Entity refs:

- tea
- brewing method
- vessel type

### `occasion_intent`

Entity refs:

- occasion
- ranked tea set

### `attribute_intent`

Entity refs:

- attribute type
- supporting tea set

### `decision_intent`

Entity refs:

- category or tea set
- audience
- decision frame such as beginner, budget, gift, low caffeine

---

## Page Candidate Scoring

## Score Components

- `intent_fit_score`
- `data_coverage_score`
- `uniqueness_score`
- `utility_score`
- `link_support_score`
- `serp_packaging_score`

## Example Eligibility Rules

Comparison page:

- two teas must not be near-duplicates unless explicit comparison demand exists
- two teas must have enough contrasting data
- page must have a strong surrounding cluster of linkable pages

Occasion page:

- must produce a recommendation set with meaningful variation
- must have at least three strong teas with good supporting data

Brewing page:

- tea must have at least one strong brewing method payload
- page must not merely restate the tea page without added utility

## Publish Thresholds

Suggested states:

- `publish`
- `hold_for_enrichment`
- `discard`

These thresholds should be family-specific.

---

## Structured Content Generation Design

## Principle

LLMs generate presentation modules within strict schemas. They do not decide canonical facts.

## Example Module Schemas

### Brewing module

Fields:

- `quick_answer`
- `gongfu_summary`
- `western_summary`
- `mistakes`
- `adjustments_for_bitterness`
- `adjustments_for_weakness`
- `faq`

### Comparison module

Fields:

- `quick_verdict`
- `choose_tea_a_if`
- `choose_tea_b_if`
- `beginner_recommendation`
- `advanced_recommendation`
- `brewing_difference_summary`
- `price_value_summary`
- `faq`

### Occasion module

Fields:

- `occasion_summary`
- `top_picks`
- `avoid_if`
- `brewing_ease_notes`
- `caffeine_fit`
- `faq`

### Tea detail enhancement module

Fields:

- `taste_summary`
- `best_time_to_drink`
- `who_should_try_it`
- `who_should_skip_it`
- `best_first_purchase_advice`
- `common_mistakes`

## Validation Rules

- every module must validate against schema
- generated statements must not contradict canonical facts
- invalid modules move to hold or retry

---

## Interlinking Engine Design

## Purpose

Internal linking should express topical relationships and user paths, not just parent-child structure.

## Link Types

- `hierarchy`
- `sibling`
- `intent_support`
- `alternative`
- `comparison_neighbor`
- `next_step`
- `freshness_promote`

## Cluster Model

A cluster is a connected group of URLs around a user intent.

Examples:

- `da-hong-pao` cluster
- `oolong-for-beginners` cluster
- `tea-for-focus` cluster

Each page candidate gets:

- `cluster_id`
- `cluster_role`

Cluster roles:

- `hub`
- `canonical`
- `comparison`
- `brewing`
- `selection`
- `supporting`

## Link Generation Rules

### Tea page

Must link to:

- best brewing pages
- best-fit occasions
- top comparisons
- closest alternatives

### Comparison page

Must link to:

- both tea detail pages
- adjacent comparisons
- occasion pages relevant to the decision
- brewing pages if preparation differs materially

### Occasion page

Must link to:

- top tea recommendations
- brewing pages for those teas
- category or attribute pages explaining the recommendation logic

### Category page

Must link to:

- beginner paths
- budget paths
- brewing paths
- selection paths

## Link Scoring

Each candidate link can be scored by:

- semantic relevance
- click usefulness
- cluster support
- crawl benefit
- diversity contribution

Low-value links are omitted.

## Link Graph Persistence

Persist generated links with reasons so audits and rebuilds are deterministic.

---

## Rendering and Build Design

## Generator Refactor

Current generator flow is template-family based. It should be refactored into:

- page system registry
- candidate collection pass
- eligibility and scoring pass
- module generation pass
- interlinking pass
- render pass
- manifest write pass

## Build Inputs

Each rendered page should be a pure function of:

- canonical entities
- validated content modules
- generated link edges
- template version

## Build Outputs

- rendered HTML
- page manifest record
- score metadata
- link graph edges

---

## Publish, Refresh, and Prune Design

## Publish Queue

Selection factors:

- overall page score
- family-specific quotas
- cluster balance
- freshness of linked support pages

## Refresh Queue

Triggers:

- high impressions, weak CTR
- strong engagement but weak rankings
- stale entities underlying a high-value page
- improved content schema available

## Prune Queue

Triggers:

- no impressions after aging period
- weak uniqueness score
- thin support graph
- cluster redundancy

Prune actions:

- noindex
- archive
- redirect to canonical sibling
- delete from publish rotation

---

## Performance Feedback Design

## Data Sources

- Google Search Console
- analytics
- internal page and family metadata

## Outcome Classifications

- `winner`
- `needs_ctr_rewrite`
- `needs_content_enrichment`
- `needs_link_support`
- `needs_prune_review`

## Feedback Effects

- adjust title/meta variants
- trigger module regeneration
- raise or lower family publish threshold
- promote or demote cluster priority

---

## Operational Concerns

## Scheduling

Recommended cadence:

- daily research and candidate generation
- daily low-volume publish job
- daily interlink rebuild for affected clusters
- weekly score recalibration
- weekly prune and refresh review job

## Idempotency

Jobs must be re-runnable without duplicate production side effects.

Strategies:

- deterministic keys
- upserts
- entity versioning
- immutable source snapshots

## Observability

Need dashboards for:

- graph health
- family health
- publish activity
- prune activity
- link graph health
- search performance by family

## Failure Handling

Use hold states for:

- low-confidence reconciliation
- schema-invalid content modules
- conflicting high-value source claims
- low-score page candidates

---

## Security and Safety

- never allow direct model writes to production entity tables
- never publish low-score pages just because generation succeeded
- never overwrite high-confidence fields with weak evidence
- always preserve source provenance for key facts

---

## Suggested Module Layout

Possible package expansion inside `execution/`:

- `execution/research/`
- `execution/research/discovery.py`
- `execution/research/fetch.py`
- `execution/research/extract.py`
- `execution/research/reconcile.py`
- `execution/research/quality.py`
- `execution/page_systems/`
- `execution/page_systems/base.py`
- `execution/page_systems/tea_detail.py`
- `execution/page_systems/comparison.py`
- `execution/page_systems/brewing.py`
- `execution/page_systems/occasion.py`
- `execution/page_systems/attribute.py`
- `execution/page_systems/decision.py`
- `execution/content_modules/`
- `execution/content_modules/schemas.py`
- `execution/content_modules/generator.py`
- `execution/linking/`
- `execution/linking/engine.py`
- `execution/linking/clusters.py`
- `execution/linking/scoring.py`
- `execution/ops/`
- `execution/ops/publish.py`
- `execution/ops/refresh.py`
- `execution/ops/prune.py`
- `execution/ops/performance.py`

---

## Open Design Decisions

- which source domains are allowed for autonomous research
- where source snapshots are stored on disk
- whether content module schemas live in code only or also as JSON schema artifacts
- whether family thresholds are static config or learned policies
- whether prune actions default to noindex before delete

---

## Recommended First Implementation Slice

The first working slice should be:

1. source document snapshots
2. entity claims and reconciliation
3. page candidate table
4. pluggable `comparison_v2` page system
5. strict comparison module schema
6. interlinking upgrade for comparison clusters
7. publish score gating

This slice is the smallest path to proving the architecture end to end before expanding to brewing and occasion systems.
