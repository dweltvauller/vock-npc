#!/usr/bin/env python3
"""Converts data/character_table.csv (the hand-edited master) into
data/character_table.json and data/character_table.js for index.html.

This is a pure 1:1 format conversion -- it reads no other file and applies
no merging logic. All editing happens directly in the CSV (Excel, Sheets,
or a text editor); re-run this after every edit to refresh the page.

Cells that hold more than one value for a row (an NPC with multiple
msg/int files and/or audio-tag prefixes, e.g. Kaga's 5 encounter files, or
a photo that differs per dialogue file, e.g. Dalia) use a literal newline
between values inside the cell -- csv.DictReader preserves that as \\n in
the string, which is what's written out here unchanged.
"""
import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "character_table.csv")
JSON_PATH = os.path.join(DATA_DIR, "character_table.json")
JS_PATH = os.path.join(DATA_DIR, "character_table.js")


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
        f.write("\n")

    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write("window.CHARACTER_TABLE = ")
        json.dump(rows, f, indent=1, ensure_ascii=False)
        f.write(";\n")

    print(f"Wrote {len(rows)} rows to {os.path.relpath(JSON_PATH)} and {os.path.relpath(JS_PATH)}")


if __name__ == "__main__":
    main()
