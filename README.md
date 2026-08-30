# V.O.C.K. - NPC Table

A single reference table covering every character VOCK tracks for Fallout 2 voice
acting, cross-referenced with the [Fallout Wiki's Fallout 2 characters
page](https://fallout.fandom.com/wiki/Fallout_2_characters) so the full vanilla
cast is represented even where VOCK has no plans (yet).

Live columns: name, dialogue-file (`Msg File`) / talking-head art-file
(`FRM file`) / audio-prefix IDs, location, mod, talking-head mod (`TH Mod`),
production status, casting status, voice actor, a free-text **Description** of
the character/voice, three audition lines (A/B/C), a wiki link, the Talking
Head portrait, and (where one exists) the voice actor from the third-party
**THAT** ("Fallout 2 Talking Heads Mod") casting-call project, kept separate
from VOCK's own casting since it's a different mod with its own cast, and a
companion flag (see below).

**Prefix, Description, and Line A/B/C are populated for VOCK NPCs only**
(`Mod = VOCK`) — cleared to blank for `FO2`/`RPU`/`THAT` rows and the
wiki-roster rows, since VOCK isn't casting or recording those. There is
no longer a Notes column: the internal tagging notes (concat-bug state, forked
scripts, audit-file paths) were removed because that information isn't for
public sharing.

The `Mod` column (shown in `index.html` as **Voiced By**) is a single,
mutually-exclusive value: `FO2`, `RPU`, `THAT`, or `VOCK`, in that priority
order. `FO2`/`RPU` mean the character already has
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

Cut content restored by the (unofficial) Restoration Project — NPCs in the
Abbey, EPA, Umbra Tribe, Vault Village, plus Kaga — mostly has **no Fallout
Wiki article**, so those rows' `WikiLink` points at the matching
[f2rp.bgforge.net](https://f2rp.bgforge.net/) handbook area page instead of a
dead `fallout.fandom.com` URL, and `index.html` renders it as an "RPU guide"
link rather than "wiki".

The `TH Mod` column records which project made the character's **talking-head
art** (`.FRM`). Three values:

- `Fallout 2` — the head ships in the retail game. This set is exactly the
  "Voiced by Fallout 2" group (`Mod = FO2`), 12 rows: Arroyo Elder, Hakunin,
  Sergeant Arch Dornan, Enclave Gate Guard, Harold, Marcus, Sulik, Myron,
  Dick Richardson, Tandi, Joanne Lynette, Frank Horrigan (`FRM file` `bosss` —
  the vanilla `art/heads/BOSSS*.FRM` set).
- `RPU` — added by the Restoration Project. Exactly one row: **John Cassidy**
  (RPU gave him both his voice and his head).
- `Talking Heads` — the third-party *Fallout 2 Talking Heads* mod (THAT).
  Every other head in the table (168 rows — all the `VOCK`- and `THAT`-voiced
  NPCs that have one).
- blank — no talking head (`FRM file` empty).

`TH Mod` is about the *head art* only — independent of who voices the NPC
(`Mod`) or which mod restored the character. A vanilla Fallout 2 character can
have `TH Mod = Talking Heads` (head added by the mod).

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

- `data/character_table.csv` — **the hand-edited master file.** Open it in
  Excel/Sheets or a text editor and edit it directly; this is the source of
  truth, not a generated artifact. See "Editing the table" below for the
  multi-value-cell convention before you touch `Msg File`, `FRM file`,
  `Prefix`, or `ImageFile`.
- `data/character_table.json` / `data/character_table.js` — the same data,
  mechanically converted from the CSV by `scripts/csv_to_json.py`. `.js`
  (a `window.CHARACTER_TABLE = [...]` global) is what `index.html` actually
  loads, so it also works opened straight off disk with no server. Never
  hand-edit either — re-run the script instead.
- `data/wiki_roster.tsv` / `data/wiki_links.tsv` — a cached extract from the
  Fallout Wiki page, kept only as reference for how the table was originally
  compiled. No longer read by anything.
- `vock-fo2/THAT.md` — a reference table Fede compiled from the public
  Casting Call Club listings for THAT (the *Fallout 2 Talking Heads* mod, a
  third-party project, not VOCK). Per THAT.md's own disclaimer: third-party
  info, may be outdated, blank means no confirmed actor was found in the
  public listings — treat as a lead, not a confirmed credit.
- `images/` — Talking Head portraits, one file per `msg_stem` (e.g.
  `dcsmitty.png` for Smitty, not a shorter audio-tag prefix like `smit.png`)
  — see "Editing the table" below. Not every character has a portrait yet —
  coverage is partial.
- `scripts/build_table.py` — **deprecated, do not run.** This originally
  compiled the CSV from `vock-fo2/characters.py`, audit files, `CREDITS.md`,
  `float_filter.cfg`, va-scripts, and the Wiki roster. Since the CSV is now
  hand-edited directly, running it again would silently overwrite manual
  edits (merged rows, multi-line cells, msg_stem-renamed images). It now
  exits immediately with a warning instead of running. Kept only as a record
  of how the table was first assembled.
- `scripts/csv_to_json.py` — the only script you actually run. A pure,
  mechanical CSV → JSON/JS conversion with no merging logic and no other
  inputs. Re-run it after every CSV edit.
- `index.html` — a standalone, filterable, sortable browser for the table.
  Works straight off GitHub Pages (or any static host, or opened directly
  from disk) with no build step — it loads `data/character_table.js`,
  `images/*`, and `assets/fonts/*` relative to itself. Uses
  [Tabulator](https://tabulator.info/) (loaded from jsDelivr) for the grid:
  per-column text search boxes, **multi-select** dropdown filters on the
  Location / Status / Voiced By / TH Mod / Companion columns (each with an
  `(empty)` option that matches rows blank in that column), a quick-search
  box, a "Companions only" toggle, a "Show non Talking Head NPCs" toggle
  (off by default — hides the wiki-roster rows), a "Clear all filters"
  button, and a live "showing X of Y rows" count. Status / Voiced By / TH Mod
  / Companion render as coloured chips in fixed distinct hues (green / amber /
  blue / magenta so e.g. VOCK vs THAT read apart at a glance); Location /
  Msg File / FRM file / Prefix are chips with a hue auto-derived from the
  text. Name, Voice Actors, and the Description / audition-line columns are
  plain wrapped text. Name / Voice Actors / Msg File / FRM file / Prefix each
  have a text-search box in the header. The table has a fixed height so its
  horizontal scrollbar stays on screen; rows scroll inside it.
- `assets/fonts/` — `Fallout.otf` and `FalloutFont4.ttf`, the same display
  faces the dweltvauller.github.io site uses. `index.html` uses `Fallout.otf`
  throughout — title, control bar, column headers, and cell contents — over
  the phosphor-green palette (`#3cf800`) copied from that site. Search input
  stays monospace for typing.

## Editing the table

Edit `data/character_table.csv` directly, then run:

```
cd scripts
python3 csv_to_json.py
```

to refresh `index.html`.

**Multi-value cells.** Most NPCs have exactly one dialogue file (`Msg File`),
one talking-head art file (`FRM file`), one audio-tag prefix (`Prefix`), and
at most one portrait (`ImageFile`). A few don't — when an NPC has more than
one, list every value in that cell with a line break between them (a literal
newline inside the CSV cell — Excel/Sheets: Alt+Enter; a plain text editor:
just press Enter, the CSV quoting handles it). Keep
`Msg File`/`FRM file`/`Prefix`/`ImageFile` in the same order line-for-line
across the row so line *N* of each still refers to the same underlying file.
Leave a line blank if that particular file has no photo
yet, rather than dropping the line, so the positions stay aligned.
(`Prefix` is only kept for `Mod = VOCK` rows — see above — so on a non-VOCK
multi-stem row like Dalia the `Prefix` column is simply blank while
`Msg File` keeps its lines.) The current cases:

- **Kaga** — 5 dialogue files (`eckaga1`…`eckaga5`), but they're the same
  encounter/look sharing one prefix (`kaga`) and one portrait — `Msg File`
  lists all 5 lines, `Prefix` and `ImageFile` stay single-line.
- **Quartermaster** — 2 dialogue files, each with its own legacy prefix
  (`ccmaster`/`qm2` and `ccqmstr`/`qm`) but treated as one NPC/one portrait —
  `Msg File`, `FRM file` and `Prefix` each get 2 lines, `ImageFile` stays
  single-line.

**Dalia is the exception — two separate rows, not a multi-value row.** She has
two different talking heads (New Khans camp, `bcdalia`/`dalia` head, Vault 15;
and Vault 13, `ocdalia`/`dal13` head, `ocdalia.png`), so as of 2026-08-29 she's
split into one row per head with its own `Location` and `ImageFile`, and each
row's `Description` carries a note pointing at the other. Don't re-merge them.

**Don't merge same-name-but-different-NPC rows this way.** A few names cover
two unrelated characters rather than one NPC with two files — Eric (Broken
Hills's ghoul innkeeper `hceric` vs. the Special-Encounter Monty-Python
horse-servant `eceric`). And in `characters.py` the Monty-Python Holy Grail
cast (Arthur Pendragon, Concorde, that second Eric, John, Patsy) all share
one audio prefix (`arth`) despite being five different people — a coincidence
in the source data, not a reason to combine them. (Only Arthur still carries
`arth` in the table now; the other four had their `Prefix` cleared when they
left the VOCK category — see the caveats section.)

**Images.** Name every portrait file after its `Msg File` value (e.g.
`dcsmitty.png`, not a shorter prefix like `smit.png`), so `ImageFile` cells
and filenames always match 1:1. For a multi-line `Msg File`/`ImageFile` pair,
name each file after the stem on its own line.

## Known data-quality caveats (read before trusting a row blindly)

- **`FRM file`** was added 2026-08-29 and back-filled from `characters.py`'s
  `head` field (the 5th tuple element) — the talking-head art stem(s), one per
  line, with the same ordering rule as `Msg File` (Hakunin → `hakun`/`haku2`/
  `haku3`; Quartermaster → `qm2`/`qm`). Blank where `characters.py` has no
  entry for that stem (wiki-roster rows, the Monty Python retinue, etc.). Bare
  stems, no `.frm` extension, matching the other ID columns. Frank Horrigan
  (`qcfrank`, not in `characters.py`) was filled by hand from vanilla
  `art/heads`: `bosss`.
- **`VoiceActor`** for the `TH Mod = Fallout 2` and `TH Mod = RPU` rows is
  the public retail / Restoration-Project talking-head cast, taken verbatim
  from `rpu/data/text/english/credits.txt` ("FEATURING THE VOICES OF"): Flo
  DiRe (Elder), Dwight Schultz (Hakunin), Peter Jason (Dornan + Gate Guard),
  Charlie Adler (Harold), Michael Dorn (Marcus + Frank Horrigan), Greg Eagles
  (Sulik), Jason Marsden (Myron), Jeffrey Jones (President Richardson), Tress
  MacNeille (Tandi), Cree Summer (Lynette). John Cassidy's restored head has
  two — Joey Bracken (RPU default) and Adam Dravean — listed one per line.
- **Line A/B/C** are VOCK-NPC-only and hand-curated. The historical
  auto-pick from vanilla RPU dialogue text was a rough starting point; a
  proper curated selection is being filled in by hand. Blank for non-VOCK
  rows.
- **Description** (formerly "Voice Type") is a free-text character/voice
  brief, VOCK-NPC-only, written by hand. Blank for `FO2`/`RPU`/`THAT` and
  wiki-roster rows.
- **Location** comes from (in order of preference) the audit file, then
  `CREDITS.md`, then the Wiki roster match by name+dialogue-file, then a
  looser wiki match by name alone, then the FO2/RPU list -- then it's
  collapsed to its parent town via `base_town()` (`Vault City Courtyard` /
  `Vault City Downtown` / `Vault City Inner` all become `Vault City`, `Den
  East Side` / `Den West Side` become `Den`, etc. -- see `KNOWN_TOWNS` in
  `scripts/build_table.py`). The finer sub-area, when it said something the
  town name alone doesn't, was historically kept in a `Notes` cell as
  `Area: ...`; that column has since been removed, so any such detail now
  lives only in git history of the CSV. A few other cleanup rules keep the raw sources from leaking
  garbage into Location before that collapse happens: the Wiki's "Player
  characters" grouping (all companions listed together) is never used as a
  Location -- a companion's real hometown is preferred instead, falling back
  to blank rather than the misleading "Player characters" label. A name-only
  Wiki match is dropped entirely if that Wiki row's own dialogue file points
  to a different character (e.g. our Monty-Python "John" vs. the Wiki's
  unrelated "John"/Bcjohn.msg in Vault 15) -- same name, different NPC, no
  guess made. Audit `location` fields that are really flavor text ("Random
  encounter (Monty Python parody) -- one of Arthur's knights...") are
  detected and dropped rather than used as a Location, falling through to a
  real place.
  After all that, a handful of characters (mostly ones the Wiki lists
  without a location bucket at all) are still blank — that's an honest "we
  don't know," not a bug.
- **Status** values in use: `Completed`, `Cast`, `Auditioning`,
  `Work In Progress` for VOCK NPCs; `Completed` for `FO2`/`RPU`/`THAT` rows
  (their audio already ships); blank on wiki-roster rows.
- **WikiLink is a real link scraped directly off the Fallout Wiki's
  characters page** (`data/wiki_links.tsv`, keyed by dialogue file where the
  Wiki table gave one, else by display name) -- not a guess. `CREDITS.md`'s
  hand-confirmed link wins when both exist (Fede may have picked a more
  specific target); a guessed article-slug (name with spaces -> underscores)
  is the last-resort fallback for the handful of rows neither source covers.
  To refresh `wiki_links.tsv` after the Wiki page changes, re-scrape it (see
  the script comment above `WIKI_LINKS_TSV` for the extraction method used).
  **Exception:** RPU restored-content NPCs (Abbey, EPA, Umbra Tribe, Vault
  Village, Kaga) had their dead `fallout.fandom.com` slugs replaced by hand
  with the matching `f2rp.bgforge.net/<area>/` handbook page, since the Fallout
  Wiki has no article for most restored cut content.
- **`InVockScope = No` rows** are hidden by default in `index.html`. Most are
  wiki characters with no corresponding entry in `characters.py` — filler NPCs
  with no unique dialogue, or ones VOCK's RPU baseline handles differently than
  the wiki's vanilla-game description (`Mod`/`Status` left blank). A second
  group *does* have a `characters.py` entry but was pushed out: the 9
  no-talking-head Monty Python Holy Grail "Special Encounter" retinue (Sir
  Bedemir, Concorde, Eric `eceric`, John, Joshua, Patsy, Sir Robin, Sir
  Launcelot, Sir Galahad). These were removed from the VOCK category
  (`Mod` blanked; `Prefix`/`Description`/audio/`Line A/B/C`/`Status` cleared)
  on 2026-08-29. They keep only their `Location` and `WikiLink` — a
  `characters.py`-derived row with everything else blank. Arthur Pendragon, the Bridge Keeper, and Dogmeat are also "Special
  Encounter" but stay `Mod = VOCK` and in scope — the first two have talking
  heads, and Dogmeat isn't part of the Holy Grail gag.
- Conversely, some `characters.py`/RPU entries have no Wiki match at all
  (RPU adds/changes some things vs. vanilla) — expected, per Fede.
- **Kaga's 5 encounter files (`eckaga1`-`eckaga5`) are one row, not five.**
  `characters.py` lists him 5 times (one per random-encounter file), but
  they're the same NPC sharing one audio-tag prefix (`kaga`) -- the build
  script collapses any group of rows that share both a display name AND a
  prefix into a single merged row, whose `Msg File` column lists all the
  underlying files (`eckaga1, eckaga2, ..., eckaga5`). This only fires when
  BOTH match; same name with a *different* prefix is left as separate rows on
  purpose.
- **Same display name, different character**: `characters.py` has names that
  cover two *unrelated* NPCs each -- Eric (Broken Hills's ghoul innkeeper,
  `hceric`, vs. the Special-Encounter Monty-Python horse-servant, `eceric`),
  and Quartermaster (`ccqmstr` vs `ccmaster`). (Dalia's two stems `bcdalia`/
  `ocdalia` are the *same* NPC in two spots — deliberately two rows, see
  above.) Every name-only lookup (CREDITS.md, THAT.md, TH Images) is
  ambiguity-aware for these: a CREDITS.md/THAT.md match is only trusted for a
  given stem if that source's own Wiki-link text actually names the place
  that stem is independently confirmed to be at, and a TH Images portrait is
  only auto-assigned to whichever of the ambiguous stems looks like the
  "real" Talking Head (has a confirmed real-place Wiki entry and/or an audit
  file) rather than being cloned onto both -- this is what fixed Eric's
  portrait bleeding from the Broken Hills ghoul onto the Special-Encounter
  reuse of his name.
- TH Images matching is name-based fuzzy matching (handles "Dr."/"Doc" vs
  "Doctor", articles, punctuation, curly quotes) plus a direct stem-or-prefix
  filename lookup against whatever's already in `images/` — together, about
  169/348 rows (169/192 VOCK-scope) have a portrait; the rest have neither a
  TH Images name-match nor a manually-placed file yet (plus a couple held
  back by the ambiguous-name rule above).
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
