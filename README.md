# What Makes an HDB Flat Expensive?

**HDB Singapore** is a standalone interactive webpage telling the story of Singapore resale housing. It is built from the six supplied datasets, independently of earlier branch work. The webpage has no framework, CDN, external basemap or runtime internet dependency. User-approved OneMap geocoding enriches the uploaded block and school addresses during preparation; prices and amenity records still come only from the uploads.

## Open the webpage

The public GitHub branch contains source only. Keep your six original CSV/GeoJSON files locally in the repository-root `datasets`, then run `python scripts/prepare_data.py datasets` before starting the server. Run the coordinate preparation commands below to enable school markers and the new accessibility charts. All uploaded and derived data assets remain excluded from Git.

Python 3 is sufficient:

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open **http://127.0.0.1:8000/**. Serve the files over HTTP rather than opening `index.html` directly, because the page fetches its local JSON data. Any static host can serve the `dist` folder.

## Six connected chapters

1. Monthly price trends, price per square metre, and annual percentage-growth bars relative to 2017.
2. Singapore planning boundaries with town price symbols and a linked ranking.
3. Transaction scatterplot: lease, floor area, and building age; horizontal drag selects a property range.
4. Storey-band price distributions, with a building-age selector.
5. Town × flat-type heatmap, plus model comparisons.
6. MRT exits, hawker locations, primary-school markers, common-cohort amenity-distance boxplots, and lease/accessibility bubbles with a linked block map.

Shared period, flat-type and town filters support multiple selections and update exact statistics, animated charts and CSV export. The context ranking retains all towns. The matrix retains all town/type combinations and highlights the selection. The time chart respects selected periods, leaves gaps between unselected years, and uses a reveal cursor for playback without changing the filtered transaction cohort. The amenity inventory follows directly named selected towns unless a planning area is explicitly chosen. Its points remain snapshot records, independently of the price period.

Dark mode, responsive layouts, scroll entrances, chart transitions, hover details, map pan/zoom, timeline playback and a six-minute presentation view are included. Chapter 6 has presentation subviews for the amenity map, price/distance distributions and ageing/accessibility bubbles. Presentation arrow keys move between chapters; the timed tour can pause or resume. This is a webpage, not a generated video. Narration must be recorded by the students themselves.

## Data integrity

- 242,259 transactions, January 2017 to October 2026. 2026 is partial.
- 242,256 records join to building information on normalized block + street. Three unmatched block 82 MacPherson Lane sales remain in price analysis.
- Transaction-level price/m² is calculated before taking medians.
- All summaries use every filtered row. Only scatter dots are sampled, deterministically, to at most 2,400. The displayed denominator and methodology disclose this.
- Building age uses completion year and sale year. Storey groups use the midpoint of the recorded storey range with nonoverlapping thresholds.
- Sparse time-series months are not interpolated across missing observations. Timeline playback animates a reveal clip over a stable full-history path and scale, preserving prior history instead of redrawing it. The monthly axis uses rounded ticks; extrema are annotated. Growth bars show cumulative annual-median change versus 2017, and 2026 has a dashed outline.
- 55 planning polygons retain holes and multipolygons. Price symbols anchor HDB town names to matching planning areas; they do **not** spatially assign sales. Central Area and Kallang/Whampoa remain in the ranking without map symbols.
- 613 MRT exit records and 129 hawker records are assigned to areas by point-in-polygon. Exit counts are not unique station counts; hawkers retain all uploaded statuses.
- 179 primary schools retain their recorded DGP area classification for inventories; verified geocoded addresses provide individual map markers. The school file contains 337 schools overall.
- HDB and school coordinates are absent in the raw uploads. With explicit user approval, OneMap Search resolves their addresses to WGS84 and SVY21 coordinates. Exact block/road matches and school postal-code matches are checked; materially ambiguous addresses are not guessed. All geocoded datasets and caches stay local.
- Nearest-amenity distances are Euclidean in EPSG:3414, not walking routes. The distance selector preserves one common complete-coordinate cohort across MRT exits, primary schools and existing/interim hawkers. Under-construction hawkers are excluded from distance calculations.
- The comparison uses a separate 2017–2026 or all-years selector and building-age selector, while sharing town, flat type and property-range filters with the historical charts. 2026 is partial.
- Tukey boxplots use Q1, median, Q3, and whiskers ending at observed values within 1.5×IQR fences. All outlier counts are exact; at most 160 outlier marks per group are drawn for clarity.
- Lease/accessibility bubbles aggregate 5-year lease groups × distance bands, require at least five sales, use median lease and price/m², and use equal-size points by default, with optional transaction-count sizing by point area.
- The within-comparable-group contrast matches sale year, town, flat type, 10-year building-age bands and 20m² floor-area bands. Strata require at least five near (<400m) and five far (≥1200m) sales. The displayed contrast is exp(weighted average of log near/far median-price ratios) − 1, weighted by the smaller count in each stratum. This is descriptive, not causal.
- Amenities are later snapshots and do not reconstruct historical accessibility.
- No causal effects, inflation adjustment, repeat-sales indices, or predictions are claimed.

## Reproduce the preparation

Place the six original uploaded CSV/GeoJSON files in one folder and run:

```sh
python scripts/prepare_data.py /path/to/uploaded-datasets
```

The script uses the Python standard library only. It writes `dist/metadata.json` (including SHA-256 source fingerprints) and the complete coded `dist/transactions.json`. `dist/app.js` documents the code-column order through metadata. The original assignment PDF and Word template inform the presentation structure and are not analytic data.

## Add approved address coordinates and accessibility analysis

After generating the base JSON files, run:

```sh
python scripts/geocode_onemap.py --workers 4
python scripts/build_accessibility.py
```

The first command calls OneMap Search using only uploaded school postal codes and HDB block addresses, validates returned address fields, and caches results in `work/onemap-cache.json`. It can take several minutes. Re-running resumes from the cache. `--retry-unmatched` retries unresolved addresses. OneMap may require an account/token or impose rate limits; an optional `ONEMAP_TOKEN` environment variable supplies a token without writing it to source. API authentication failures are not treated as coordinate matches.

The second command generates `dist/accessibility.json` with matched school markers, block coordinates, nearest-amenity distances and coverage. Every derived JSON asset and coordinate cache is ignored by Git. Serve the webpage after both commands finish to load the new analysis. No coordinates are substituted for unresolved addresses.

The full school match count, block match count, projection validation error and unmatched addresses are recorded in the generated file. The map and price charts still work without enrichment; the accessibility panels clearly show that verified coordinates are required.

## Verification

JavaScript syntax checked with `node --check dist/app.js`. Browser validation covers exact count/median baselines, combined filtering against an independent predicate, scatter brushing and clearing, theme switching, methodology dialog, presentation navigation, and a 390px mobile viewport with no page-wide overflow. Refinement checks verify rounded ticks, annual growth values and dashed 2026 styling, preservation of the line path during playback, standard boxplot fences and outliers, all 179 school markers, identical amenity comparison cohort counts, linked distance selection and the new 720p presentation subviews. Nearest distances are independently checked with a KD-tree implementation to within the 0.005m rounding precision. There were no browser JavaScript errors.

Optional Playwright checks are in `tests/browser_check.py`; edit the browser path and output paths for another machine. The production webpage has no dependency on Playwright.

See `PRESENTATION_GUIDE.md` for a six-minute walkthrough and report notes.

## Dataset references supplied in `infrormation.docx`

These links document the uploaded datasets' provenance; no replacement datasets are fetched by the webpage.

- [HDB resale transactions](https://data.gov.sg/datasets?query=resale+flat&resultId=d_8b84c4ee58e3cfc0ece0d773c8ca6abc)
- [HDB Property Information](https://data.gov.sg/datasets?query=hdb+property&resultId=d_17f5382f26140b1fdae0ba2ef6239d2f)
- [MRT station exits](https://data.gov.sg/datasets?query=lta+mrt&resultId=d_b39d3a0871985372d7e1637193335da5)
- [URA planning-area boundaries](https://data.gov.sg/datasets?query=URA+Planning+Area+Boundaries&resultId=d_2cc750190544007400b2cfd5d7f53209)
- [Hawker centres](https://data.gov.sg/datasets?agencies=National+Environment+Agency+(NEA)&resultId=d_4a086da0a5553be1d89383cd90d07ecd)
- [General information of schools](https://data.gov.sg/datasets?query=moe+general+information+of+school&resultId=d_688b934f82c1059ed0a6993d2a829089)
- [OneMap](https://www.onemap.gov.sg/) — user-approved address-coordinate lookup only.

## Latest requested usability edits

The masthead uses only HDB Singapore; the hero names SC4024 Data Visualisation. All original flat types are retained, including 1 ROOM and MULTI-GENERATION; there is no combined Others category. The vertical trend legend supports selection, and visible monthly extrema are calculated only from selected categories. A least-squares best-fit line uses every eligible filtered sale, not just sampled scatter dots; the displayed R² is descriptive. Boxplot medians are labelled directly. The town/type matrix uses two side-by-side panels, showing all 26 towns without an internal vertical scrollbar. Earlier accessibility years compare historical sale prices with later amenity snapshots, so they do not reconstruct historical availability. Typography follows chart title > axis title > numeric tick label, and light-mode explanatory text is black.

## Latest label and emphasis update

Monthly price and price/m² trend titles and axes use the requested descriptive labels. Trend and scatter numeric ticks omit currency symbols; extrema and median annotations retain them. Lowest summaries are red and highest summaries are green, with contrasting dark-theme colours. The original flat categories are restored without changing any prepared data files. Unselected towns use neutral grey symbols and ranking bars. The observed-difference and ageing-comparison narrative blocks are removed from the webpage; the remaining methodology still documents analytical limitations. Building age is labelled at Sale rather than Scale, because it is transaction year minus completion year.

## Copy and methodology simplification

KPI descriptions use brief median definitions. The chart legend is boxed, playback is labelled Play, quick-comparison buttons and the requested narrative/coverage text are removed from the main page. Coordinate coverage remains available in Data & Methodology. The Flat Model bar chart now ranks median **total resale price (SGD)** rather than median price/m², matching its requested caption; this uses the same transaction data and keeps the minimum five-sale rule, disclosed on hover. Accessibility axes and property-map labels use the latest requested wording. The methodology dialog follows the supplied content, with the corrected definition that outliers are beyond the whiskers, not merely beyond Q1/Q3 boxes. No data preparation or geocoding rerun is needed.

## Repository layout

The webpage now lives directly in the `practice` repository root. Run all commands above from `practice`; no `cd hdb-atlas` step is needed.

## Updating an existing local checkout

After pulling this restructuring, move any remaining ignored local contents from `hdb-atlas/datasets`, `hdb-atlas/work` and generated JSON files from `hdb-atlas/dist` to the matching root folders. Preserve `work/onemap-cache.json` to avoid repeating geocoding. See `MIGRATION.md` for safe PowerShell commands that refuse to overwrite files.
