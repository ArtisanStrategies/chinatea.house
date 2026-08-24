# Production Operations

## Canonical hostname

Cloudflare Pages does not support domain-level rules in its `_redirects` file.
Configure this once in **Cloudflare Dashboard → Bulk Redirects**:

- Source: `https://www.chinatea.house`
- Target: `https://chinatea.house`
- Status: `301`
- Enable subpath matching, preserve path suffix, and preserve query string.

Keep the `www` DNS record proxied. After deployment, verify both the root and a
nested path:

```sh
curl -I https://www.chinatea.house/
curl -I https://www.chinatea.house/guide/
```

Both responses must be `301` with the equivalent apex URL in `Location`.

Reference: <https://developers.cloudflare.com/pages/how-to/www-redirect/>

## Release contract

Production deploys are clean snapshots. The workflow creates the database from
seed data, validates it, runs regression tests, builds every public route, then
checks links, JSON-LD, routing files, and the comparison-page publication cap
before uploading to Cloudflare Pages.

Unknown paths are handled by the generated top-level `404.html`. Do not remove
that file: Cloudflare Pages otherwise assumes the project is a single-page app
and serves the homepage for missing URLs.
