#! /usr/bin/env python3
"""Patch futuravailableunits.json for two related reasons, both about
per-civ unit-line access this repo's other tooling can't touch (see below
for why the .dat itself doesn't encode this):

1. Deliberate historical-identity removals - e.g. Knight/Cavalier/Paladin
   for Turks/Huns. The civ -> unit-ids decisions live in
   mods/regional_heritage.py's DISABLE_UNIT_LINES_FOR_CIV, alongside every
   other civ-identity decision this project makes; this script just applies
   that config to the real file.

2. Automatic button-collision fixes. When regional_heritage.mod() grants a
   civ a unit that shares its native (building, button) training slot with
   something that civ already has natively, the two units silently fight
   over the same menu button unless one is removed. This is figured out
   from the real data every run, not hand-maintained: trace every unit
   regional_heritage.mod() actually grants (mirrors sync_tech_trees.py's
   trace_grants), look up each granted unit's real (building, button) in
   the .dat, then for every OTHER unit that civ already has listed under
   that same building in futuravailableunits.json, check whether it trains
   from the exact same button - if so, it's a real collision and gets
   removed. (Confirmed this class of bug for real: Rocket Cart -> Japanese
   shares Siege Workshop button 2 with Japanese's own real, natively-active
   Mangonel/Onager - both showed up in futuravailableunits.json before this
   fix, meaning both would have been simultaneously offered at one button.)

Why this file, and not the .dat: unlike every unit-granting mechanism this
repo already had (which only ever ADDS access via a self-triggering tech),
neither removing a civ's native access nor un-granting a colliding native
default is something the .dat's own effect/tech system reliably controls.
Confirmed empirically for Knight/Cavalier/Paladin: Franks (has Knight) and
Aztecs (confirmed lacks it) are byte-identical in the .dat for
unit.enabled, train_locations, and every tech/effect referencing those
three unit ids. The real per-civ gate lives here instead - a separate file,
in the same resources/_common/dat folder as civilizations.json, listing
exactly which units each civ's buildings can train and at what age.
Confirmed Mangonel/Onager are ALSO tracked here for Japanese (not just
Knight-style exclusions), so the same file has to be the fix for both
categories of removal.

UNVERIFIED whether this file is load-bearing for the actual training gate
or only powers a UI feature (the "next age" unlock preview tooltip) - the
same category of uncertainty that applied to CivTechTrees before it was
confirmed in a real game. Needs an in-game test before trusting it fully.
"""
import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path

from genieutils.datfile import DatFile

from mods import heroes_and_villains, regional_heritage
from mods.regional_heritage import DISABLE_UNIT_LINES_FOR_CIV


def civ_name_to_futuravailableunits_key(data: DatFile, civilizations_json_path: Path) -> dict[int, str]:
    """civ_id -> futuravailableunits.json's own top-level key for that civ -
    matches civilizations.json's internal_name exactly (e.g. "Byzantines"
    plural), confirmed by inspection - NOT the .dat's own Civ.name."""
    with civilizations_json_path.open(encoding='utf-8') as f:
        civ_entries = json.load(f)['civilization_list']
    return {civ_id: civ_entries[civ_id]['internal_name'] for civ_id in range(len(data.civs))}


# The villager "Builder" build-menu (id 118) lists constructable BUILDINGS,
# not trained combat units - a completely different button-numbering scheme
# where multiple options are simultaneously visible rather than each button
# being one exclusive training slot. Matching (building, button) pairs
# there produces false positives (confirmed: it flagged Castle itself as
# "colliding" with a newly-granted building). Building grants in this repo
# are verified safe by hand elsewhere (no collision ever found across the
# whole session for Caravanserai/Donjon/Krepost/Feitoria/etc) - skip it here.
BUILD_MENU_ID = 118


def trace_granted_units(data: DatFile) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """(newly_enabled, line_upgraded) civ_id -> {unit_id, ...} for
    everything regional_heritage.mod() (and heroes_and_villains.mod()'s
    plain enables) actually grants. Mirrors sync_tech_trees.py's
    trace_grants - intercepts the granting calls instead of applying them,
    so this can run against an unmodified .dat.

    Kept separate on purpose: a genuinely NEW unit (enable_unit_for_civ, or
    a type=2 effect command) can collide with something already at its
    button - a real bug to fix. A unit reached by upgrading an existing
    line in place (upgrade_unit_for_civ, or a type=3 effect command) is
    SUPPOSED to share its base unit's button - that's not a collision, the
    base tiers are its own prerequisites (e.g. Legionary needs Byzantines'
    Militia/Man-at-Arms/Long Swordsman to remain trainable, since that's
    the path to it). Only newly_enabled goes through collision detection.
    """
    enabled: dict[int, set[int]] = defaultdict(set)
    upgraded: dict[int, set[int]] = defaultdict(set)

    def rec_enable(data, civ_id, unit_id, required_tech):
        enabled[civ_id].add(unit_id)

    def rec_upgrade(data, civ_id, base_unit_id, upgraded_unit_id, required_tech):
        upgraded[civ_id].add(upgraded_unit_id)

    def rec_grant_effect(data, civ_id, effect_commands, required_tech, name):
        for cmd in effect_commands:
            if cmd.type == 2 and cmd.b == 1:
                enabled[civ_id].add(cmd.a)
            elif cmd.type == 3:
                upgraded[civ_id].add(cmd.b)
        return -1

    def noop_button(data, civ_id, unit_id, building_id, button_id):
        pass

    def noop_reskin(data, civ_id, unit_id, donor_unit_id):
        pass

    import mods.util as util
    orig = (util.enable_unit_for_civ, util.upgrade_unit_for_civ, util.grant_effect_to_civ,
            util.set_train_button_for_civ, util.reskin_unit_for_civ)
    regional_heritage.enable_unit_for_civ = rec_enable
    regional_heritage.upgrade_unit_for_civ = rec_upgrade
    regional_heritage.grant_effect_to_civ = rec_grant_effect
    regional_heritage.set_train_button_for_civ = noop_button
    regional_heritage.reskin_unit_for_civ = noop_reskin
    heroes_and_villains.enable_unit_for_civ = rec_enable
    regional_heritage.mod(data)
    (util.enable_unit_for_civ, util.upgrade_unit_for_civ, util.grant_effect_to_civ,
     util.set_train_button_for_civ, util.reskin_unit_for_civ) = orig

    return enabled, upgraded


def build_upgrade_families(data: DatFile) -> dict[int, set[int]]:
    """unit_id -> every unit id connected to it by a real vanilla
    TYPE_UPGRADE_UNIT tech (Knight->Cavalier->Paladin, Camel Rider->Heavy
    Camel Rider, Cavalry Archer->Heavy Cavalry Archer, etc), transitively
    closed and including the unit itself. Every tier of the same
    progression trains from the identical (building, button) by design -
    that's not a collision, it's one continuous line. Scanned from the real
    tech/effect data rather than hardcoded, so it stays correct as new
    civs/units get added upstream.
    """
    parent: dict[int, int] = {}

    def find(x: int) -> int:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for t in data.techs:
        if t is None or t.effect_id < 0:
            continue
        for cmd in data.effects[t.effect_id].effect_commands:
            if cmd.type == 3 and cmd.a >= 0 and cmd.b >= 0:
                union(cmd.a, cmd.b)

    families: dict[int, set[int]] = defaultdict(set)
    for unit_id in list(parent):
        families[find(unit_id)].add(unit_id)
    return {unit_id: families[find(unit_id)] for unit_id in parent}


def find_button_collisions(data: DatFile, civ_filenames: dict[int, str], granted: dict[int, set[int]],
                            available_units: dict) -> dict[str, set[int]]:
    """For every granted unit, find any OTHER unit that civ already has
    listed under the same building in futuravailableunits.json and that
    trains from the exact same button - a real collision, since only one
    unit can actually occupy a given (building, button) slot. Excludes
    anything in the granted unit's own upgrade family (see
    build_upgrade_families) - those are the same progression, not a
    competing unit. Returns the same shape as DISABLE_UNIT_LINES_FOR_CIV so
    the two can be merged.
    """
    base = data.civs[0]
    families = build_upgrade_families(data)
    collisions: dict[str, set[int]] = defaultdict(set)

    def train_location(unit_id: int):
        u = base.units[unit_id] if unit_id < len(base.units) else None
        if u is None or not u.creatable or not u.creatable.train_locations:
            return None
        tl = u.creatable.train_locations[0]
        return (tl.unit_id, tl.button_id) if tl.unit_id != -1 else None

    for civ_id, unit_ids in granted.items():
        civ_key = civ_filenames.get(civ_id)
        civ_entry = available_units.get(civ_key)
        if civ_entry is None:
            continue
        buildings_by_id = {b.get('ID'): b for b in civ_entry.get('Buildings', [])}
        for unit_id in unit_ids:
            loc = train_location(unit_id)
            if loc is None:
                continue
            building_id, button_id = loc
            if building_id == BUILD_MENU_ID:
                continue
            building = buildings_by_id.get(building_id)
            if building is None:
                continue
            same_family = families.get(unit_id, {unit_id})
            for other in building.get('Units', []):
                other_id = other.get('ID')
                if other_id is None or other_id == unit_id or other_id in unit_ids or other_id in same_family:
                    continue
                other_loc = train_location(other_id)
                if other_loc == (building_id, button_id):
                    collisions[civ_key].add(other_id)
    return collisions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dat_filename', type=Path, help='The base .dat file to trace grants against')
    parser.add_argument('source', type=Path, help='Source futuravailableunits.json')
    parser.add_argument('civilizations_json', type=Path, help='Source civilizations.json')
    parser.add_argument('output', type=Path, help='Where to write the patched file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    data = DatFile.parse(args.dat_filename)
    civ_filenames = civ_name_to_futuravailableunits_key(data, args.civilizations_json)
    newly_enabled, _line_upgraded = trace_granted_units(data)

    with args.source.open(encoding='utf-8') as f:
        available_units = json.load(f)

    collisions = find_button_collisions(data, civ_filenames, newly_enabled, available_units)
    for civ_key, unit_ids in collisions.items():
        logging.info(f'{civ_key}: auto-detected button collision, disabling {sorted(unit_ids)}')

    disable_map: dict[str, set[int]] = defaultdict(set)
    for civ_name, unit_ids in DISABLE_UNIT_LINES_FOR_CIV.items():
        disable_map[civ_name] |= set(unit_ids)
    for civ_key, unit_ids in collisions.items():
        disable_map[civ_key] |= unit_ids

    for civ_name, unit_ids in disable_map.items():
        civ_entry = available_units.get(civ_name)
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
        json.dump(available_units, f)
    logging.info(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
