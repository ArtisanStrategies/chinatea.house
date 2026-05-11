# Autonomous SEO System Implementation Plan

## Purpose

This document defines how `chinatea.house` becomes a mostly hands-off, continuously improving onsite SEO system.

The target outcome is not a larger one-time site build. The target outcome is an operating system that:

- expands and repairs the factual graph automatically
- discovers and scores new page opportunities automatically
- generates structured page modules automatically
- builds and publishes new pages automatically
- improves interlinking automatically
- refreshes, reworks, or prunes weak pages automatically

This plan covers the full loop from research to page production to performance-driven iteration.

---

## Target State

At steady state, the system should run on a schedule with only light human oversight.

Daily behavior:

- discover new entities and missing facts
- refresh stale or weak-confidence entities
- generate candidate pages across active page systems
- score candidates and publish only high-confidence pages
- regenerate internal links for affected clusters

Weekly behavior:

- evaluate page-family performance
- tighten or loosen scoring thresholds
- refresh pages with strong impressions but weak CTR
- prune or noindex weak pages

Monthly behavior:

- add one new query system or expand an existing one
- reprocess older entities with improved prompts or rules
- review low-confidence exceptions and source drift

---

## Design Principles

1. Facts are evidence-backed.
2. AI extracts and synthesizes; it does not directly write canonical truth into production tables.
3. Every page family is a system with candidates, rules, schemas, renderers, scores, and refresh logic.
4. Every URL must justify its existence through differentiated utility.
5. Interlinking is treated as a core ranking and crawl system, not a template afterthought.
6. The system must be able to delete pages as confidently as it creates them.

---

## Scope

The implementation includes:

- autonomous graph acquisition and repair
- evidence-backed canonical entity resolution
- structured content generation for page modules
- new page systems beyond the current category, region, tea, and comparison families
- automated interlinking and cluster graph generation
- quality scoring, publish gating, refresh, and prune workflows
- reporting and operational metrics

The implementation does not initially include:

- offsite SEO
- link acquisition
- editorial CMS for manual writing
- ecommerce

---

## System Workstreams

### 1. Research and Graph Expansion

Goal:

- continuously grow and repair the tea knowledge graph without manual DB maintenance

Deliverables:

- source ingestion layer
- candidate discovery pipeline
- claim extraction pipeline
- entity reconciliation pipeline
- entity quality scoring
- refresh queue for stale entities

Key result:

- the database becomes a produced artifact of the research system, not a hand-maintained asset

### 2. Canonical Data and Validation

Goal:

- make every production entity traceable, scored, and safe for page generation

Deliverables:

- stronger validation rules
- per-field confidence
- source count thresholds
- duplicate detection
- conflict resolution rules
- entity version history

Key result:

- page generation only runs on publishable entities

### 3. Page Systems

Goal:

- move from a few hardcoded page families to a pluggable set of query systems

Initial page systems:

- `tea_detail_v2`
- `comparison_v2`
- `brewing_intent`
- `occasion_intent`
- `attribute_intent`
- `decision_intent`

Key result:

- inventory growth is driven by query systems, not ad hoc brainstorming

### 4. Structured Content Modules

Goal:

- use LLMs to fill strict, reusable modules instead of writing freeform pages

Examples:

- brewing quick answer
- mistake diagnosis
- choose-if matrix
- who-should-skip section
- FAQ blocks
- title and meta variants
- summary bullets

Key result:

- consistent quality and re-renderable pages

### 5. Interlinking System

Goal:

- build an internal link graph around intent clusters, not only site hierarchy

Linking surfaces:

- hierarchy links
- sibling links
- query-cluster links
- decision-path links
- freshness links
- substitution links such as "if you like X, try Y"

Key result:

- better crawl depth, stronger topical clustering, and more controllable authority flow

### 6. Publish, Refresh, and Prune

Goal:

- operate the site as a managed inventory portfolio

Deliverables:

- publish score thresholds
- batch publishing strategy
- refresh rules
- prune and noindex rules
- family-level performance dashboards

Key result:

- the site gets denser where quality is proven and thinner where utility is weak

---

## Phased Implementation

## Phase 0: Foundations

Objective:

- prepare the repo to support the new architecture without breaking the current build

Tasks:

- add new planning and design docs
- define new DB tables for sources, claims, candidates, page scores, and link graph state
- define page-system interface and job interface
- define canonical quality thresholds for production entities
- define publish quality thresholds for production pages

Acceptance criteria:

- approved schema and module boundaries
- all new system states defined
- no codepath yet depends on external data ingestion

## Phase 1: Evidence-Backed Research Pipeline

Objective:

- replace one-shot research with a source -> claim -> canonical entity pipeline

Tasks:

- implement `source_documents`
- implement `entity_candidates`
- implement `entity_claims`
- implement `entity_aliases`
- implement `entity_versions`
- implement `entity_quality`
- implement candidate discovery jobs
- implement source fetchers and snapshot storage
- implement LLM claim extraction
- implement deterministic reconciliation rules
- implement entity validation and quality scoring
- implement safe upsert into production entities

Acceptance criteria:

- new teas can be added automatically from multi-source evidence
- existing teas can be refreshed automatically
- every production fact can be traced back to claims and sources

## Phase 2: Page-System Framework

Objective:

- make page generation modular and score-driven

Tasks:

- refactor generator into pluggable page systems
- add candidate generation for each page family
- add page eligibility rules
- add page quality scoring
- add page manifest enrichment with score, family, cluster, and refresh metadata

Acceptance criteria:

- adding a new page family does not require large generator branching
- each page family can be enabled, disabled, and tuned independently

## Phase 3: Content Module System

Objective:

- move from loose section JSON to strict family-specific schemas

Tasks:

- define schemas for brewing, comparison, tea detail, occasion, and attribute modules
- store generated modules in dedicated content tables
- make templates consume stored modules instead of template fallbacks where possible
- implement generation retries, schema validation, and hold states

Acceptance criteria:

- AI output is schema-valid or rejected
- content modules can be regenerated without changing canonical facts
- templates remain deterministic and reusable

## Phase 4: Interlinking Engine

Objective:

- automate crawl-aware, intent-aware internal linking

Tasks:

- define link graph rules per page family
- generate cluster hubs and cluster edges
- add related-path sections across tea, brewing, occasion, and comparison families
- score link candidates by relevance, diversity, and supportability
- add link audits for orphaning and overlinking

Acceptance criteria:

- no published page is orphaned
- every page family participates in at least one strong cluster
- link generation is deterministic and auditable

## Phase 5: Publish, Refresh, and Prune Loop

Objective:

- make the site self-managing after pages exist

Tasks:

- add publish queue based on page score, freshness, and family strategy
- add refresh queue for high-potential pages
- add re-title/meta rewrite workflow for low-CTR pages
- add prune/noindex/archive workflow for weak pages
- add family-level score calibration

Acceptance criteria:

- the system can autonomously publish, refresh, and retire URLs
- weak inventory does not accumulate indefinitely

## Phase 6: Performance Learning Loop

Objective:

- let the site learn from search outcomes

Tasks:

- ingest GSC and analytics data
- store performance snapshots at URL and family level
- detect pages with impressions but poor CTR
- detect pages with rank but weak engagement
- feed performance into publish and refresh scoring

Acceptance criteria:

- the system changes behavior based on real outcomes, not just generation logic

---

## Proposed Page Systems

### `tea_detail_v2`

Purpose:

- canonical entity page for each tea

Core modules:

- quick answers
- flavor and fit
- brewing quick reference
- best first purchase
- similar teas
- linked intent paths

Eligibility:

- entity quality above threshold
- minimum brewing and flavor coverage

### `comparison_v2`

Purpose:

- solve explicit tea comparison queries and adjacent decision queries

Core modules:

- quick verdict
- choose-if matrix
- audience fit
- brewing differences
- price and availability framing
- substitute-next links

Eligibility:

- meaningful differentiation
- useful search intent or cluster support
- minimum link neighborhood

### `brewing_intent`

Purpose:

- capture high-utility preparation queries

Core modules:

- temperature and timing
- gongfu and western variants
- troubleshooting
- vessel-specific adjustments
- quick calculator

Eligibility:

- sufficient brewing data
- sufficient distinctiveness from parent tea page

### `occasion_intent`

Purpose:

- capture "best tea for X" selection intent

Core modules:

- ranked recommendations
- why each tea fits
- who should avoid it
- brewing simplicity
- caffeine guidance

Eligibility:

- occasion has distinct recommendation set
- at least three strong candidate teas

### `attribute_intent`

Purpose:

- capture attribute-driven searches such as caffeine, roast, oxidation, flavor, body

Core modules:

- answer block
- supporting explanation
- ranked examples
- caveats

Eligibility:

- enough structured evidence to differentiate answers

### `decision_intent`

Purpose:

- capture beginner and tradeoff queries

Examples:

- best oolong for beginners
- best tea for gifting
- best pu-erh under a budget

Core modules:

- ranking table
- choose-if blocks
- simplicity, value, caffeine, and flavor fit

Eligibility:

- meaningful recommendation differences

---

## Interlinking Strategy

Interlinking must be system-generated and family-aware.

### Link Types

- parent and child hierarchy links
- sibling links
- intent-cluster links
- alternative and substitute links
- next-step educational links
- freshness links to newly improved pages

### Required Link Patterns

- tea page -> brewing pages
- tea page -> top comparisons
- tea page -> best-fit occasions
- tea page -> alternative teas
- occasion page -> recommended teas
- occasion page -> corresponding brewing paths
- comparison page -> tea detail pages for both entities
- comparison page -> adjacent comparisons and substitutes
- category page -> beginner, caffeine, budget, and brewing paths

### Link Rules

- no orphan published pages
- no page should rely only on nav or sitemap discovery
- no page should exceed configurable contextual link limits
- link anchors should match user intent and page purpose

### Link Quality Signals

- semantic relevance
- cluster diversity
- reciprocal support
- crawl distance reduction
- user path usefulness

---

## Operational Requirements

### Jobs

- candidate discovery job
- source fetch job
- claim extraction job
- reconciliation job
- validation job
- page candidate generation job
- content module generation job
- interlinking rebuild job
- publish job
- refresh job
- prune job
- reporting job

### Queues

- research queue
- entity refresh queue
- page generation queue
- content regeneration queue
- link rebuild queue
- publish queue
- prune queue

### Safety Gates

- source minimums for key facts
- schema validation required for generated modules
- duplicate intent suppression
- page score threshold for publish
- manual hold bucket for low-confidence exceptions

---

## Success Metrics For This Plan

### Graph Health

- entities added per week
- stale entities refreshed per week
- percent of entities above production quality threshold
- percent of production entities with source traceability

### Page System Health

- candidates generated per family
- percent eligible per family
- percent published per family
- percent refreshed per family
- percent pruned per family

### Search Outcomes

- indexed pages by family
- impressions per page by family
- CTR by family
- clicks per page by family
- percent of pages with any clicks

### Link Graph Health

- orphan pages
- average cluster size
- average crawl distance to supporting pages
- contextual links per page

---

## Risks

### Overproduction

Risk:

- the system generates too many low-signal pages

Mitigation:

- hard publish thresholds
- family-level quotas
- prune rules

### Factual Drift

Risk:

- LLM extraction causes subtle incorrect facts

Mitigation:

- claim-level evidence storage
- multi-source confidence rules
- deterministic reconciliation before upsert

### Index Bloat

Risk:

- pages exist but should not be indexed

Mitigation:

- eligibility scoring before generation
- prune and noindex states
- stricter family-level gating

### Link Noise

Risk:

- overlinking creates weak clusters and poor UX

Mitigation:

- score-based link selection
- per-family link budgets
- cluster-aware linking rules

---

## Immediate Next Steps

1. Approve the target architecture and page-system model.
2. Implement the schema additions for research, claims, and page scoring.
3. Refactor the generator into pluggable page systems.
4. Ship the evidence-backed research pipeline before adding large new page families.
5. Ship `comparison_v2` and `brewing_intent` as the first two upgraded systems.
6. Ship the interlinking engine upgrade before high-volume publishing.
7. Add performance ingestion and automated refresh/prune once publishing is stable.

---

## Definition of Done

The implementation is complete when:

- the DB can expand and repair itself through evidence-backed automation
- new page families can be added as independent systems
- pages are generated from strict structured modules
- interlinking is generated by cluster logic rather than template-only logic
- the site can publish, refresh, and prune automatically
- performance data changes system behavior over time
