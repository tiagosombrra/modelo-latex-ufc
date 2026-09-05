# V3 Object Typography Decision

Updated: 2026-09-05
Status: ACCEPTED — AUTOMATED REGRESSION GREEN

## Decision

The v3 object typography contract distinguishes upper identification/title from lower auxiliary text.

Accepted project behavior:

- upper illustration/table/object identification/title: 12 pt, single spacing;
- lower source: 10 pt, single spacing;
- lower legend/note/other auxiliary information: 10 pt, single spacing where applicable;
- identification/title/source/legend/note remain constrained to object width rather than page width.

## Authority basis

The UFC normalisation landing page continues to publish the UFC academic-work guide as institutional guidance. The guide distinguishes general 12 pt body text and smaller legends/sources from the separately described upper illustration/table identification/title. The two recovered librarian-review layers independently mark upper figure/table titles as body-size text.

This reading avoids conflating the guide's lower `legenda` exception with the upper identification/title.

## Implementation history

Initial migration `f2f5124c4adcb34069a667f1ef80c76fb17728bd`:

1. removed upper illustration/table identification/title from the reduced-font exception;
2. introduced semantically correct 12 pt rules `illustration.identification.font-size` and `table.identification.font-size`;
3. retired historical 10 pt title rule IDs through `standards/rule-migrations.json` rather than silently repurposing them;
4. updated `objects.def`, locator ownership and final-PDF measurement expectations;
5. preserved lower source/legend/note at 10 pt where applicable.

Linux `33963240297` then exposed an independent `tabularray-abnt` adapter still forcing table identification to 10 pt. Runtime correction `7ec385ebecf21ba17e59db1e7ec16d3336f4bf4c` restored body-size upper table captions while retaining reduced lower auxiliary styles.

Linux `33964421597` proved the corrected final-PDF title/source split but exposed a stale independent IBGE assertion that still expected a 10 pt table caption. Commit `a3ce2d82899162d12b06c7335b149dc2b44ecfa3` aligned that observer to the accepted 12 pt title / 10 pt lower contract.

## Acceptance evidence

Synchronized checkpoint `3f47081cbbd00a44b9ee86a6b406580e79b593c0` passed:

- Static contract `33965794475`: success;
- full Linux integration `33965794519`: success;
- Linux summary: `PASS=31 FAIL=0 SKIP=0`;
- illustration identification/title: 12 pt, PASS;
- illustration source: 10 pt, PASS;
- table identification/title: 12 pt, PASS;
- table source: 10 pt, PASS;
- object geometry: PASS;
- IBGE table subset: PASS with 12 pt caption and 10 pt source/note.

Review item 21 is therefore `PASS`. The migration is no longer pending acceptance.

## Current-edition technical boundary

The repository identifies ABNT NBR 14724:2024 as current technical authority, but exact authoritative clause text for this point is not available in the repository/public evidence corpus. This decision uses current UFC institutional guidance plus recovered UFC librarian review evidence and remains reopenable if licensed current-edition ABNT text establishes a contrary rule.

This limitation does not justify reverting the former conflation. The available institutional evidence and accepted regression distinguish upper identification/title from lower source/legend/note independently for illustrations and tables.
