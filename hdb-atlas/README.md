# What Makes an HDB Flat Expensive?

**HDB Atlas** is a standalone interactive webpage telling the story of Singapore resale housing. It is built from the six supplied datasets, independently of earlier branch work. No framework, build step, account, API key, external basemap, geocoder, CDN, or runtime internet connection is required.

## Open the webpage

The public branch includes source only. Before opening the page, place your six uploaded datasets in a local folder and run `python scripts/prepare_data.py /path/to/uploaded-datasets` to generate the private JSON assets. These assets are intentionally ignored by Git.

Python 3 is sufficient:

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open **http://127.0.0.1:8000/**. Serve the files over HTTP rather than opening `index.html` directly, because the page fetches its local JSON data. Any static host can serve the `dist` folder.

## Six connected chapters

1. Monthly price trends, price per square metre, and indexed growth.
2. Singapore planning boundaries with town price symbols and a linked ranking.
3. Transaction scatterplot: lease, floor area, and building age; horizontal drag selects a property range.
4. Storey-band price distributions, with a building-age selector.
5. Town × flat-type heatmap, plus model comparisons.
6. MRT exits, hawker locations and primary-school area inventories.

Shared period, flat-type and town filters update exact statistics, animated charts and CSV export. The context ranking retains all towns. The matrix retains all town/type combinations and highlights the selection. The time chart retains the history up to the selected year. The amenity inventory follows directly named selected towns unless a planning area is explicitly chosen. Its points remain snapshot records, independently of the price period.

Dark mode, responsive layouts, scroll entrances, chart transitions, hover details, map pan/zoom, timeline playback and a six-minute presentation view are included. Presentation arrow keys move between chapters; the timed tour can pause or resume. This is a webpage, not a generated video. Narration must be recorded by the students themselves.

## Data integrity

- 242,259 transactions, January 2017 to October 2026. 2026 is partial.
- 242,256 records join to building information on normalized block + street. Three unmatched block 82 MacPherson Lane sales remain in price analysis.
- Transaction-level price/m² is calculated before taking medians.
- All summaries use every filtered row. Only scatter dots are sampled, deterministically, to at most 2,400. The displayed denominator and methodology disclose this.
- Building age uses completion year and sale year. Storey groups use the midpoint of the recorded storey range with nonoverlapping thresholds.
- Sparse time-series months are not interpolated across missing observations.
- 55 planning polygons retain holes and multipolygons. Price symbols anchor HDB town names to matching planning areas; they do **not** spatially assign sales. Central Area and Kallang/Whampoa remain in the ranking without map symbols.
- 613 MRT exit records and 129 hawker records are assigned to areas by point-in-polygon. Exit counts are not unique station counts; hawkers retain all uploaded statuses.
- 179 primary schools are classified by their recorded DGP area. The school dataset contains 337 schools overall. No school point locations are invented.
- HDB and school coordinates are absent, so amenity distance premiums cannot be estimated from these files alone. No external enrichment is used. Amenities are later snapshots and do not reconstruct historical accessibility.
- No causal effects, inflation adjustment, repeat-sales indices, or predictions are claimed.

## Reproduce the preparation

Place the six original uploaded CSV/GeoJSON files in one folder and run:

```sh
python scripts/prepare_data.py /path/to/uploaded-datasets
```

The script uses the Python standard library only. It writes `dist/metadata.json` (including SHA-256 source fingerprints) and the complete coded `dist/transactions.json`. `dist/app.js` documents the code-column order through metadata. The original assignment PDF and Word template inform the presentation structure and are not analytic data.

## Verification

JavaScript syntax checked with `node --check dist/app.js`. Browser validation covered exact count/median baselines, combined filtering against an independent predicate, scatter brushing and clearing, theme switching, methodology dialog, presentation navigation, and a 390px mobile viewport with no page-wide overflow. There were no browser JavaScript errors.

Optional Playwright checks are in `tests/browser_check.py`; edit the browser path and output paths for another machine. The production webpage has no dependency on Playwright.

See `PRESENTATION_GUIDE.md` for a six-minute walkthrough and report notes.
