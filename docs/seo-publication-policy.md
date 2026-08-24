# SEO Publication Policy

This policy supersedes the project's original page-volume strategy. Database
rows and mechanically valid combinations are not automatically public pages.

## Indexable page families

- Homepage and navigation hubs
- Tea categories and regions
- Individual tea profiles with complete canonical metadata
- Brewing and occasion guides
- Evergreen editorial guides
- Useful interactive tools and the documented dataset

Every indexable page must have a unique purpose, a crawlable internal path, one
canonical URL, one primary heading, honest structured data, and no broken local
references. The generated-site verifier enforces the machine-checkable parts.

## Comparison pages

The database may contain all valid tea pairs for analysis. Only comparison IDs
listed in `execution/build/publication.py` can be rendered or linked publicly.
Those pages remain `noindex, follow` until their claims and prose receive an
independent editorial review. Adding a pair requires both a publication-policy
change and a regression-test update.

## Evidence and claims

- Never generate ratings, review counts, reviews, offers, or freshness dates.
- Treat flavor, price, caffeine, and brewing values as comparative guidance;
  disclose their variability on the page.
- Prefer primary sources and render citations visibly when sources are added.
- Do not make medical promises.
- Use Organization authorship only for content maintained by the project; do
  not imply a named expert or first-hand testing that did not occur.

## Release gate

A release must pass data validation, unit tests, a clean full build, and
`scripts/verify_build.py`. Search Console performance is a feedback signal, not
permission to create unreviewed page families.
