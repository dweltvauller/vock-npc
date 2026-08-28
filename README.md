# VOCK Character Table

A single reference table covering every character VOCK tracks for Fallout 2 voice
acting, cross-referenced with the [Fallout Wiki's Fallout 2 characters
page](https://fallout.fandom.com/wiki/Fallout_2_characters) so the full vanilla
cast is represented even where VOCK has no plans (yet).

Live columns: name, dialogue-file/prefix IDs, location, mod, production status,
casting status, voice actor, voice type, TH-audio and float-audio completion
(recorded/total), three auto-picked audition lines (A/B/C), notes (concat bugs,
forked scripts, audit links), a Fallout Wiki link, the Talking Head portrait,
(where one exists) the voice actor from the third-party **THAT** ("Fallout 2
Talking Heads Mod") casting-call project, kept separate from VOCK's own casting
since it's a different mod with its own cast, and a companion flag (see below).

The `Mod` column is a single, mutually-exclusive value: `FO2`, `RPU`, `THAT`,
or `VOCK`, in that priority order. `FO2`/`RPU` mean the character already has
spoken audio shipped with vanilla Fallout 2 itself, or added by the
(unofficial) Restoration Project; `THAT` means the character is on the third-party Talking Heads mod's roster
at all (whether or not a voice actor is confirmed in the public listings --
`THATVoiceActor` is left blank when unconfirmed, but the Mod tag still applies). `VOCK` only shows when none of those three apply --
VOCK doesn't re-voice a character that already has audio elsewhere. Source for
FO2/RPU: a short list Fede supplied directly (2026-08-28) -- see
`FO2_RPU_VOICED` in `scripts/build_table.py`. Example: John Cassidy is `RPU`
(Restoration Project voiced him; vanilla FO2 did not). One entry in that list
(`gcpacoff`, the Enclave communications officer, FO2-voiced) has no
`characters.py` row yet, so it isn't reflected in the table.

`Companion` / `CompanionMod` are separate from the `Mod` column above --
`Mod` is about who *voiced* a character, `Companion`/`CompanionMod` is about
whether the game lets you recruit them into your party. `Companion` is `Yes`
for vanilla FO2 companions (per the Wiki's "Player characters" section --
Cassidy, Sulik, Vic, Marcus, Myron, Goris, Lenny, Skynet, Davin, Laddie,
Dogmeat, Pariah dog, K-9, Robodog, Miria, Brahmin Bess) plus everyone added as
a companion by the **RPCE** mod. `CompanionMod` is blank for vanilla
companions (no mod needed) and `RPCE` for characters recruited via
[Restoration Project - Companion Expansion](https://www.nexusmods.com/fallout2/mods/70),
which turns 6 existing NPCs into full companions and expands a 7th (Miria, via
its "Better Miria" integration): Lara, Doc Jones, Angela Bishop, Mason, Lil'
Jesus Mordino, Christopher Wright, and Miria. RPCE also introduces 3 brand-new
characters with no `characters.py`/Wiki entry at all yet (Red-Knuckle Rhea,
Ceri, and an unnamed Den slave) -- not reflected in this table since there's
no msg_stem or dialogue source to key them on.

## Files

- `data/character_table.csv` — the flat data file. Open in Excel/Sheets, or load
  into anything else.
- `data/character_table.json` — same data, used by `index.html`.
- `data/wiki_roster.tsv` — cached raw extract from the Fallout Wiki page
  (section, character name, dialogue file). Re-fetch and overwrite this if the
  wiki page changes.
- Source: `vock-fo2/THAT.md` — a reference table Fede compiled from the public
  Casting Call Club listings for THAT (the *Fallout 2 Talking Heads* mod, a
  third-party project, not VOCK). Feeds the `THATVoiceActor`/`THATLink` columns.
  Per THAT.md's own disclaimer: third-party info, may be outdated, blank means
  no confirmed actor was found in the public listings — treat as a lead, not a
  confirmed credit.
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
- **Kaga (`eckaga1`-`eckaga5`) shows identical TH/Float audio totals on all 5 rows** — this is correct, not a bug: those 5 files share one continuous tag space (`kaga1`-`kaga49`) per VOCK convention, so the combined total is the only meaningful number.
- TH Images matching is name-based fuzzy matching (handles "Dr."/"Doc" vs
  "Doctor", articles, punctuation, curly quotes) — about 128/196 VOCK-scope
  characters matched a portrait; the rest simply aren't in the TH Images
  folder yet.
- **RPCE's 3 new companions aren't rows yet** (Red-Knuckle Rhea, Ceri, Den
  slave) — they have no `characters.py` entry, msg_stem, or Wiki page to key
  on. If/when VOCK starts tracking them, add `characters.py` rows first and
  they'll pick up automatically once their stems are added to
  `RPCE_COMPANION_STEMS`.

## Publishing to GitHub Pages

This folder is meant to become its own repo (same pattern as `vock-fo2` next
to the `vock` tool repo — see project memory `vock_project_structure`). Once
pushed, enable GitHub Pages on the repo (Settings → Pages → Deploy from
branch → `main` / root) and `index.html` becomes the live filterable table at
`https://<user>.github.io/<repo>/`.
