# Retraction cascades — acquisition

Use Crossref's production Retraction Watch paths, not the deprecated Labs feed:

- `https://gitlab.com/crossref/retraction-watch-data`
- `https://api.crossref.org/v1/works?filter=update-type:retraction`
- `https://developers.openalex.org/`
- `https://www.semanticscholar.org/product/api`

Expected local inputs are a frozen Retraction Watch CSV, Crossref response
pages, OpenAlex citing-work pages, and Semantic Scholar citation responses.
Record API keys only through environment variables and never in manifests.

