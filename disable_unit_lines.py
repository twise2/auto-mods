#! /usr/bin/env python3
"""Patch futuravailableunits.json to remove native unit-line access for
specific civs - e.g. Knight/Cavalier/Paladin for Turks/Huns, matching the
"steppe civs shouldn't also have Western knights" flavor rule discussed in
NOTES-civ-identity-expansion.md.

Unlike everything else in this repo (which only ever ADDS access, via a
self-triggering tech in the .dat), this is the first REMOVAL of a civ's
native access - and the .dat turns out not to encode that distinction at
all. Confirmed empirically: Franks (has Knight) and Aztecs (confirmed
lacks it) are byte-identical in the .dat for unit.enabled, train_locations,
and every tech/effect referencing Knight/Cavalier/Paladin.

The real per-civ gate lives in a separate file - futuravailableunits.json,
in the same resources/_common/dat folder as civilizations.json - which
lists, per civ, exactly which units each of that civ's buildings can train
and at what age. Confirmed by diffing Aztecs (empty Knight/Cavalier/Paladin
entries under their Stable) against Franks/Turks/Huns (real entries) -
Turks specifically shows Knight+Cavalier but no Paladin, matching exactly
what the real CivTechTrees UI already showed for them.

UNVERIFIED whether this file is load-bearing for the actual training gate
or only powers a UI feature (the "next age" unlock preview tooltip) - the
same category of uncertainty that applied to CivTechTrees before it was
confirmed in a real game. Needs an in-game test before trusting it fully.
"""
import argparse
import json
import logging
from pathlib import Path

# civ name (as it appears as a top-level key in futuravailableunits.json,
# not necessarily the same as the .dat's Civ.name) -> unit ids to strip
# from every building entry that offers them.
DISABLE_UNITS_FOR_CIV = {
    'Turks': {38, 283, 569},  # Knight, Cavalier, Paladin
    'Huns': {38, 283, 569},
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Source futuravailableunits.json')
    parser.add_argument('output', type=Path, help='Where to write the patched file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    with args.source.open(encoding='utf-8') as f:
        data = json.load(f)

    for civ_name, unit_ids in DISABLE_UNITS_FOR_CIV.items():
        civ_entry = data.get(civ_name)
        if civ_entry is None:
            logging.warning(f'civ {civ_name!r} not found in {args.source}')
            continue
        for building in civ_entry.get('Buildings', []):
            before = len(building.get('Units', []))
            building['Units'] = [u for u in building.get('Units', []) if u.get('ID') not in unit_ids]
            removed = before - len(building['Units'])
            if removed:
                logging.info(f'{civ_name}: removed {removed} unit(s) from {building.get("Name")}')

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding='utf-8') as f:
        json.dump(data, f)
    logging.info(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
