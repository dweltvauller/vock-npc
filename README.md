# V.O.C.K. NPC Table

A single browsable table of every Fallout 2 NPC that VOCK tracks for voice
acting — casting status, voice actor, a character/voice brief, three audition
lines, the Talking Head portrait — cross-referenced with the full vanilla
cast for reference.

**Live:** <https://dweltvauller.github.io/vock-npc/>

## Files

| Path | What |
|------|------|
| `data/character_table.csv` | **The hand-edited master.** Edit this directly (Excel / Sheets / text editor). |
| `data/character_table.json` / `.js` | Generated from the CSV by `scripts/csv_to_json.py`. `.js` is what the page loads. Never hand-edit. |
| `scripts/csv_to_json.py` | Pure CSV → JSON/JS conversion. Run after every CSV edit. |
| `index.html` | Standalone filterable/sortable table (Tabulator from a CDN, no build step). Loads `data/character_table.js`, `images/*`, `assets/fonts/*` — all relative. |
| `images/` | Talking Head portraits, one file per `Msg File` stem (e.g. `dcsmitty.png`). Coverage is partial. |
| `assets/fonts/` | `Fallout.otf` / `FalloutFont4.ttf`, the display faces from dweltvauller.github.io. |

## Editing

Edit `data/character_table.csv`, then:

```
python3 scripts/csv_to_json.py
git add -A && git commit -m "..." && git push
```

GitHub Pages rebuilds on every push to `master` (~1 min).

### Multi-value cells

Most NPCs have one `Msg File`, one `FRM file`, one `Prefix`, one `ImageFile`.
When an NPC has more than one, put each value on its own line **inside the
CSV cell** (a literal newline — Excel/Sheets: Alt+Enter). Keep
`Msg File` / `FRM file` / `Prefix` / `ImageFile` in the same order line-for-line
so line *N* of each refers to the same underlying file; leave a line blank
rather than dropping it. Current cases: **Kaga** (5 `Msg File` lines, one
prefix/portrait), **Quartermaster** (2 `Msg File` + 2 `Prefix`, one portrait).

**Dalia is two separate rows**, not a multi-value row — she has two different
talking heads (Vault 15 `bcdalia`, Vault 13 `ocdalia`), one row each, with a
cross-reference note in each `Description`. Don't merge them.

Name portrait files after the `Msg File` stem so `ImageFile` and filenames
match 1:1.

## Columns

- **Mod** (shown as *Voiced By*) — one of `FO2`, `RPU`, `THAT`, `VOCK`, in that
  priority. `FO2`/`RPU` = audio already ships (retail game / Restoration
  Project). `THAT` = on the third-party *Fallout 2 Talking Heads* mod roster
  (its VA goes in `VoiceActor`, `<unknown>` if the public listing has none).
  `VOCK` = none of the above; VOCK's to voice.
- **TH Mod** — which project made the talking-head art: `Fallout 2` (retail;
  exactly the `Mod = FO2` set), `RPU` (only John Cassidy), `Talking Heads`
  (the THAT mod — every other head), blank (no head). Independent of `Mod`.
- **Status** (`Mod = VOCK` rows) — `Completed` / `Cast` / `Work In Progress` /
  `Auditioning`, kept in sync with `vock-fo2/CHANGELOG.md` + `CREDITS.md`
  (shipped version → Completed, credited but unshipped → Cast, `## WIP` →
  Work In Progress, AI-voiced or unassigned → Auditioning). `Completed` on
  `FO2`/`RPU`/`THAT` rows; blank on wiki-roster rows.
- **Prefix, Description, Line A/B/C** — populated for `Mod = VOCK` rows only;
  blank elsewhere.
- **WikiLink** — fandom article, except RPU restored-content NPCs (Abbey, EPA,
  Umbra Tribe, Vault Village, Kaga), which have no fandom page and instead
  point at the matching `f2rp.bgforge.net/<area>/` handbook page (rendered as
  "RPU guide").
- **Companion** / **CompanionMod** — whether the game lets you recruit them:
  `Yes` for vanilla FO2 companions, `RPCE` in `CompanionMod` for ones the
  [RPU Companion Expansion](https://www.nexusmods.com/fallout2/mods/70) adds.
- **InVockScope** — `No` rows are hidden by default in the page (a "Show non
  Talking Head NPCs" toggle reveals them). They're wiki-roster reference rows
  plus the deliberately-parked Monty Python Holy Grail retinue (Sir Bedemir,
  Concorde, Eric `eceric`, John, Joshua, Patsy, Sir Robin, Sir Launcelot, Sir
  Galahad — `Mod` blanked, only `Location` + `WikiLink` kept).

## Notes

- **Same display name, different NPC**: `Eric` (Broken Hills `hceric` vs.
  Special-Encounter `eceric`) and `Quartermaster` (`ccqmstr` vs `ccmaster`)
  are unrelated characters — keep them as separate rows.
- Some `characters.py` / RPU entries have no fandom Wiki article — expected.
- `Frank Horrigan`'s `FRM file` (`bosss`) was filled by hand; he isn't in
  `characters.py`.
