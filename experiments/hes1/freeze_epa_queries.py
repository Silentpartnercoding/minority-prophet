#!/usr/bin/env python3
"""Freeze value-blind EPA third-site queries from metadata and availability."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.hgd1.run_hgd1 import MAX_REFERENCE_KM, haversine

ARCHIVE = ROOT / "artifacts" / "hgd1-source" / "daily_88101_2025.zip"
SOURCE_MANIFEST = ROOT / "experiments" / "hgd1" / "source-manifest.json"
OUTPUT = ROOT / "experiments" / "hes1" / "epa-query-selection.json"


def main() -> None:
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() != manifest["archiveSha256"]:
        raise RuntimeError("EPA archive hash mismatch")
    available = defaultdict(set)
    context_sites = defaultdict(set)
    coordinates = {}
    with zipfile.ZipFile(ARCHIVE) as archive, archive.open(manifest["memberName"]) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        for row in reader:
            try:
                # Validate availability without retaining or comparing the evidence value.
                value = float(row["Arithmetic Mean"])
                count = int(row["Observation Count"])
                latitude = float(row["Latitude"])
                longitude = float(row["Longitude"])
            except (TypeError, ValueError):
                continue
            if count <= 0 or not math.isfinite(value):
                continue
            site = (row["State Code"], row["County Code"], row["Site Num"])
            context = (row["Date Local"], row["Sample Duration"], row["Units of Measure"])
            available[(context, site)].add(str(row["POC"]))
            context_sites[context].add(site)
            coordinates[site] = (latitude, longitude)

    collocated = sorted({site for (_, site), pocs in available.items() if len(pocs) >= 2})
    development_site = collocated[0]
    selections = []
    for context, context_site_set in sorted(context_sites.items()):
        sites = sorted(context_site_set)
        for site in sites:
            if site == development_site or len(available[(context, site)]) < 2:
                continue
            candidates = sorted((haversine(coordinates[site], coordinates[other]), other)
                                for other in sites if other != site
                                and haversine(coordinates[site], coordinates[other]) <= MAX_REFERENCE_KM)
            if not candidates:
                continue
            reference_distance, reference = candidates[0]
            third = next(((distance, candidate) for distance, candidate in candidates
                          if candidate != reference), None)
            selections.append({
                "context": list(context),
                "site": list(site),
                "referenceSite": list(reference),
                "referenceDistanceKm": reference_distance,
                "selectedThirdSite": list(third[1]) if third else None,
                "selectedThirdDistanceKm": third[0] if third else None,
                "selectionRule": "nearest available distinct site after frozen reference",
            })
    packet = {
        "schema": "minority-prophet.hes1.epa-query-selection.v1",
        "archiveSha256": manifest["archiveSha256"],
        "valueBlindFields": ["context", "site identity", "POC availability", "coordinates"],
        "retainedCandidateEvidenceValues": False,
        "selections": selections,
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
