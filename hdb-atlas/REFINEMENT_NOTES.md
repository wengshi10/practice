# Webpage refinement for review

No code push or webpage publication is authorized by this document. All changes are prepared locally for the user's explicit approval.

## Requested comments implemented

- Rename the masthead and footer to **HDB Singapore** and replace the H glyph with a drawn house icon.
- Remove the `YOUR LENS` icon, label and `All Singapore` summary from the fixed filters.
- Give the filter/navigation band a distinct sage background with a dark-theme counterpart.
- Replace the `2017 = 100` line view with yearly percentage-change bars relative to the 2017 annual median. Negative changes remain visible. Outline 2026 with dashes and label it January–October only.
- Use rounded, regular numerical axes; the all-data monthly price chart uses SGD 200,000 increments.
- Annotate the lowest and highest visible monthly medians and show the active growth-view extrema.
- Rename the monthly horizontal axis to **Month**.
- Animate the history-reveal clipping rectangle over a stable full-history line path and scale, preserving previous years during playback. Resume from the current selected year; restart after the end.
- Use a clear sequential blue price palette for map symbols, heatmap cells and town ranking bars. Ranking bars are thicker, span the available width, and retain a zero baseline so differences are not exaggerated.
- Replace percentile whiskers with conventional 1.5×IQR Tukey boxplots. Whiskers end at actual observed values within the fences. Outlier counts are exact; displayed marks are capped at 160 per group for legibility and disclosed.
- Add verified coordinates for all 179 primary schools and an independently toggled school marker layer.
- Add V7: the same complete-coordinate transaction cohort is grouped by common amenity-distance bands under an MRT/school/hawker selector; show distributions, medians, counts and unadjusted near/far comparisons.
- Add a descriptive within-comparable-group contrast matching town, flat type, building-age band and floor-area band. Report only groups with ≥5 near and ≥5 far sales, with explicit weighting and causal limitations.
- Add V8: lease/accessibility bubbles grouped by five-year remaining-lease band and amenity-distance band, using median lease and median price/m²; bubble area represents sales count, with groups needing at least five sales.
- Link distance-band and bubble selections to a geocoded HDB block map.
- Add neighbourhood presentation subviews for the amenity map, price/distance distributions, and ageing/accessibility relationship.
- Preserve the historical six-dataset records. Only coordinates are enriched through user-approved OneMap; no replacement price or property data is fetched.

## Data preparation on the user's laptop

The public GitHub source continues to exclude all uploaded, processed and geocoded datasets. After pulling an approved source update, keep the original six files locally in `datasets`, then run:

```powershell
py scripts\prepare_data.py .\datasets
py scripts\geocode_onemap.py --workers 4
py scripts\build_accessibility.py
py -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open `http://localhost:8000/`. The geocoder caches results and resumes if interrupted. Run with `--retry-unmatched` for unresolved-address retries. Optional OneMap API credentials belong in the local `ONEMAP_TOKEN` environment variable, never in Git. API failures are not accepted as coordinate matches.

## Interpretation

The accessibility comparison has a separate 2025/2026 year selector, defaulting to the full 2025 year, and its own building-age selector. It shares town, flat-type and property-range filters with the rest of the webpage. It uses current address coordinates and the uploaded amenity snapshots. It cannot reconstruct historical opening/closure dates, walking routes, a causal accessibility premium, or an isolated offset to depreciation.

Town price symbols remain HDB town summaries anchored to matching planning-area names, as explicitly labelled; they have not been silently converted into a planning-area choropleth. Schools retain their uploaded DGP classifications for inventories while markers and nearest-school distances use verified address coordinates.

## Follow-up Word document edits

- Remove the masthead subtitle, shorten the hero copy, rename the introduction and chart sections, and move descriptions beneath titles.
- Enable multiple period, flat-type and town selections, including links preserving multiple selections.
- Combine 1 ROOM and MULTI-GENERATION as Others in visual analyses without rewriting the raw JSON or original CSV export labels.
- Move the vertical trend legend beside the plot and selected-series extrema below it.
- Add a least-squares scatterplot line, using all eligible filtered records, with fit controls and R².
- Label medians on height and accessibility boxplots.
- Display all towns in two matrix panels without an inner vertical scrollbar.
- Expand comparison years to 2017–2026 and All years; retain the later-snapshot limitation and match sale year in comparable strata.
- Simplify the ageing/accessibility default to equal-size points and retain sales-count sizing as an option.
- Increase font sizes and use black light-mode explanatory text, with chart titles larger than axis titles and axis titles larger than ticks.

These are local review notes; they do not authorize a push. Existing prepared data and geocoding caches remain compatible, so this UI update does not require another OneMap run.
