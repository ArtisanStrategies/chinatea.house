# Configuration

## Google Search Console

To wire Google Search Console into the autonomous SEO pipeline:

1. Copy the template:

   ```bash
   cp config/gsc.yaml.template config/gsc.yaml
   ```

2. Add your GSC HTML verification code to `config/gsc.yaml`:

   ```yaml
   verification_code: "YOUR_CODE_HERE"
   ```

   The verification meta tag will be rendered on every page during the next build.

3. Choose an authentication method:

   **OAuth (recommended if you already have a refresh token)**
   - Set these environment variables in a `.env` file or your shell:
     ```bash
     GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
     GOOGLE_CLIENT_SECRET=your-client-secret
     GOOGLE_REFRESH_TOKEN=your-refresh-token
     ```
   - Set `credential_type: "oauth"` in `config/gsc.yaml`.

   If you already have OAuth credentials in `agswebsite/scripts/search-console/.env`,
   you can run chinatea.house GSC commands from that directory so the `.env` is loaded:

   ```bash
   cd /Users/josephw/MoneyGenerating/agswebsite/scripts/search-console
   PYTHONPATH=/Users/josephw/MoneyGenerating/chinateahouse \
     python -m execution.cli --db /Users/josephw/MoneyGenerating/chinateahouse/data/canonical/tea.db gsc test-connection
   ```

   **Service account**
   - Create a service account in [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the **Google Search Console API**.
   - Download the JSON key and save it to `config/gsc-service-account.json`.
   - Add the service account email as an **Owner** of your GSC property.
   - Set `credential_type: "service_account"` in `config/gsc.yaml`.

4. Test the configuration:

   ```bash
   python -m execution.cli gsc verify-config
   python -m execution.cli gsc test-connection
   ```

5. Fetch performance data:

   ```bash
   python -m execution.cli gsc fetch-performance
   ```

6. Find pages that need title/meta rewrites:

   ```bash
   python -m execution.cli gsc underperforming
   ```

**Never commit `config/gsc.yaml`, service account keys, or `.env` files.** They are ignored by `.gitignore`.
