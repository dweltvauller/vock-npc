# VOCK Character Table

A single reference table covering every character VOCK tracks for Fallout 2 voice
acting, cross-referenced with the [Fallout Wiki's Fallout 2 characters
page](https://fallout.fandom.com/wiki/Fallout_2_characters) so the full vanilla
cast is represented even where VOCK has no plans (yet).

Live columns: name, dialogue-file/prefix IDs, location, mod, production status,
casting status, voice actor, voice type, TH-audio and float-audio completion
(recorded/total), three auto-picked audition lines (A/B/C), notes (concat bugs,
forked scripts, audit links), a Fallout Wiki link, and the Talking Head portrait.

## Files

- `data/character_table.csv` — the flat data file. Open in Excel/Sheets, or load
  into anything else.
- `data/character_table.json` — same data, used by `index.html`.
- `data/wiki_roster.tsv` — cached raw extract from the Fallout Wiki page
  (section, character name, dialogue file). Re-fetch and overwrite this if the
  wiki page changes.
- `images/` — Talking Head portraits copied from `../TH Images/` and renamed to
  `<msg_stem>.<ext>` so they can be looked up programmatically. Not every
  character has a portrait yet — the TH Images folder only covers a portion of
  the roster.
- `scripts/build_table.py` — regenerates everything above. **This is the source
  of truth's source** — don't hand-edit the CSV/JSON, edit the underlying VOCK
  files (characters.py, audit files, CREDITS.md, float_filter.cfg, va-scripts)
  and re-run the script instead.
- `index.html` — a standalone, filterable, sortable browser for the table.
  Works straight off GitHub Pages (or any static host) with no build step —
  it just fetches `data/character_table.json` and `images/*` relative to
  itself. Uses [Tabulator](https://tabulator.info/) (loaded from jsDelivr) for
  the grid: per-column search boxes, a quick-search box, status/casting
  dropdown filters, a toggle for the full wiki roster (hidden by default since
  most of those rows have no VOCK data), and a row-expand arrow for the full
  audition lines + notes that don't fit in the grid.

## Regenerating

```
cd scripts
python3 build_table.py
```

Re-run any time `characters.py`, an audit file, `CREDITS.md`,
`float_filter.cfg`, a `va-scripts/*.md`, `msg/`, `msg/pending/`, `wav/`, or
`TH Images/` changes. It's fully deterministic — nothing is preserved from a
previous run except what's re-derived from those source files.

## Known data-quality caveats (read before trusting a row blindly)

- **Audition lines for untagged NPCs are auto-picked from vanilla RPU dialogue
  text**, not curated. They're a starting point for casting calls, not a
  finished script — a human should sanity-check them (the "look" description
  line is filtered out, but a few narration-flavored lines can still slip
  through for characters that don't have a `va-scripts/*.md` yet).
- **Voice Type is only filled in where a `va-scripts/*.md` file already states
  a direction** (e.g. "Adult male, ..."). It is not inferred for the ~130
  characters without a VA script — left blank rather than guessed.
- **TH Audio / Float Audio totals** only exist for characters with an audit
  file (`tags_total` in its frontmatter). Recorded counts come from actual
  `.wav` files in `vock-fo2/wav/`, split against `float_filter.cfg`'s ranges.
  For NPCs with no audit yet, these are blank.
- **Location** comes from (in order of preference) the audit file, then
  `CREDITS.md`, then the Wiki roster match by name+dialogue-file, then a
  looser wiki match by name alone. A handful of characters (mostly ones the
  Wiki lists without a location bucket, or edge cases in name matching) are
  still blank — worth a manual pass.
- **"Not in VOCK scope" rows** are wiki characters with no corresponding entry
  in `characters.py` — mostly filler NPCs with no unique dialogue, or ones
  VOCK's RPU baseline handles differently than the wiki's vanilla-game
  description. These are hidden by default in `index.html`.
- Conversely, some `characters.py`/RPU entries have no Wiki match at all
  (RPU adds/changes some things vs. vanilla) — expected, per Fede.
- TH Images matching is name-based fuzzy matching (handles "Dr."/"Doc" vs
  "Doctor", articles, punctuation, curly quotes) — about 128/196 VOCK-scope
  characters matched a portrait; the rest simply aren't in the TH Images
  folder yet.

## Publishing to GitHub Pages

This folder is meant to become its own repo (same pattern as `vock-fo2` next
to the `vock` tool repo — see project memory `vock_project_structure`). Once
pushed, enable GitHub Pages on the repo (Settings → Pages → Deploy from
branch → `main` / root) and `index.html` becomes the live filterable table at
`https://<user>.github.io/<repo>/`.
