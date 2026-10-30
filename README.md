# Themes Catalog API

Static JSON export. Base URL after deployment: https://yuxiaoli.github.io/themes-catalog-api/

- `api/v1/index.json`: categories, counts and limitations.
- `api/v1/editor/index.json`, `api/v1/terminal/index.json`: all available names, namespaced IDs and per-theme paths; withheld names appear separately in `excluded`.
- Select a category, look up the exact display name in `names`, then choose an ID from its list and fetch that entry's `path`. Names are not unique; never silently pick the first match.
- All `path`, `original_documents` and `license_documents` values resolve against the repository Pages root. Per-theme keys are SHA-256 of UTF-8(category + NUL + full namespaced ID), never a lossy name slug.
- Theme responses preserve functional palette/styles/CSS/conversion data and warnings; `publication` links exact necessary source documents and notices. No crawler inventories or unrelated source project files are shipped.
- TerminalColors and derived counterparts are withheld pending distribution-license verification. Official Helix file-level Vim/GPL notices are preserved with their license texts and editable source forms. See counts and reasons in indexes. This export is partial.
- Native Helix `terminal:` and `indexed:` colors are unresolved dependencies, not fabricated RGB values. Derived schemes are not lossless equivalents or accessibility guarantees.
- JSON Schema Draft 2020-12 contracts are under `api/v1/schema/`.

See [ATTRIBUTION.md](ATTRIBUTION.md). No blanket license supersedes upstream rights.
