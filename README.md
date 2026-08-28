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
  looser wiki match by name alone, then the FO2/RPU list -- then it's
  collapsed to its parent town via `base_town()` (`Vault City Courtyard` /
  `Vault City Downtown` / `Vault City Inner` all become `Vault City`, `Den
  East Side` / `Den West Side` become `Den`, etc. -- see `KNOWN_TOWNS` in
  `scripts/build_table.py`). The finer sub-area, when it said something the
  town name alone doesn't, is kept in Notes as `Area: ...` rather than
  thrown away. A few other cleanup rules keep the raw sources from leaking
  garbage into Location before that collapse happens: the Wiki's "Player
  characters" grouping (all companions listed together) is never used as a
  Location -- a companion's real hometown is preferred instead, falling back
  to blank rather than the misleading "Player characters" label. A name-only
  Wiki match is dropped entirely if that Wiki row's own dialogue file points
  to a different character (e.g. our Monty-Python "John" vs. the Wiki's
  unrelated "John"/Bcjohn.msg in Vault 15) -- same name, different NPC, no
  guess made. Audit `location` fields that are really flavor text ("Random
  encounter (Monty Python parody) -- one of Arthur's knights...") are
  detected and moved to Notes instead, falling through to a real place.
  After all that, a handful of characters (mostly ones the Wiki lists
  without a location bucket at all) are still blank — that's an honest "we
  don't know," not a bug.
- **Status** is one of exactly 5 values: `Not started`, `Tagged (pending)`,
  `Tagged, needs compile`, `Recorded`, `Not in VOCK scope` (the last one only
  ever applies to wiki-only rows).
- **WikiLink is a real link scraped directly off the Fallout Wiki's
  characters page** (`data/wiki_links.tsv`, keyed by dialogue file where the
  Wiki table gave one, else by display name) -- not a guess. `CREDITS.md`'s
  hand-confirmed link wins when both exist (Fede may have picked a more
  specific target); a guessed article-slug (name with spaces -> underscores)
  is the last-resort fallback for the handful of rows neither source covers.
  To refresh `wiki_links.tsv` after the Wiki page changes, re-scrape it (see
  the script comment above `WIKI_LINKS_TSV` for the extraction method used).
- **"Not in VOCK scope" rows** are wiki characters with no corresponding entry
  in `characters.py` — mostly filler NPCs with no unique dialogue, or ones
  VOCK's RPU baseline handles differently than the wiki's vanilla-game
  description. These are hidden by default in `index.html`.
- Conversely, some `characters.py`/RPU entries have no Wiki match at all
  (RPU adds/changes some things vs. vanilla) — expected, per Fede.
- **Kaga's 5 encounter files (`eckaga1`-`eckaga5`) are one row, not five.**
  `characters.py` lists him 5 times (one per random-encounter file), but
  they're the same NPC sharing one audio-tag prefix (`kaga`) -- the build
  script collapses any group of rows that share both a display name AND a
  prefix into a single merged row, whose `MsgStem` column lists all the
  underlying files (`eckaga1, eckaga2, ..., eckaga5`). This only fires when
  BOTH match; same name with a *different* prefix (Eric, Dalia, Quartermaster
  -- see below) is left as separate rows on purpose, since that means two
  unrelated characters who just happen to share a display name.
- **Same display name, different character**: `characters.py` has three
  names that cover two unrelated NPCs each -- Eric (Broken Hills's ghoul
  innkeeper, `hceric`, vs. the Special-Encounter Monty-Python horse-servant,
  `eceric`), Dalia (`bcdalia` vs `ocdalia`), and Quartermaster (`ccqmstr` vs
  `ccmaster`). Every name-only lookup (CREDITS.md, THAT.md, TH Images) is
  ambiguity-aware for these: a CREDITS.md/THAT.md match is only trusted for a
  given stem if that source's own Wiki-link text actually names the place
  that stem is independently confirmed to be at, and a TH Images portrait is
  only auto-assigned to whichever of the ambiguous stems looks like the
  "real" Talking Head (has a confirmed real-place Wiki entry and/or an audit
  file) rather than being cloned onto both -- this is what fixed Eric's
  portrait bleeding from the Broken Hills ghoul onto the Special-Encounter
  reuse of his name.
- TH Images matching is name-based fuzzy matching (handles "Dr."/"Doc" vs
  "Doctor", articles, punctuation, curly quotes) — about 122/192 VOCK-scope
  characters matched a portrait; the rest simply aren't in the TH Images
  folder yet (plus a couple held back by the ambiguous-name rule above).
- **RPCE's 3 new companions aren't rows yet** (Red-Knuckle Rhea, Ceri, Den
  slave) — they have no `characters.py` entry, msg_stem, or Wiki page to key
  on. If/when VOCK starts tracking them, add `characters.py` rows first and
  they'll pick up automatically once their stems are added to
  `RPCE_COMPANION_STEMS`.
- **`index.html`'s grid never auto-hides a column.** It used to
  (`responsiveLayout: "collapse"`), collapsing whichever columns didn't fit
  into an expand-arrow -- but that could hide a column (Voice Actor,
  Companion, ...) that the hand-written detail panel didn't happen to also
  repeat, making it invisible on a narrower window with no way to get it
  back short of resizing. Now every column is always in the grid at its
  natural width; if they don't all fit, the table scrolls horizontally
  within its own box (Photo and Name stay frozen on the left for
  orientation) instead of hiding data or scrolling the whole page.

## Publishing to GitHub Pages

This folder is meant to become its own repo (same pattern as `vock-fo2` next
to the `vock` tool repo — see project memory `vock_project_structure`). Once
pushed, enable GitHub Pages on the repo (Settings → Pages → Deploy from
branch → `main` / root) and `index.html` becomes the live filterable table at
`https://<user>.github.io/<repo>/`.
