#!/usr/bin/env python3
"""
Fetch a Zotero collection's items + PDFs to a local folder.

Usage:
  python fetch_collection.py <collection_name> [--output <dir>] [--group <group_id>]

Env vars required:
  ZOTERO_API_KEY   - Get at https://www.zotero.org/settings/keys
  ZOTERO_USER_ID   - Shown at https://www.zotero.org/settings/keys
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_BASE = "https://api.zotero.org"


def headers():
    key = os.environ.get("ZOTERO_API_KEY")
    if not key:
        sys.exit("ERROR: ZOTERO_API_KEY not set. Get one at https://www.zotero.org/settings/keys")
    return {"Zotero-API-Key": key, "Zotero-API-Version": "3"}


def library_path(group_id):
    if group_id:
        return f"/groups/{group_id}"
    user_id = os.environ.get("ZOTERO_USER_ID")
    if not user_id:
        sys.exit("ERROR: ZOTERO_USER_ID not set (or pass --group)")
    return f"/users/{user_id}"


def paginated_get(url, params=None):
    """Fetch all pages of a Zotero API endpoint."""
    params = dict(params or {})
    params.setdefault("limit", 100)
    results = []
    start = 0
    while True:
        params["start"] = start
        r = requests.get(url, headers=headers(), params=params)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        results.extend(batch)
        if len(batch) < params["limit"]:
            break
        start += params["limit"]
    return results


def find_collection(lib, name):
    """Find a collection by name (case-insensitive). Exits with suggestions if not found."""
    collections = paginated_get(f"{API_BASE}{lib}/collections")
    exact = [c for c in collections if c["data"]["name"].lower() == name.lower()]
    if exact:
        return exact[0]["key"], exact[0]["data"]["name"]
    partial = [c for c in collections if name.lower() in c["data"]["name"].lower()]
    if partial:
        print(f"No exact match for '{name}'. Close matches:")
        for c in partial[:10]:
            print(f"  - {c['data']['name']}")
        sys.exit(1)
    sys.exit(f"No collection matching '{name}' in library")


def get_collection_items(lib, key):
    """Top-level items in a collection (excludes child attachments)."""
    return paginated_get(f"{API_BASE}{lib}/collections/{key}/items/top")


def get_children(lib, item_key):
    """Children of an item (usually attachments). Paginated in case of >100."""
    return paginated_get(f"{API_BASE}{lib}/items/{item_key}/children")


def download_file(lib, item_key, dest):
    """Download attachment file. Returns 'cached' | 'downloaded' | 'failed: <reason>'."""
    if dest.exists() and dest.stat().st_size > 0:
        return "cached"
    r = requests.get(f"{API_BASE}{lib}/items/{item_key}/file", headers=headers(), stream=True)
    if r.status_code != 200:
        return f"failed ({r.status_code})"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return "downloaded"


def safe_name(s, max_len=80):
    keep = "-_.() "
    cleaned = "".join(c for c in (s or "") if c.isalnum() or c in keep).strip()
    return cleaned[:max_len] or "untitled"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("collection", help="Collection name (case-insensitive, partial match ok)")
    p.add_argument("--output", help="Output directory (default: ./zotero_cache/<collection>/)")
    p.add_argument("--group", help="Group library ID (instead of personal library)")
    args = p.parse_args()

    lib = library_path(args.group)
    print(f"Looking up collection '{args.collection}'...")
    coll_key, coll_name = find_collection(lib, args.collection)
    print(f"Found: {coll_name} ({coll_key})")

    output = Path(args.output or f"./zotero_cache/{safe_name(coll_name)}").expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    print(f"Output: {output}\n")

    items = get_collection_items(lib, coll_key)
    print(f"{len(items)} items in collection\n")

    index = []
    for i, item in enumerate(items, 1):
        data = item["data"]
        title = data.get("title", "(no title)")
        year = (data.get("date") or "")[:4] or "nodate"
        creators = data.get("creators", [])
        first_last = (creators[0].get("lastName") or creators[0].get("name") or "anon") if creators else "anon"
        etal = "_etal" if len(creators) > 1 else ""

        entry = {
            "key": item["key"],
            "title": title,
            "year": year,
            "authors": [
                f"{c.get('lastName', '')}, {c.get('firstName', '')}".strip(", ")
                for c in creators
                if c.get("lastName") or c.get("name")
            ],
            "abstract": data.get("abstractNote", ""),
            "doi": data.get("DOI", ""),
            "url": data.get("url", ""),
            "item_type": data.get("itemType", ""),
            "pdf_path": None,
        }

        # Find PDF attachment among children
        children = get_children(lib, item["key"])
        pdf = next(
            (c for c in children if c["data"].get("contentType") == "application/pdf"),
            None,
        )

        short_title = safe_name(title, 50)
        prefix = f"[{i}/{len(items)}]"
        if pdf:
            filename = f"{safe_name(first_last)}{etal}_{year}_{short_title}.pdf"
            dest = output / filename
            status = download_file(lib, pdf["key"], dest)
            entry["pdf_path"] = str(dest)
            print(f"{prefix} [{status}] {filename}")
        else:
            print(f"{prefix} [no PDF] {first_last}{etal} {year} — {title[:60]}")

        index.append(entry)

    index_path = output / "index.json"
    index_path.write_text(json.dumps(index, indent=2))

    with_pdf = sum(1 for e in index if e["pdf_path"])
    print(f"\nDone. {with_pdf}/{len(index)} items have PDFs.")
    print(f"Index: {index_path}")


if __name__ == "__main__":
    main()
