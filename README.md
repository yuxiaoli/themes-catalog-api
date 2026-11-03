# Themes Catalog API

Static, read-only JSON export served by GitHub Pages. Fetch the published files with HTTP GET; no authentication is required. There are no server-side searches, query filters, pagination, or write operations. Filter the downloaded indexes in your client.

Pages base URL: [https://yuxiaoli.github.io/themes-catalog-api/](https://yuxiaoli.github.io/themes-catalog-api/). The root currently returns a GitHub Pages 404 page; start with the JSON catalog index below. Paths returned in JSON still resolve against this base URL.

The [OpenAPI 3.1 description](docs/openapi.json) documents requests, response fields, file discovery, and limitations. It can be imported into an OpenAPI viewer or client.

## Complete endpoint URLs

Every URL below is ready to open or fetch directly.

| Resource | URL |
| --- | --- |
| Catalog: categories, counts, limitations | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/index.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/index.json) |
| Editor names, IDs, theme paths, exclusions | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/editor/index.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/editor/index.json) |
| Terminal names, IDs, theme paths, exclusions | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/terminal/index.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/terminal/index.json) |
| Editor example: Ace Dracula (`ace/dracula`) | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/editor/themes/c6135ba3c41cde85980a8679d8a3279adc3328b089a4a2d938cebd22222581ad.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/editor/themes/c6135ba3c41cde85980a8679d8a3279adc3328b089a4a2d938cebd22222581ad.json) |
| Editor example: derived Dracula (a different ID with the same display name) | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/editor/themes/9b4f639181d334d8cc0af4db702cf3b8b308cae6e8ed4fd94fb3fb14227e9a0c.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/editor/themes/9b4f639181d334d8cc0af4db702cf3b8b308cae6e8ed4fd94fb3fb14227e9a0c.json) |
| Terminal example: Gogh Spaceduck | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/terminal/themes/907b41fd19d0ebcfa49f6b66c8a6638008c3eddfceac853fb8a3ff1845639ffa.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/terminal/themes/907b41fd19d0ebcfa49f6b66c8a6638008c3eddfceac853fb8a3ff1845639ffa.json) |
| Category-index JSON Schema (Draft 2020-12) | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/schema/index.schema.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/schema/index.schema.json) |
| Theme-response JSON Schema (Draft 2020-12) | [https://yuxiaoli.github.io/themes-catalog-api/api/v1/schema/theme.schema.json](https://yuxiaoli.github.io/themes-catalog-api/api/v1/schema/theme.schema.json) |

The index schema describes **category indexes**, not the top-level catalog index. Theme URLs are existing hashed files discovered through category indexes; a display name or namespaced ID is not a URL route.

## Find and fetch a theme

1. Fetch the catalog index and choose `editor` or `terminal` from `categories`.
2. Fetch that category's `path`. Its `entries` contain available themes; `names` maps each exact, case-sensitive display name to an **array** of namespaced IDs. Withheld records are listed separately in `excluded` with a `reason` and no download path.
3. Choose a full ID explicitly, then find the matching entry and fetch its `path`. Names are not unique; never silently pick the first match. For example, editor `names["Dracula"]` includes both `ace/dracula` and `derived/gogh/0aa8623f8cb06b648c27935591ef98c22267a35a76c2e240dd1a6b9df19f4212`.

This browser JavaScript example explicitly selects the Ace version:

```js
const base = "https://yuxiaoli.github.io/themes-catalog-api/";
async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
  return response.json();
}

const catalog = await getJSON("https://yuxiaoli.github.io/themes-catalog-api/api/v1/index.json");
const index = await getJSON(new URL(catalog.categories.editor.path, base));
const ids = index.names["Dracula"] ?? [];
const selectedId = "ace/dracula"; // Explicit choice among possible matches.
if (!ids.includes(selectedId)) throw new Error("Selected theme is unavailable");
const entry = index.entries.find(item => item.id === selectedId);
if (!entry) throw new Error("Selected ID has no available entry");
const result = await getJSON(new URL(entry.path, base));
console.log(result.theme.id, result.theme.palette, result.theme.publication);
```

All returned `path`, `publication.original_documents`, and `publication.license_documents` values resolve against the **Pages base URL**, not the current JSON URL or the domain root. For example, use `new URL(entry.path, base)`, keeping the trailing slash on `base`. Per-theme filenames are SHA-256 of UTF-8(`category + NUL + full namespaced ID`); the NUL is one zero byte. Prefer the returned path over calculating a filename.

Theme responses contain `api_version`, `category`, and `theme`. The theme has `id`, `name`, `source_id`, `source_theme_id`, `palette`, and `publication`; styles, CSS, conversion metadata, and warnings depend on its format. Use the index entry's `format`: Ace payloads do not contain a `theme.format` field. Palette values are not uniformly RGB strings; terminal palettes include an `ansi` array and native Helix colors can remain unresolved.

Missing files return HTTP 404 with a hosting error page, not a JSON API error. Check the HTTP status before parsing JSON.

## Coverage and licensing

The export is partial. The current catalog reports 1,570 available editor themes (112 excluded; 1,682 source records) and 1,251 available terminal themes (112 excluded; 1,363 source records). Read the indexes for current counts and reasons. The supported categories are `editor` and `terminal`; source formats and available records differ between them.

- TerminalColors records and derived counterparts are withheld pending distribution-license verification.
- Theme responses preserve functional palette/styles/CSS/conversion data and warnings; `publication` links exact necessary source documents and notices. No crawler inventories or unrelated source project files are shipped. Follow `original_documents` to provenance JSON containing retained source `text`, `url`, and `sha256`, and `license_documents` to license text files. An empty `original_documents` array is valid; Gogh records are retained in the theme payload, and derived Gogh editor themes also include `publication.original_record`.
- Official Helix file-level Vim/GPL notices are preserved with their license texts and editable source forms. Preserve applicable MPL/source-form obligations and file-specific terms described in the attribution notices.
- Native Helix `terminal:` and `indexed:` colors are unresolved dependencies, not fabricated RGB values. Derived schemes are not lossless equivalents or accessibility guarantees.

See [ATTRIBUTION.md](ATTRIBUTION.md). No blanket license supersedes upstream rights.

## Popularity is category metadata

Popularity is an optional flag within a category, not a third category or a
separate endpoint. Fetch the existing [terminal index](https://yuxiaoli.github.io/themes-catalog-api/api/v1/terminal/index.json)
and filter locally. Adding `?popular=true` does not filter a static Pages response.

The optional top-level `popularity` object uses metadata version `"1"` inside
API v1. Existing `entries`, IDs, paths, palette files, exclusions and category
counts are unchanged. Flags are keyed by full stable ID instead of adding fields
to the previously strict entry objects; the updated index also validates against
the original v1 schema.

- `popularity.flags[id] === true`: a confirmed member of the upstream subset.
- `false`: evaluated against that subset and not a member. This is not a quality score.
- Missing object or ID: **unknown**. Editor themes and the 112 license-unverified
  terminal entries have no assigned popularity; conversion does not transfer it.
- `order`: matched IDs in upstream declaration order, including any unavailable
  member. Intersect with `entries` before fetching. This is not a guaranteed live
  website display order: clicking Gogh's Popular filter selects Shuffle.
- `unmatched`: upstream names absent or ambiguous in this palette snapshot,
  with original one-based positions. Ambiguous matches receive no flag.
- `unavailable`: matched but withheld members, with reasons and positions.
  They remain excluded and have no fetchable palette path.

The definition is the exact `POPULAR_THEME_NAMES` set in
[Gogh's website source](https://github.com/Gogh-Co/gogh-website/blob/a5ca684f9aa82bc20ef62990eed7df9bc3408fa7/app/pages/index.vue#L499-L548),
not our own popularity research or a live vote count. Its authors describe a
September 2026 selection using several signals. We preserve their membership
without independently endorsing the cited figures. The website deployment run
[39970200009](https://github.com/Gogh-Co/gogh-website/actions/runs/39970200009)
succeeded for that revision; the palette source is independently pinned to
Gogh `3277da1a295142cd8664e0657c5a3c2a44cc520a`. All 48 names match uniquely;
none are unavailable or unmatched in this snapshot. Later upstream changes
require a reviewed metadata refresh; this static export does not track them live.

```javascript
const index = await fetch('https://yuxiaoli.github.io/themes-catalog-api/api/v1/terminal/index.json').then(r => r.json());
const flags = index.popularity?.flags ?? {};
const popular = index.entries.filter(theme => flags[theme.id] === true);
// Preserve upstream declaration order when desired:
const available = new Map(index.entries.map(theme => [theme.id, theme]));
const ordered = (index.popularity?.order ?? []).flatMap(id => available.has(id) ? [available.get(id)] : []);
```

```powershell
$index = Invoke-RestMethod 'https://yuxiaoli.github.io/themes-catalog-api/api/v1/terminal/index.json'
$index.entries | Where-Object { $index.popularity -and $index.popularity.flags.($_.id) -eq $true }
```

Reproduce with Python 3.10+: `python tools/update-popularity.py --check` and
`python -m unittest discover -s tests -v`. To independently verify the saved
48-name snapshot, download the exact upstream `index.vue` from its pinned raw
GitHub URL and pass `--source-file /path/to/index.vue`. The generator verifies
the reviewed Git blob before extracting membership, and reads only the public
export. No private catalogue data or withheld palettes are imported.

### Editor popularity evidence

The editor index remains fully available at `api/v1/editor/index.json` (1,570
published entries and 112 withheld summaries). Its popularity is unknown.
The pinned [Ace enumeration](https://github.com/ajaxorg/ace/blob/62d5ffd789b4eb29ef7c1acc17554c91c745a307/src/ext/themelist.js)
defines captions, paths, names and light/dark classification; it does not
declare popularity. The pinned Helix, CptPotato and gokayburuc source guides
describe theme collections and installation, without a comparable Popular
selection. This is evidence about the reviewed source contracts, not a claim
that no external editor-theme popularity source exists.

A future editor client can use the same optional flags contract, but must show
"popularity unavailable" when metadata is absent. It must not interpret all
editor entries as false, transfer terminal membership to converted themes, or
present an empty filtered result as an authoritative editor Popular list.
An editor Popular feature needs a separately approved upstream source or curated
definition and a documented mapping to editor IDs.
