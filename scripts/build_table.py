#!/usr/bin/env python3
"""VOCK character table builder.
Merges vock-fo2/characters.py roster with the Fallout Wiki's Fallout 2
characters page, plus VOCK's own audit/credits/audio data, into one CSV.
Re-run this any time source data changes; it is fully regenerated, not edited by hand.
"""
import os, re, sys, csv, glob, shutil, json, unicodedata, statistics
import yaml

ROOT = os.path.expanduser("~/mnt/VOCK")
FO2 = os.path.join(ROOT, "vock-fo2")
OUT_DIR = os.path.join(ROOT, "vock-characters")
DATA_DIR = os.path.join(OUT_DIR, "data")
IMG_OUT = os.path.join(OUT_DIR, "images")
TH_IMAGES_SRC = os.path.join(ROOT, "TH Images")
AUDIT_DIR = os.path.join(ROOT, "claude", "audit", "vock-fo2")
VA_SCRIPTS_DIR = os.path.join(FO2, "va-scripts")
MSG_DIR = os.path.join(FO2, "msg")
MSG_PENDING_DIR = os.path.join(FO2, "msg", "pending")
WAV_DIR = os.path.join(FO2, "wav")
RPU_DIALOG_DIR = os.path.join(ROOT, "rpu", "data", "text", "english", "dialog")
CREDITS_MD = os.path.join(FO2, "CREDITS.md")
THAT_MD = os.path.join(FO2, "THAT.md")
FLOAT_CFG = os.path.join(FO2, "float_filter.cfg")
WIKI_TSV = os.path.join(DATA_DIR, "wiki_roster.tsv")
WIKI_LINKS_TSV = os.path.join(DATA_DIR, "wiki_links.tsv")

QUOTE_MAP = {"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"}

def clean_quotes(s):
    for k, v in QUOTE_MAP.items():
        s = s.replace(k, v)
    return s

def norm(s):
    if not s:
        return ""
    s = clean_quotes(s)
    s = re.sub(r"^\s*the\s+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\bDr\.?\b", "Doctor", s, flags=re.IGNORECASE)
    s = re.sub(r"\bDoc\b", "Doctor", s, flags=re.IGNORECASE)
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s

# manual aliases: norm(alt name) -> norm(canonical characters.py name)
NAME_ALIASES = {
    norm("Chuck and Buck Dunton"): norm("Chuck or Buck Dunton"),
    norm("Chuck Dunton"): norm("Chuck or Buck Dunton"),
    norm("Buck Dunton"): norm("Chuck or Buck Dunton"),
    norm("Rebecca (Vault 15)"): norm("Rebecca"),
    norm("Painless Doc Johnson"): norm("Painless Doc Johnson"),
    norm("Torr Buckner"): norm("Torr Buckner"),
    norm("Zomak the Destroyer"): norm("Zomak The Destroyer"),
    norm("Sir Bedemir"): norm("Sir Bedemir"),
    norm("Sir Galahad"): norm("Sir Galahad"),
    norm("Sir Launcelot"): norm("Sir Launcelot"),
    norm("Sir Robin"): norm("Sir Robin"),
    norm("Phil (Bartender)"): norm("Phil (bartender, arm-wrestle commentary)"),
    norm("Maida Buckner"): norm("Maida Buckner"),
    norm("Fannie Mae"): norm("Fannie Mae"),
    norm("Great Ananias"): norm("Great Ananias"),
    norm("Big Jesus Mordino"): norm("Big Jesus Mordino"),
    norm("Chieftain"): norm("Chieftain"),
    norm("Doctor Andrew"): norm('"Doctor" Andrew'),
    norm("Navarro Base Commander"): norm("Navarro Base Commander"),
    norm("Christopher Wright"): norm("Christopher Wright"),
    norm("Keith Wright"): norm("Keith Wright"),
    norm("Bridge Keeper"): norm("Bridge Keeper"),
    norm("Bridgekeeper"): norm("Bridge Keeper"),
}

def canon(n):
    nn = norm(n)
    return NAME_ALIASES.get(nn, nn)

# ---------- characters.py ----------
sys.path.insert(0, FO2)
import characters as _characters_mod
CHARACTERS = _characters_mod.CHARACTERS  # (msg_stem, name, prefix, ssl_stems, head)
print(f"characters.py: {len(CHARACTERS)} rows")

# ---------- collapse same-NPC/multi-encounter rows (e.g. Kaga x5) ----------
# Two characters.py rows are "the same NPC told with more than one dialogue
# file" only when they share BOTH a display name and a prefix (the prefix is
# the shared audio-tag namespace -- Kaga's 5 encounter files all use tag
# prefix "kaga", so they're really one character). Same name + DIFFERENT
# prefix (Eric/Dalia/Quartermaster below) means two unrelated characters
# that just happen to share a display name -- never merge those.
_char_groups = {}
_char_group_order = []
for _c in CHARACTERS:
    _key = (canon(_c[1]), _c[2])
    if _key not in _char_groups:
        _char_groups[_key] = []
        _char_group_order.append(_key)
    _char_groups[_key].append(_c)

MERGED_CHARACTERS = []  # (primary_stem, name, prefix, ssl_stems, head, all_stems)
for _key in _char_group_order:
    _group = _char_groups[_key]
    _primary = _group[0]
    MERGED_CHARACTERS.append((_primary[0], _primary[1], _primary[2], _primary[3], _primary[4],
                               [_c[0] for _c in _group]))
if len(MERGED_CHARACTERS) != len(CHARACTERS):
    print(f"  collapsed {len(CHARACTERS) - len(MERGED_CHARACTERS)} multi-encounter rows into "
          f"{sum(1 for _k in _char_group_order if len(_char_groups[_k]) > 1)} merged NPCs "
          f"(e.g. Kaga's 5 encounter files -> 1 row)")

# ---------- names that mean two+ different characters (share a display name, different prefix) ----------
_name_prefixes = {}
for _c in CHARACTERS:
    _name_prefixes.setdefault(canon(_c[1]), set()).add(_c[2])
AMBIGUOUS_NAMES = {n for n, prefixes in _name_prefixes.items() if len(prefixes) > 1}

# ---------- coarse town grouping ("Vault City Courtyard" -> "Vault City") ----------
KNOWN_TOWNS = [
    "Vault City", "Broken Hills", "New Reno", "Den", "Redding",
    "NCR", "Klamath", "Navarro", "Gecko", "Modoc", "Arroyo", "Vault 13",
    "Vault 15", "San Francisco", "Enclave Oil Rig", "Enclave", "Sierra Army Depot",
    "New Khans", "PMV Valdez", "Stables", "Westin Ranch", "Hubologist",
    "Mariposa", "Council Hall", "Central Council and Vault 8",
    "Special Encounter", "Random Encounter", "EPA", "Abbey",
    "Primitive Tribe", "Umbra Tribe", "Slaver Camp",
]
_KNOWN_TOWNS_SORTED = sorted(KNOWN_TOWNS, key=len, reverse=True)
def base_town(loc):
    """Collapse a detailed sub-area Location down to its parent town."""
    if not loc:
        return loc
    low = re.sub(r"^\s*the\s+", "", loc.lower())
    for t in _KNOWN_TOWNS_SORTED:
        if low.startswith(t.lower()):
            return t
    return loc

# ---------- real Wiki article links, scraped directly from the Fallout Wiki's
# Fallout 2 characters page (not guessed) -- keyed by msg_stem where the
# table gave a dialogue file, else by display name for the handful of
# stem-less rows (companions/props with no unique dialogue). ----------
WIKI_BASE = "https://fallout.fandom.com"
wiki_link_by_stem = {}
wiki_link_by_name = {}
if os.path.isfile(WIKI_LINKS_TSV):
    with open(WIKI_LINKS_TSV, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            kind, key, path = parts
            url = WIKI_BASE + path
            if kind == "S":
                wiki_link_by_stem[key] = url
            else:
                wiki_link_by_name[key] = url
print(f"wiki_links.tsv: {len(wiki_link_by_stem)} stem links, {len(wiki_link_by_name)} name-only links")

# ---------- float_filter.cfg ----------
def expand_spec(spec):
    nums = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            nums.update(range(int(a), int(b) + 1))
        else:
            nums.add(int(part))
    return nums

float_by_prefix = {}
with open(FLOAT_CFG, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^(\S+)\s+(.+)$", line.strip())
        if m:
            prefix, spec = m.group(1), m.group(2)
            float_by_prefix.setdefault(prefix, set()).update(expand_spec(spec))

# ---------- audit frontmatter ----------
audit_by_stem = {}
for path in glob.glob(os.path.join(AUDIT_DIR, "*.md")):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not m:
        continue
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        continue
    stem = (fm.get("msg_stem") or "").lower()
    if stem:
        fm["_audit_path"] = path
        audit_by_stem[stem] = fm
        # A few audits cover a whole numbered-encounter group with a range
        # like "eckaga1-5" instead of one file -- register each individual
        # stem too so per-character lookups (eckaga1, eckaga2, ...) find it.
        rm = re.match(r"^([a-z]+?)(\d+)-(\d+)$", stem)
        if rm:
            base, lo, hi = rm.group(1), int(rm.group(2)), int(rm.group(3))
            for n in range(lo, hi + 1):
                audit_by_stem.setdefault(f"{base}{n}", fm)

# ---------- CREDITS.md ----------
credits_by_name = {}
with open(CREDITS_MD, encoding="utf-8") as f:
    credits_txt = f.read()
section = None
for line in credits_txt.splitlines():
    if line.startswith("## Voice Actors"):
        section = "cast"; continue
    if line.startswith("## AI-Voiced"):
        section = "ai"; continue
    if line.startswith("## "):
        section = None; continue
    if section in ("cast", "ai") and line.startswith("|") and "---" not in line:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].lower() == "character":
            continue
        name_cell = cells[0]
        mlink = re.match(r"\[(.*?)\]\((.*)\)$", name_cell)
        disp_name, wiki_url = (mlink.group(1), mlink.group(2)) if mlink else (name_cell, "")
        key = canon(disp_name)
        if section == "cast" and len(cells) >= 3:
            credits_by_name[key] = {"wiki_url": wiki_url, "location": cells[1], "va": cells[2], "cast_status": "Cast"}
        elif section == "ai" and len(cells) >= 2:
            credits_by_name[key] = {"wiki_url": wiki_url, "location": cells[1], "va": "AI (temp, to be replaced)", "cast_status": "AI-voiced (temp)"}

# ---------- THAT.md (third-party Talking Heads mod VA reference) ----------
that_by_name = {}
if os.path.isfile(THAT_MD):
    with open(THAT_MD, encoding="utf-8") as f:
        that_txt = f.read()
    for line in that_txt.splitlines():
        if not line.startswith("|") or "---" in line or line.lower().startswith("| npc"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        name_cell, location, va = cells[0], cells[1], cells[2]
        mlink = re.match(r"\[(.*?)\]\((.*)\)$", name_cell)
        disp_name = mlink.group(1) if mlink else name_cell
        disp_name = re.sub(r"\s*\(Companion\)\s*", "", disp_name).strip()
        key = canon(disp_name)
        links = cells[3] if len(cells) > 3 else ""
        that_by_name[key] = {"location": location, "va": va, "links": links}
print(f"THAT.md: {len(that_by_name)} named entries")

# ---------- FO2 (vanilla game) / RPU voiced-NPC list (Fede-curated, 2026-08-28) ----------
# These are characters that already have existing spoken audio shipped either with
# vanilla Fallout 2 itself, or added by the (unofficial) Restoration Project (RPU) --
# distinct from VOCK's own recording effort and from the third-party THAT mod.
FO2_RPU_VOICED = [
    # (mod, msg_stem, location)
    ("FO2", "ahelder",  "Arroyo"),
    ("FO2", "ahhakun",  "Arroyo"),
    ("FO2", "hcmarcus", "Broken Hills"),
    ("FO2", "qcfrank",  "Enclave Oil Rig"),
    ("FO2", "qhprzrch", "Enclave Oil Rig"),
    ("FO2", "gcharold", "Gecko"),
    ("FO2", "kcsulik",  "Klamath"),
    ("FO2", "ccdrill",  "Navarro"),
    ("FO2", "ccgguard", "Navarro"),
    ("FO2", "shtandi",  "NCR"),
    ("FO2", "nhmyron",  "Stables"),
    ("FO2", "vclynett", "Vault City"),
    ("RPU", "vccasidy", "Vault City"),
    # gcpacoff (Enclave communications officer, FO2-voiced) has no characters.py row yet -- not applied.
]
fo2rpu_by_stem = {}
for mod, stem, loc in FO2_RPU_VOICED:
    fo2rpu_by_stem.setdefault(stem, []).append((mod, loc))

# ---------- Companion flag + companion-adding mod ----------
# RPCE = "Restoration Project - Companion Expansion" (nexusmods.com/fallout2/mods/70) --
# the one mod (as of 2026-08-28) that turns additional vanilla NPCs into full companions.
# Only characters with an existing characters.py row are listed here; the mod also adds
# 3 wholly new characters (Red-Knuckle Rhea, Ceri, a Den slave) with no VOCK/wiki msg_stem yet.
RPCE_COMPANION_STEMS = {
    "dclara",    # Lara
    "bcjones",   # Doc Jones
    "ncangbis",  # Angela Bishop
    "ncmason",   # Mason
    "ncliljes",  # Lil' Jesus Mordino
    "ncchrwri",  # Christopher Wright
    "mcmiria",   # Miria (expanded via "Better Miria" integration)
}

# ---------- wav/ -> recorded tag numbers per prefix ----------
prefixes_sorted = sorted({c[2] for c in CHARACTERS}, key=len, reverse=True)
recorded_by_prefix = {}
for fn in os.listdir(WAV_DIR):
    if not fn.lower().endswith(".wav"):
        continue
    stem = fn[:-4]
    for p in prefixes_sorted:
        if stem.startswith(p) and stem[len(p):].isdigit():
            recorded_by_prefix.setdefault(p, set()).add(int(stem[len(p):]))
            break

# ---------- msg presence ----------
done_stems = {os.path.splitext(f)[0].lower() for f in os.listdir(MSG_DIR) if f.lower().endswith(".msg")}
pending_stems = {os.path.splitext(f)[0].lower() for f in os.listdir(MSG_PENDING_DIR) if f.lower().endswith(".msg")}

# ---------- va-scripts ----------
va_by_canon = {}
for path in glob.glob(os.path.join(VA_SCRIPTS_DIR, "*.md")):
    fname = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    direction_m = re.search(r"\*\*Direction:\*\*\s*(.+)", txt)
    direction = direction_m.group(1).strip() if direction_m else ""
    lines = []
    for m in re.finditer(r"`([a-zA-Z]+\d+):`\s*(.+)", txt):
        tag, text = m.group(1), m.group(2).strip()
        text = re.sub(r"^\*.*?\*\s*", "", text)  # strip leading stage direction
        if text and not (text.startswith("*") and text.endswith("*")):
            num_m = re.search(r"(\d+)$", tag)
            lines.append((int(num_m.group(1)) if num_m else 0, text))
    va_by_canon[canon(fname)] = {"direction": direction, "lines": lines, "path": path}

def parse_msg_file(path):
    lines = []
    if not os.path.isfile(path):
        return lines
    with open(path, encoding="latin-1") as f:
        txt = f.read()
    for m in re.finditer(r"\{(\d+)\}\{[^}]*\}\{([^}]*)\}", txt):
        idx, text = int(m.group(1)), m.group(2).strip()
        if text and not re.match(r"^you see\b", text, re.IGNORECASE) and idx != 1:
            lines.append((idx, text))
    return lines

def pick_abc(lines):
    # lines: list of (order, text), dedup by text, need len>=2 words ideally
    seen = {}
    for order, text in lines:
        if text and text not in seen:
            seen[text] = order
    pool = sorted(seen.items(), key=lambda kv: kv[1])  # (text, order) sorted by order
    if not pool:
        return "", "", ""
    a = pool[0][0]
    by_len = sorted(seen.keys(), key=len)
    c = by_len[-1]
    remaining = [t for t in by_len if t != a and t != c]
    if remaining:
        med_len = statistics.median(len(t) for t in remaining)
        b = min(remaining, key=lambda t: abs(len(t) - med_len))
    else:
        b = ""
    return a, b, c

# ---------- wiki roster ----------
wiki_rows = []
with open(WIKI_TSV, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        section, name, dfile = parts
        stem = "" if dfile.lower() == "none" else os.path.splitext(dfile)[0].lower()
        wiki_rows.append({"section": section, "name": name, "stem": stem})

wiki_by_stem = {}
for r in wiki_rows:
    if r["stem"]:
        wiki_by_stem.setdefault(r["stem"], []).append(r)
wiki_by_canonname = {}
for r in wiki_rows:
    wiki_by_canonname.setdefault(canon(r["name"]), []).append(r)

# Vanilla companions per the Fallout Wiki's "Player characters" section of the
# characters page.
vanilla_companion_stems = {r["stem"] for r in wiki_rows if r["section"] == "Player characters" and r["stem"]}

# Wiki sections that group characters by role/rarity rather than by place --
# never good Location values on their own.
NON_LOCATION_WIKI_SECTIONS = {"Player characters", "Special Encounter", "Random Encounter"}

# A couple of Location spellings collide once you ignore case/wording --
# normalize them to one canonical form so the filter dropdown doesn't show
# the same place twice.
LOCATION_ALIASES = {
    "the den": "Den",
    "vault city courtyard": "Vault City Courtyard",
}
def normalize_location(loc):
    return LOCATION_ALIASES.get(loc.lower(), loc) if loc else loc

# ---------- TH Images matching ----------
os.makedirs(IMG_OUT, exist_ok=True)

# A portrait can also be dropped straight into the OUTPUT images/ folder,
# named exactly after its msg_stem (e.g. "steve.png") -- this is how Fede
# adds one-off portraits (THAT-mod talking heads, etc.) that don't come
# from the "TH Images" source folder's "NNN_Full Name.png" naming scheme,
# so they'd never be found by the name-matching pass below. Any such file
# always wins for its stem, VOCK-scope or wiki-only alike.
IMG_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")
def _direct_image_for_stem(s):
    if not s:
        return None
    for ext in IMG_EXTS:
        if os.path.isfile(os.path.join(IMG_OUT, s + ext)):
            return s + ext
    return None

img_files = [f for f in os.listdir(TH_IMAGES_SRC) if os.path.isfile(os.path.join(TH_IMAGES_SRC, f))]
img_by_canon = {}
for fn in img_files:
    base, ext = os.path.splitext(fn)
    base = re.sub(r"^\d+[_\-\s]*", "", base)  # strip leading NNN_
    base = base.replace("_", " ").strip()
    key = canon(base)
    img_by_canon.setdefault(key, []).append(fn)

def _has_real_wiki_place(stem):
    return any(r["section"] not in NON_LOCATION_WIKI_SECTIONS for r in wiki_by_stem.get(stem, []))

# For a name shared by two+ unrelated characters (different prefixes -- see
# AMBIGUOUS_NAMES), there's no way to tell from the image filename alone
# which one it belongs to. Rather than clone the same portrait onto both
# (e.g. the Broken Hills ghoul Eric's photo used to also show up on the
# Special-Encounter Eric), only the single most-likely "real Talking Head"
# owner gets it: prefer whichever stem has its own confirmed real-place Wiki
# entry (a special/random encounter reuse of a name is not a rendered TH),
# then whichever has an audit file, then just the first one deterministically.
def _pick_image_owner(stems):
    if len(stems) == 1:
        return stems[0]
    def score(s):
        return (_has_real_wiki_place(s), s in audit_by_stem)
    return sorted(stems, key=score, reverse=True)[0]

_stems_by_name = {}
for stem, name, prefix, ssl_stems, head, all_stems in MERGED_CHARACTERS:
    _stems_by_name.setdefault(canon(name), []).append(stem)

matched_images = {}   # msg_stem -> src filename
unmatched_chars = []
for stem, name, prefix, ssl_stems, head, all_stems in MERGED_CHARACTERS:
    key = canon(name)
    cands = img_by_canon.get(key)
    if not cands:
        unmatched_chars.append(name)
        continue
    if key in AMBIGUOUS_NAMES and _pick_image_owner(_stems_by_name[key]) != stem:
        unmatched_chars.append(name)  # portrait went to the other same-named stem instead
        continue
    matched_images[stem] = cands[0]

used_images = {v for v in matched_images.values()}
unmatched_images = [f for f in img_files if f not in used_images]

_prefix_by_stem = {c[0]: c[2] for c in CHARACTERS}
for stem, fn in matched_images.items():
    if _direct_image_for_stem(stem) or _direct_image_for_stem(_prefix_by_stem.get(stem, "")):
        continue  # a manually-placed portrait for this stem/prefix wins; don't overwrite it
    src = os.path.join(TH_IMAGES_SRC, fn)
    ext = os.path.splitext(fn)[1].lower()
    dst = os.path.join(IMG_OUT, f"{stem}{ext}")
    shutil.copyfile(src, dst)

print(f"TH Images: {len(img_files)} files, matched {len(matched_images)} characters.py rows, {len(unmatched_chars)} unmatched characters, {len(unmatched_images)} unmatched images")
if unmatched_chars:
    print("  unmatched characters (sample):", unmatched_chars[:25])
if unmatched_images:
    print("  unmatched images (sample):", unmatched_images[:25])

# ---------- assemble rows for characters.py roster ----------
rows = []
seen_stems_in_wiki = set()

for stem, name, prefix, ssl_stems, head, all_stems in MERGED_CHARACTERS:
    ck = canon(name)
    audit = audit_by_stem.get(stem, {})

    # A name shared by two+ unrelated characters (AMBIGUOUS_NAMES) can't be
    # trusted to fetch the right CREDITS.md/THAT.md row by name alone --
    # those files have no dialogue-file reference to disambiguate by. Only
    # accept a name-keyed hit if its own wiki_url/location text names the
    # place THIS specific stem is independently known to be at (via its own
    # exact dialogue-file Wiki match) -- e.g. CREDITS.md's Eric row links to
    # ".../Eric_(Broken_Hills)", which only agrees with hceric, not eceric.
    def _resolve_ambiguous(entry):
        if not entry or ck not in AMBIGUOUS_NAMES:
            return entry
        own_places = [base_town(r["section"]) for r in wiki_by_stem.get(stem, [])]
        disambig_text = (entry.get("wiki_url", "") + " " + entry.get("location", "")).lower().replace("_", " ")
        for place in own_places:
            if place and place.lower() in disambig_text:
                return entry
        return {}

    credit = _resolve_ambiguous(credits_by_name.get(ck, {}))
    that_entry = _resolve_ambiguous(that_by_name.get(ck, {}))

    # location precedence: audit > credits > wiki(by name+stem) > wiki(by stem only) > FO2/RPU list
    # A few audit files put flavor text in `location` instead of a place
    # ("Random encounter (Monty Python parody) -- one of Arthur's knights,
    # first encounter (rndholy1)"). Anything that long or that descriptive
    # isn't a location -- keep it as a note instead and fall through to a
    # real place.
    raw_audit_loc = audit.get("location") or ""
    location_note = ""
    _descriptive = raw_audit_loc and (
        len(raw_audit_loc) > 45
        or " -- " in raw_audit_loc
        or " — " in raw_audit_loc
        or (len(raw_audit_loc) > 20 and raw_audit_loc.lower().startswith(("random encounter", "special encounter")))
    )
    if _descriptive:
        location_note = raw_audit_loc
        raw_audit_loc = ""
    location = raw_audit_loc or credit.get("location") or ""

    wiki_hit_stem = wiki_by_stem.get(stem, [])
    # A canon-name match whose Wiki row names a DIFFERENT dialogue file is a
    # different character wearing the same display name (e.g. our
    # Monty-Python "John" vs. the Wiki's unrelated Vault-15 "John",
    # Bcjohn.msg) -- drop those, keep only hits that don't contradict our
    # own stem (either they agree, or the Wiki row has no dialogue file to
    # check against).
    wiki_hit_name = [r for r in wiki_by_canonname.get(ck, []) if not r["stem"] or r["stem"] == stem]
    # "Player characters" is the Wiki's companion-roster grouping, not a
    # place -- never use it as a Location when a real town is available.
    # "Special Encounter"/"Random Encounter" are fine as a last resort
    # (some characters genuinely have no fixed town).
    def _real_place_hit(hits):
        for r in hits:
            if r["section"] not in NON_LOCATION_WIKI_SECTIONS:
                return r["section"]
        return ""
    def _any_hit(hits):
        return hits[0]["section"] if hits else ""

    if not location:
        # prefer a wiki row that matches both name and stem, real place first
        name_stem_hits = [r for r in wiki_hit_name if r["stem"] == stem]
        location = _real_place_hit(name_stem_hits)
    if not location:
        location = _real_place_hit(wiki_hit_stem)
    if not location:
        location = _real_place_hit(wiki_hit_name)
    fo2rpu_hits = fo2rpu_by_stem.get(stem, [])
    if not location and fo2rpu_hits:
        location = fo2rpu_hits[0][1]
    # last resort: fall back to a categorical wiki section (Special/Random
    # Encounter) rather than leave a real-place-less row totally blank.
    if not location:
        name_stem_hits = [r for r in wiki_hit_name if r["stem"] == stem]
        location = _any_hit(name_stem_hits) or _any_hit(wiki_hit_stem) or _any_hit(wiki_hit_name)
        if location in ("Player characters",):
            location = ""  # still never show the companion-roster grouping itself
    location = normalize_location(location)
    _detailed_location = location
    location = base_town(location)
    if _detailed_location and _detailed_location != location:
        location_note = (location_note + "; " if location_note else "") + f"Area: {_detailed_location}"
    seen_stems_in_wiki.add(stem)

    # status
    if stem in done_stems:
        status = "Recorded" if not audit.get("needs_compile") else "Tagged, needs compile"
    elif stem in pending_stems:
        status = "Tagged (pending)"
    else:
        status = "Not started"

    cast_status = credit.get("cast_status", "Not cast")
    voice_actor = credit.get("va", "")
    # Real link, scraped straight off the Wiki's own characters page, wins.
    # CREDITS.md's hand-confirmed link is next (Fede may have picked a more
    # specific target). Last resort: a guessed article-slug -- not
    # guaranteed to resolve for every obscure/minor NPC.
    wiki_link = (
        wiki_link_by_stem.get(stem)
        or credit.get("wiki_url", "")
        or wiki_link_by_name.get(name, "")
        or (f"https://fallout.fandom.com/wiki/{name.replace(' ', '_')}" if name else "")
    )

    tags_total = audit.get("tags_total")
    float_nums = float_by_prefix.get(prefix, set())
    rec_nums = recorded_by_prefix.get(prefix, set())
    float_total = len(float_nums) if (tags_total is not None or float_nums) else None
    if tags_total is not None:
        th_total = tags_total - len(float_nums)
    else:
        th_total = None
    th_recorded = len([n for n in rec_nums if n not in float_nums])
    float_recorded = len([n for n in rec_nums if n in float_nums])
    th_audio = f"{th_recorded}/{th_total}" if th_total is not None else (f"{th_recorded}/?" if th_recorded else "")
    float_audio = f"{float_recorded}/{float_total}" if float_total else ("" if not float_nums else f"{float_recorded}/{len(float_nums)}")

    # ABC lines: va-script > local msg > pending msg > rpu baseline
    va = va_by_canon.get(ck)
    src_note = ""
    if va and va["lines"]:
        a, b, c = pick_abc(va["lines"])
        voice_type = va["direction"].split(",")[0].strip().rstrip(".") if va["direction"] else ""
    else:
        local_msg = os.path.join(MSG_DIR, stem + ".msg")
        pending_msg = os.path.join(MSG_PENDING_DIR, stem + ".msg")
        rpu_msg = os.path.join(RPU_DIALOG_DIR, stem + ".msg")
        voice_type = ""
        if os.path.isfile(local_msg):
            a, b, c = pick_abc(parse_msg_file(local_msg))
        elif os.path.isfile(pending_msg):
            a, b, c = pick_abc(parse_msg_file(pending_msg))
        elif os.path.isfile(rpu_msg):
            a, b, c = pick_abc(parse_msg_file(rpu_msg))
            src_note = "untagged, vanilla RPU baseline text"
        else:
            a, b, c = "", "", ""

    notes = []
    if location_note:
        notes.append(location_note)
    if audit.get("concat_bug") not in (None, False, "n/a"):
        notes.append(f"concat_bug={audit.get('concat_bug')}")
    if audit.get("forked_script"):
        notes.append("forked script")
    if src_note:
        notes.append(src_note)
    if audit.get("_audit_path"):
        notes.append("audit: " + os.path.relpath(audit["_audit_path"], ROOT))

    # Mutually exclusive: FO2 > RPU > THAT > VOCK. VOCK doesn't re-voice
    # a character that already has audio from one of the other three.
    fo2rpu_mods_here = {m for m, _loc in fo2rpu_hits}
    if "FO2" in fo2rpu_mods_here:
        mod_value = "FO2"
    elif "RPU" in fo2rpu_mods_here:
        mod_value = "RPU"
    elif that_entry:  # matched a THAT.md row at all, VA confirmed or not
        mod_value = "THAT"
    else:
        mod_value = "VOCK"

    companion_mod = "RPCE" if stem in RPCE_COMPANION_STEMS else ""
    is_companion = "Yes" if (stem in RPCE_COMPANION_STEMS or stem in vanilla_companion_stems) else ""
    display_stem = ", ".join(all_stems) if len(all_stems) > 1 else stem

    # Image file actually sitting in images/: a manually-placed portrait
    # wins, checked against every underlying stem (e.g. any of Kaga's 5)
    # and then the audio-tag prefix -- Fede names these files either way
    # (e.g. "vcconnar.png" by msg_stem, or "steve.png" by prefix for a
    # character whose real stem is "hcsteve"). Otherwise fall back to
    # whatever the TH-Images name-match copied there.
    image_file = ""
    for _s in list(all_stems) + [prefix]:
        _f = _direct_image_for_stem(_s)
        if _f:
            image_file = _f
            break
    if not image_file and stem in matched_images:
        image_file = stem + os.path.splitext(matched_images[stem])[1].lower()

    rows.append({
        "Name": name, "MsgStem": display_stem, "Prefix": prefix, "Location": location,
        "Mod": mod_value, "Status": status, "CastStatus": cast_status,
        "VoiceActor": voice_actor, "VoiceType": voice_type,
        "THAudio": th_audio, "FloatAudio": float_audio,
        "AuditionLineA": a, "AuditionLineB": b, "AuditionLineC": c,
        "Notes": "; ".join(notes), "WikiLink": wiki_link,
        "ImageFile": image_file,
        "InVockScope": "Yes",
        "THATVoiceActor": that_entry.get("va", ""),
        "THATLink": that_entry.get("links", ""),
        "Companion": is_companion,
        "CompanionMod": companion_mod,
    })

# ---------- wiki-only additions ----------
existing_stems = {c[0] for c in CHARACTERS}
existing_names_canon = {canon(c[1]) for c in CHARACTERS}
# Group every wiki row by the same key the dedup below uses, so a character
# who shows up under more than one section (e.g. their hometown AND the
# "Player characters" companion roster) gets its real place, not whichever
# section happened to appear first in the scrape.
wiki_sections_by_key = {}
for r in wiki_rows:
    key = r["stem"] if r["stem"] else f"__nostem__{canon(r['name'])}"
    wiki_sections_by_key.setdefault(key, []).append(r["section"])

def _best_wiki_location(sections):
    for sec in sections:
        if sec not in NON_LOCATION_WIKI_SECTIONS:
            return sec
    for sec in sections:
        if sec != "Player characters":
            return sec
    return ""

added_stem_keys = set()
for r in wiki_rows:
    key = r["stem"] if r["stem"] else f"__nostem__{canon(r['name'])}"
    if r["stem"] and r["stem"] in existing_stems:
        continue
    if canon(r["name"]) in existing_names_canon:
        continue
    if key in added_stem_keys:
        continue
    added_stem_keys.add(key)
    best_location = base_town(normalize_location(_best_wiki_location(wiki_sections_by_key.get(key, [r["section"]]))))
    that_entry_wiki = that_by_name.get(canon(r["name"]), {})
    fo2rpu_wiki = fo2rpu_by_stem.get(r["stem"], [])
    fo2rpu_mods_wiki = {m for m, _l in fo2rpu_wiki}
    if "FO2" in fo2rpu_mods_wiki:
        wiki_mod_value = "FO2"
    elif "RPU" in fo2rpu_mods_wiki:
        wiki_mod_value = "RPU"
    elif that_entry_wiki:
        wiki_mod_value = "THAT"
    else:
        wiki_mod_value = ""
    companion_mod_wiki = "RPCE" if r["stem"] in RPCE_COMPANION_STEMS else ""
    is_companion_wiki = "Yes" if (r["stem"] in RPCE_COMPANION_STEMS or r["stem"] in vanilla_companion_stems or r["section"] == "Player characters") else ""
    wiki_link_wiki = (
        wiki_link_by_stem.get(r["stem"])
        or wiki_link_by_name.get(r["name"], "")
        or (f"https://fallout.fandom.com/wiki/{r['name'].replace(' ', '_')}" if r["name"] else "")
    )
    # Wiki-only characters have no characters.py stem to run the TH-Images
    # name-match against, but a manually-placed portrait keyed by the Wiki
    # row's own dialogue-file stem still applies directly.
    image_file_wiki = _direct_image_for_stem(r["stem"]) or ""
    rows.append({
        "Name": r["name"], "MsgStem": r["stem"], "Prefix": "", "Location": best_location,
        "Mod": wiki_mod_value, "Status": "Not in VOCK scope", "CastStatus": "", "VoiceActor": "",
        "VoiceType": "", "THAudio": "", "FloatAudio": "", "AuditionLineA": "", "AuditionLineB": "",
        "AuditionLineC": "", "Notes": "Wiki-only; no VOCK dialogue tagging", "WikiLink": wiki_link_wiki,
        "ImageFile": image_file_wiki, "InVockScope": "No",
        "THATVoiceActor": that_by_name.get(canon(r["name"]), {}).get("va", ""),
        "THATLink": that_by_name.get(canon(r["name"]), {}).get("links", ""),
        "Companion": is_companion_wiki,
        "CompanionMod": companion_mod_wiki,
    })

print(f"Total rows: {len(rows)} ({sum(1 for r in rows if r['InVockScope']=='Yes')} VOCK-scope, {sum(1 for r in rows if r['InVockScope']=='No')} wiki-only)")
print(f"Rows with a portrait: {sum(1 for r in rows if r['ImageFile'])} of {len(rows)}")

# ---------- write CSV ----------
csv_path = os.path.join(DATA_DIR, "character_table.csv")
fieldnames = ["Name","MsgStem","Prefix","Location","Mod","Status","CastStatus","VoiceActor","VoiceType",
              "THAudio","FloatAudio","AuditionLineA","AuditionLineB","AuditionLineC","Notes","WikiLink","ImageFile","InVockScope",
              "THATVoiceActor","THATLink","Companion","CompanionMod"]
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"Wrote {csv_path}")

# also JSON for the web viewer
json.dump(rows, open(os.path.join(DATA_DIR, "character_table.json"), "w"), indent=1)
print("Wrote character_table.json")

# also a plain <script> version -- fetch() of local files is blocked by browsers
# under file:// (no CORS), so index.html loads this instead of fetching the JSON,
# which lets the page work by double-clicking it, not just when hosted/served.
with open(os.path.join(DATA_DIR, "character_table.js"), "w") as f:
    f.write("window.CHARACTER_TABLE = ")
    json.dump(rows, f, indent=1)
    f.write(";\n")
print("Wrote character_table.js")
