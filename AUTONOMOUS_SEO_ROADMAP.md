# Autonomous SEO System Roadmap

## Objective

Build `chinatea.house` into a mostly autonomous onsite SEO engine that continuously improves its graph, creates useful pages, interlinks them intelligently, and manages inventory quality over time.

This roadmap is phased to reduce risk:

- first make data acquisition trustworthy
- then make page generation modular
- then expand page systems
- then automate learning, refresh, and pruning

---

## Phase Summary

| Phase | Window | Focus | Main Output |
|------|--------|-------|-------------|
| 0 | Week 0-1 | Architecture and planning | Approved docs, schema plan, work breakdown |
| 1 | Week 1-3 | Research pipeline | Evidence-backed graph acquisition |
| 2 | Week 3-5 | Page-system framework | Pluggable page families and scoring |
| 3 | Week 5-7 | Structured module generation | Content schemas and content stores |
| 4 | Week 7-9 | Interlinking engine | Intent-aware link graph |
| 5 | Week 9-11 | New page systems | Brewing and occasion systems live |
| 6 | Week 11-13 | Autonomous inventory management | Publish, refresh, prune loop |
| 7 | Week 13-16 | Performance learning | GSC-driven optimization loop |

---

## Phase 0: Planning and Architecture

### Goals

- finalize the end-state architecture
- define tables, queues, jobs, and interfaces
- define quality thresholds and rollout strategy

### Deliverables

- implementation plan
- roadmap
- technical design
- initial schema migration specification
- page-system interface specification

### Exit Criteria

- core architecture approved
- no unresolved ambiguity about graph acquisition or page generation flow

---

## Phase 1: Evidence-Backed Graph Acquisition

### Goals

- stop relying on one-shot LLM entity creation
- introduce claims, evidence, and reconciliation

### Scope

- source discovery
- source snapshot storage
- entity candidate creation
- claim extraction
- alias resolution
- reconciliation
- quality scoring
- safe upsert to production entities

### Deliverables

- `source_documents` tables and models
- `entity_candidates` tables and models
- `entity_claims` tables and models
- `entity_versions` tables and models
- research workers and queues
- stronger validation rules

### Dependencies

- schema migrations
- storage conventions for source snapshots

### Exit Criteria

- system can autonomously add and refresh tea entities with source traceability
- production entities have confidence and freshness metadata

---

## Phase 2: Page-System Framework

### Goals

- remove page-family hardcoding as the main scaling bottleneck
- make candidate generation and scoring first-class

### Scope

- page family registry
- shared page-system interface
- page candidate table
- family-level eligibility logic
- publish score computation

### Deliverables

- page-system base classes
- page candidate models and tables
- generator refactor
- family-specific candidate generators

### Dependencies

- stable canonical entities from Phase 1

### Exit Criteria

- new page families can be added without large generator rewrites
- each family can be run independently

---

## Phase 3: Structured Module Generation

### Goals

- replace loose section generation with strict family-specific schemas

### Scope

- family schemas for brewing, comparison, tea, occasion, attribute, and decision pages
- generation workers
- validation and retry logic
- content stores
- hold states for invalid or low-confidence output

### Deliverables

- schema definitions
- content generation interfaces
- per-family content tables
- template consumption of stored modules

### Dependencies

- page-system framework

### Exit Criteria

- no family depends on freeform AI prose for critical structure
- templates can render with consistent module contracts

---

## Phase 4: Interlinking Engine

### Goals

- treat internal links as a generated graph, not hand-authored template glue

### Scope

- cluster model
- intent-aware edge generation
- family-aware link policies
- orphan detection
- link budget control
- link audit reporting

### Deliverables

- link graph builder
- cluster assignment logic
- per-family link rules
- link graph persistence
- link audit reports

### Dependencies

- page candidates and family metadata

### Exit Criteria

- published pages are cluster-connected
- system can rebuild link neighborhoods deterministically

---

## Phase 5: New Page Systems

### Goals

- unlock new search coverage from the current graph

### Priority Order

1. `comparison_v2`
2. `brewing_intent`
3. `occasion_intent`
4. `tea_detail_v2`
5. `attribute_intent`
6. `decision_intent`

### Deliverables

- live page systems for brewing and occasion intent
- upgraded comparison pages with stronger decision support
- upgraded tea pages with quick-answer modules

### Dependencies

- Phases 2 through 4

### Exit Criteria

- at least two new page systems publishing automatically
- comparison and tea pages upgraded to structured module flows

---

## Phase 6: Autonomous Inventory Management

### Goals

- make publishing, refreshing, and pruning self-operating

### Scope

- publish queues
- family quotas
- refresh queue
- prune and noindex queue
- title/meta rewrite workflow
- aging and freshness policies

### Deliverables

- page state transitions
- scheduled publish job
- scheduled refresh job
- prune and archive workflow
- family dashboards

### Dependencies

- stable family scores
- content regeneration path

### Exit Criteria

- the system can autonomously manage page inventory without manual daily intervention

---

## Phase 7: Performance Learning Loop

### Goals

- make the system adapt to outcomes rather than only inputs

### Scope

- ingest GSC and analytics data
- compute family performance metrics
- identify low-CTR and high-impression opportunities
- feed outcomes into publish and refresh scoring

### Deliverables

- performance snapshot tables
- reporting jobs
- score recalibration rules
- re-title and re-enrichment triggers

### Dependencies

- stable URL inventory
- search performance data collection

### Exit Criteria

- the system automatically changes behavior based on real search outcomes

---

## Workstreams

## Workstream A: Data and Schema

Owns:

- research tables
- claim and source tables
- page candidate and quality tables
- versioning and freshness metadata

## Workstream B: Research Automation

Owns:

- candidate discovery
- source fetching
- claim extraction
- reconciliation
- canonical upsert

## Workstream C: Page Generation

Owns:

- page systems
- content schemas
- family renderers
- family scoring

## Workstream D: Interlinking

Owns:

- cluster assignment
- contextual edge generation
- link budgets
- audits and orphan prevention

## Workstream E: Operations and Learning

Owns:

- publish loop
- refresh and prune loop
- reporting
- score calibration

---

## Milestones

### Milestone 1: Graph Can Self-Improve

Target:

- autonomous entity discovery and refresh is live

Signals:

- new entities added from multiple sources
- stale entities revalidated automatically
- traceable evidence stored for key fields

### Milestone 2: Generator Becomes a Platform

Target:

- page systems are modular and score-driven

Signals:

- page candidates persisted and scored
- family logic isolated
- generator supports opt-in family rollout

### Milestone 3: Interlinking Becomes Strategic

Target:

- cluster-driven linking is live

Signals:

- no orphans
- cluster paths visible across tea, brewing, occasion, and comparison systems

### Milestone 4: New Systems Start Compounding

Target:

- brewing and occasion systems publish regularly

Signals:

- pages publish from automated candidate queues
- supporting links are generated automatically

### Milestone 5: Inventory Manages Itself

Target:

- publish, refresh, and prune are automated

Signals:

- system retires weak pages
- system refreshes promising pages
- family-level output quality improves over time

### Milestone 6: Search Data Closes the Loop

Target:

- performance changes the system

Signals:

- CTR rewrite flows run automatically
- family scores shift based on results
- publish thresholds evolve based on outcomes

---

## Rollout Strategy

### Rollout Rule 1

Never launch a high-volume page family before its eligibility rules and prune rules exist.

### Rollout Rule 2

Never launch a content generation family before its modules are schema-validated.

### Rollout Rule 3

Never scale a family before interlinking support exists for it.

### Rollout Rule 4

Never keep scaling a family that shows poor indexation or weak click distribution.

---

## Metrics By Phase

### Phase 1 Metrics

- entities added
- entities refreshed
- average sources per entity
- percent fields with confidence scores

### Phase 2 Metrics

- page candidates generated
- eligibility pass rate
- average page score by family

### Phase 3 Metrics

- schema validation pass rate
- content generation retry rate
- content hold rate

### Phase 4 Metrics

- orphan count
- average cluster size
- average contextual links per page

### Phase 5 Metrics

- new pages published by family
- pages refreshed by family
- pages pruned by family

### Phase 6 and 7 Metrics

- indexation rate by family
- impressions per page by family
- CTR by family
- clicks per page by family
- percent of pages driving traffic

---

## Resourcing Guidance

If implementation is staged carefully, the recommended order of engineering effort is:

1. data and schema
2. research automation
3. generator refactor
4. content schemas
5. interlinking engine
6. new page families
7. performance feedback loop

This ordering matters because the graph and page-system interfaces are foundational. Without them, scaling content generation just scales instability.

---

## Immediate Recommended Build Sequence

1. Add research and page candidate schema changes.
2. Implement evidence-backed entity acquisition.
3. Refactor generator to support page-system plugins.
4. Implement strict comparison and brewing content schemas.
5. Implement interlinking engine upgrade.
6. Launch `comparison_v2`.
7. Launch `brewing_intent`.
8. Launch `occasion_intent`.
9. Add refresh and prune automation.
10. Add performance ingestion and score calibration.
