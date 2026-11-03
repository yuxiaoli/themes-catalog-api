"""Reproduce category popularity from a pinned upstream declaration; no palette export."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a5ca684f9aa82bc20ef62990eed7df9bc3408fa7"
BLOB = "d012ca85cb25a1575ef93559860d8e76d8457982"
SOURCE_PATH = "app/pages/index.vue"
PALETTE_REVISION = "3277da1a295142cd8664e0657c5a3c2a44cc520a"

def extract(source):
    raw = source.encode("utf-8")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != BLOB:
        raise ValueError("Upstream source does not match the reviewed Git blob")
    block = re.search(r"const POPULAR_THEME_NAMES = new Set\(\[([\s\S]*?)\]\);", source)
    if not block:
        raise ValueError("Upstream declaration is missing")
    names = re.findall(r"'([^']+)'", block[1])
    if len(names) != 48 or len(set(names)) != len(names):
        raise ValueError("Unexpected upstream membership")
    return {
        "source": {
            "repository": "Gogh-Co/gogh-website",
            "revision": REVISION,
            "path": SOURCE_PATH,
            "url": f"https://github.com/Gogh-Co/gogh-website/blob/{REVISION}/{SOURCE_PATH}#L499-L548",
            "blob_sha": BLOB,
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "names": names,
    }

def build(index, snapshot):
    names = snapshot["names"]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate upstream names")
    rows = index["entries"] + index["excluded"]
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate catalog IDs")
    flags = {}
    ordered_ids, unmatched, unavailable = [], [], []
    candidates = [row for row in rows if row["source_id"] == "gogh"]
    for row in candidates:
        flags[row["id"]] = row["name"] in names
    for position, name in enumerate(names, 1):
        matches = [row for row in candidates if row["name"] == name]
        if len(matches) != 1:
            # Ambiguous identities must not inherit a positive flag.
            for row in matches:
                flags.pop(row["id"], None)
            unmatched.append({"name": name, "position": position,
                              "reason": "absent" if not matches else "ambiguous"})
            continue
        row = matches[0]
        ordered_ids.append(row["id"])
        if "reason" in row:
            unavailable.append({"id": row["id"], "name": name,
                                "position": position, "reason": row["reason"]})
    return {
        "version": "1",
        "definition": "Membership in Gogh website POPULAR_THEME_NAMES; not an independent ranking.",
        "source": snapshot["source"],
        "catalog_source_revision": PALETTE_REVISION,
        "ordering": "upstream-declaration; Gogh's Popular UI shuffles this subset",
        "flags": flags,
        "order": ordered_ids,
        "unmatched": unmatched,
        "unavailable": unavailable,
    }

def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-file", type=Path, help="Optional exact pinned index.vue for source re-verification")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    snapshot_path = ROOT / "metadata/gogh-popular.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if args.source_file:
        verified = extract(args.source_file.read_bytes().decode("utf-8"))
        if verified != snapshot:
            raise ValueError("Saved membership/provenance differs from pinned source")
    index_path = ROOT / "api/v1/terminal/index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    # This feature consumes only the approved public export.
    for entry in index["entries"]:
        if entry["source_id"] == "gogh":
            theme = json.loads((ROOT / entry["path"]).read_text(encoding="utf-8"))["theme"]
            if theme["provenance"]["revision"] != PALETTE_REVISION:
                raise ValueError("Review the changed public palette source before refreshing membership")
    index["popularity"] = build(index, snapshot)
    output = encoded(index)
    if args.check:
        if index_path.read_text(encoding="utf-8") != output:
            raise ValueError("Popularity metadata is stale; run the generator")
    else:
        index_path.write_text(output, encoding="utf-8", newline="\n")
    metadata = index["popularity"]
    print(json.dumps({"popular": sum(v is True for v in metadata["flags"].values()),
                      "unmatched": metadata["unmatched"], "unavailable": metadata["unavailable"]}))

if __name__ == "__main__":
    main()
