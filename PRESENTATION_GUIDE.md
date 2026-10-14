# Six-minute walkthrough

Use a 1280 × 720 browser recording. The supplied assignment limits the video to six minutes and 720p, asks both students to introduce themselves, and requires each student's own narration. The webpage's presentation mode supports the walkthrough; it does not generate a video or substitute narration.

Introduce the title and both presenters briefly before the first explanation, within the six-minute total. Practice and shorten each chapter to fit the introduction and closing. The timed webpage tour allocates one minute per chapter as a rehearsal aid; use manual navigation when narration requires a different pace.

| Time | Presenter | Chapter | Demonstration and message |
| --- | --- | --- | --- |
| 0:00–1:00 | Student 1 | Market | Introduce title/names, explain recorded sales, switch nominal price to annual percentage-growth bars, play a few years. In the all-home lens, annual median price is $410,000 in 2017 and $628,000 in 2025, a 53.2% observed change. Housing composition matters; this is not a repeat-sales index. |
| 1:00–2:00 | Student 1 | Location | Compare town price medians and transaction counts; click a town and clear it. Explain town symbols on corresponding planning areas and why they are not a transaction choropleth. |
| 2:00–3:00 | Student 1 | Property | Compare all homes, then 4-room, then one town. Hover a sale; brush a lease range. Explain that controls make comparisons more meaningful and the scatter sample does not replace complete summary statistics. |
| 3:00–4:00 | Student 2 | Height | Change building-age group. Explain median, middle 50%, 1.5×IQR whiskers, outliers and distribution overlap. Avoid calling raw differences causal floor premiums. |
| 4:00–5:00 | Student 2 | Mix | Select a matrix cell. Show how a location/type selection coordinates with the rest of the page. Mention that cells with few sales need care. In normal webpage mode, show model comparisons if useful. |
| 5:00–6:00 | Student 2 | Neighbourhood | Show the school-marker layer, then switch the presentation subview to Price & distance and Ageing & access. Change the amenity selector while retaining the same transaction cohort. Explain straight-line distance, verified coordinate coverage, unmatched addresses and later snapshots. Observed associations do not establish causation. |

## Report template notes

Keep the report within the supplied two-page limit, use at least 11pt font, and complete actual group number, names and contribution details yourself. These are preparation notes, not a submission-ready report or an assertion of student authorship.

- **Objectives:** Explore price evolution and associations with recorded housing characteristics and location; show the limits of accessibility analysis from the supplied data.
- **Contributions:** Record each student's actual design, analysis, implementation and narration work. Disclose external technical assistance according to course expectations.
- **Novelty:** A coordinated property-range brush connecting the individual-sale view to complete summary charts; an explicit distinction between town price geography and planning-area amenity geography; a timed presentation view preserving the exploration controls.
- **Technical challenges:** Reliable address-key joins, partial-year handling, exact filtered medians, performant sampled canvas plotting, polygon holes, snapshot amenity assignment and responsive SVG layouts.
- **References:** List the six dataset filenames and actual source web links from your own dataset provenance. The source links supplied in infrormation.docx are included in README.md; cite OneMap for approved coordinate enrichment. Include the recommended outline and any tools/assistance used where appropriate.

## Useful verified baselines

All years, all towns, all types:

- Transactions: 242,259.
- Median recorded price: SGD 505,000.
- Median transaction-level price/m²: SGD 5,326.0869565.
- Median remaining lease: 73.75 years.
- Building matches: 242,256; unmatched: 3.

The final year is January–October 2026. Prefer 2025 for full-year cross-sectional comparisons. Snapshot amenities cannot be projected backward into earlier years.
