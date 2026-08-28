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

# ---------- TH Images matching ----------
os.makedirs(IMG_OUT, exist_ok=True)
img_files = [f for f in os.listdir(TH_IMAGES_SRC) if os.path.isfile(os.path.join(TH_IMAGES_SRC, f))]
img_by_canon = {}
for fn in img_files:
    base, ext = os.path.splitext(fn)
    base = re.sub(r"^\d+[_\-\s]*", "", base)  # strip leading NNN_
    base = base.replace("_", " ").strip()
    key = canon(base)
    img_by_canon.setdefault(key, []).append(fn)

matched_images = {}   # msg_stem -> src filename
unmatched_chars = []
for stem, name, prefix, ssl_stems, head in CHARACTERS:
    key = canon(name)
    cands = img_by_canon.get(key)
    if cands:
        matched_images[stem] = cands[0]
    else:
        unmatched_chars.append(name)

used_images = {v for v in matched_images.values()}
unmatched_images = [f for f in img_files if f not in used_images]

for stem, fn in matched_images.items():
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

for stem, name, prefix, ssl_stems, head in CHARACTERS:
    ck = canon(name)
    audit = audit_by_stem.get(stem, {})
    credit = credits_by_name.get(ck, {})
    that_entry = that_by_name.get(ck, {})

    # location precedence: audit > credits > wiki(by name+stem) > wiki(by stem only)
    location = audit.get("location") or credit.get("location") or ""
    wiki_hit_stem = wiki_by_stem.get(stem, [])
    wiki_hit_name = wiki_by_canonname.get(ck, [])
    if not location:
        # prefer a wiki row that matches both name and stem
        for r in wiki_hit_name:
            if r["stem"] == stem:
                location = r["section"]; break
    if not location and wiki_hit_stem:
        location = wiki_hit_stem[0]["section"]
    if not location and wiki_hit_name:
        location = wiki_hit_name[0]["section"]
    fo2rpu_hits = fo2rpu_by_stem.get(stem, [])
    if not location and fo2rpu_hits:
        location = fo2rpu_hits[0][1]
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
    wiki_link = credit.get("wiki_url", "")

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
    if audit.get("concat_bug") not in (None, False, "n/a"):
        notes.append(f"concat_bug={audit.get('concat_bug')}")
    if audit.get("forked_script"):
        notes.append("forked script")
    if src_note:
        notes.append(src_note)
    if audit.get("_audit_path"):
        notes.append("audit: " + os.path.relpath(audit["_audit_path"], ROOT))

    mod_list = ["VOCK"]
    if that_entry.get("va"):
        mod_list.append("THAT")
    for m, _loc in fo2rpu_hits:
        if m not in mod_list:
            mod_list.append(m)
    mod_value = ", ".join(mod_list)

    rows.append({
        "Name": name, "MsgStem": stem, "Prefix": prefix, "Location": location,
        "Mod": mod_value, "Status": status, "CastStatus": cast_status,
        "VoiceActor": voice_actor, "VoiceType": voice_type,
        "THAudio": th_audio, "FloatAudio": float_audio,
        "AuditionLineA": a, "AuditionLineB": b, "AuditionLineC": c,
        "Notes": "; ".join(notes), "WikiLink": wiki_link,
        "ImageFile": (stem + os.path.splitext(matched_images[stem])[1].lower()) if stem in matched_images else "",
        "InVockScope": "Yes",
        "THATVoiceActor": that_entry.get("va", ""),
        "THATLink": that_entry.get("links", ""),
    })

# ---------- wiki-only additions ----------
existing_stems = {c[0] for c in CHARACTERS}
existing_names_canon = {canon(c[1]) for c in CHARACTERS}
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
    that_entry_wiki = that_by_name.get(canon(r["name"]), {})
    fo2rpu_wiki = fo2rpu_by_stem.get(r["stem"], [])
    wiki_mod_list = [m for m, _l in fo2rpu_wiki]
    if that_entry_wiki.get("va"):
        wiki_mod_list.append("THAT")
    rows.append({
        "Name": r["name"], "MsgStem": r["stem"], "Prefix": "", "Location": r["section"],
        "Mod": ", ".join(wiki_mod_list), "Status": "Not in VOCK scope", "CastStatus": "", "VoiceActor": "",
        "VoiceType": "", "THAudio": "", "FloatAudio": "", "AuditionLineA": "", "AuditionLineB": "",
        "AuditionLineC": "", "Notes": "Wiki-only; no VOCK dialogue tagging", "WikiLink": "",
        "ImageFile": "", "InVockScope": "No",
        "THATVoiceActor": that_by_name.get(canon(r["name"]), {}).get("va", ""),
        "THATLink": that_by_name.get(canon(r["name"]), {}).get("links", ""),
    })

print(f"Total rows: {len(rows)} ({sum(1 for r in rows if r['InVockScope']=='Yes')} VOCK-scope, {sum(1 for r in rows if r['InVockScope']=='No')} wiki-only)")

# ---------- write CSV ----------
csv_path = os.path.join(DATA_DIR, "character_table.csv")
fieldnames = ["Name","MsgStem","Prefix","Location","Mod","Status","CastStatus","VoiceActor","VoiceType",
              "THAudio","FloatAudio","AuditionLineA","AuditionLineB","AuditionLineC","Notes","WikiLink","ImageFile","InVockScope",
              "THATVoiceActor","THATLink"]
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
