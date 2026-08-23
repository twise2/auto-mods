#! /usr/bin/env python3
"""Patch futuravailableunits.json to mirror what regional_heritage.py's
grants and removals actually do, for whatever UI feature this file powers
(the F11 tech-tree preview, most likely - see below).

CONFIRMED (via real in-game testing this session, not assumed) that this
file is NOT load-bearing for actual training access: Chinese kept training
Knight instead of the granted Hei-Kuang Cavalry even after this script
"removed" Knight from their entry here, because the real .dat still had
Knight fully enabled. Both problems this file used to be the ONLY fix for
now have real .dat-level fixes instead:

- Removing a civ's native access (e.g. Knight/Cavalier/Paladin for Turks/
  Huns): mods.util.disable_unit_line_for_civ is a real .dat mutation now -
  it researches a self-triggering tech with TYPE_ENABLE_DISABLE_UNIT(b=0)
  commands, the same mechanism vanilla's own Mule Cart tech uses to
  disable Lumber Camp/Mining Camp for Georgians/Armenians (confirmed via
  direct .dat inspection). This script still traces those calls (see
  trace_granted_units) purely to keep this JSON file in sync for its UI
  purpose, not because it's needed for the removal to work anymore.
- Real button collisions: see audit_collisions.py instead, which scans
  the .dat's actual tech/effect data directly rather than relying on this
  file's per-civ listings (which are curated/incomplete - confirmed they
  missed a real collision: Packed Trebuchet, enabled at Castle button 2
  for every civ that researches the common "Trebuchet" tech, was never
  listed here for any civ, yet silently defeated every hero unit this
  mod placed at that button in real games).

This script still runs and still does something real for the UI, but
should not be trusted as a source of truth for what's actually trainable -
use audit_collisions.py and direct .dat tech inspection for that instead.
"""
import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path

from genieutils.datfile import DatFile

from mods import heroes_and_villains, regional_heritage


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


def trace_granted_units(data: DatFile) -> tuple[dict[int, set[int]], dict[int, set[int]], dict[int, set[int]],
                                                  dict[tuple[int, int], list[tuple[int, int]]]]:
    """(newly_enabled, line_upgraded, disabled, location_overrides) for
    everything regional_heritage.mod() (and heroes_and_villains.mod()'s
    plain enables) actually does. Mirrors sync_tech_trees.py's
    trace_grants - intercepts the granting/disabling calls instead of
    applying them, so this can run against an unmodified .dat.

    Kept separate on purpose: a genuinely NEW unit (enable_unit_for_civ, or
    a type=2 effect command) can collide with something already at its
    button - a real bug to fix. A unit reached by upgrading an existing
    line in place (upgrade_unit_for_civ, or a type=3 effect command) is
    SUPPOSED to share its base unit's button - that's not a collision, the
    base tiers are its own prerequisites (e.g. Legionary needs Byzantines'
    Militia/Man-at-Arms/Long Swordsman to remain trainable, since that's
    the path to it). Only newly_enabled goes through collision detection.
    disabled comes from disable_unit_line_for_civ calls - the deliberate
    historical-identity removals, unrelated to collision detection.
    location_overrides comes from set_train_locations_for_civ calls - a
    per-(civ, unit) replacement for the unit's generic default
    train_locations, needed when the default would itself collide (e.g.
    Temple Guard moved off Aztecs' native Eagle Warrior button).
    """
    enabled: dict[int, set[int]] = defaultdict(set)
    upgraded: dict[int, set[int]] = defaultdict(set)
    disabled: dict[int, set[int]] = defaultdict(set)
    location_overrides: dict[tuple[int, int], list[tuple[int, int]]] = {}

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

    def rec_set_locations(data, civ_id, unit_id, locations):
        location_overrides[(civ_id, unit_id)] = list(locations)

    def noop_reskin(data, civ_id, unit_id, donor_unit_id):
        pass

    def rec_disable_line(data, civ_id, unit_ids, required_tech):
        disabled[civ_id] |= set(unit_ids)

    def rec_research_elite(data, civ_id, upgrade_pairs, extra_required_techs, building_id, button_id,
                            resource_costs, research_time, name, age_tech=None):
        for _base_unit_id, upgraded_unit_id in upgrade_pairs:
            upgraded[civ_id].add(upgraded_unit_id)

    import mods.util as util
    orig = (util.enable_unit_for_civ, util.upgrade_unit_for_civ, util.grant_effect_to_civ,
            util.set_train_locations_for_civ, util.reskin_unit_for_civ, util.disable_unit_line_for_civ,
            util.research_elite_upgrade_for_civ)
    regional_heritage.enable_unit_for_civ = rec_enable
    regional_heritage.upgrade_unit_for_civ = rec_upgrade
    regional_heritage.grant_effect_to_civ = rec_grant_effect
    regional_heritage.set_train_locations_for_civ = rec_set_locations
    regional_heritage.reskin_unit_for_civ = noop_reskin
    regional_heritage.disable_unit_line_for_civ = rec_disable_line
    regional_heritage.research_elite_upgrade_for_civ = rec_research_elite
    heroes_and_villains.enable_unit_for_civ = rec_enable
    # Real, previously-undiscovered gap: heroes_and_villains.mod() was never
    # actually called here - only regional_heritage.mod() was - so every
    # hero grant (all ~60 civs) has been invisible to this collision checker
    # since it was written. The heroes_and_villains.enable_unit_for_civ
    # patch above was dead code with nothing to intercept. Call both, in
    # the same order build-local-mod.sh/auto-mod.py actually apply them
    # (heroes-and-villains before regional-heritage), so ids/ordering match
    # a real build.
    heroes_and_villains.mod(data)
    regional_heritage.mod(data)
    (util.enable_unit_for_civ, util.upgrade_unit_for_civ, util.grant_effect_to_civ,
     util.set_train_locations_for_civ, util.reskin_unit_for_civ, util.disable_unit_line_for_civ,
     util.research_elite_upgrade_for_civ) = orig

    return enabled, upgraded, disabled, location_overrides


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


def unit_locations(data: DatFile, civ_id: int, unit_id: int,
                    overrides: dict[tuple[int, int], list[tuple[int, int]]]) -> list[tuple[int, int]]:
    """Where this civ's copy of unit_id actually trains from: the
    set_train_locations_for_civ override if one was traced for this exact
    (civ, unit) pair, otherwise the unit's real default train_locations
    straight from the .dat (a unit can train from more than one building,
    e.g. Temple Guard from both Barracks and Monastery)."""
    if (civ_id, unit_id) in overrides:
        return overrides[(civ_id, unit_id)]
    base = data.civs[0]
    u = base.units[unit_id] if unit_id < len(base.units) else None
    if u is None or not u.creatable:
        return []
    return [(tl.unit_id, tl.button_id) for tl in u.creatable.train_locations if tl.unit_id != -1]


def find_button_collisions(data: DatFile, civ_filenames: dict[int, str], granted: dict[int, set[int]],
                            overrides: dict[tuple[int, int], list[tuple[int, int]]],
                            available_units: dict) -> dict[str, set[int]]:
    """For every granted unit, find any OTHER unit that civ already has
    listed under the same building in futuravailableunits.json and that
    trains from the exact same button - a real collision, since only one
    unit can actually occupy a given (building, button) slot. Uses the
    granted unit's actual (possibly overridden) location(s), not just its
    generic default - a set_train_locations_for_civ override exists
    specifically to dodge a collision the default would cause, so checking
    the default here would just rediscover the problem the override
    already solved. Excludes anything in the granted unit's own upgrade
    family (see build_upgrade_families) - those are the same progression,
    not a competing unit. Returns {civ_name: {unit_id, ...}}, the same
    shape disable_unit_line_for_civ calls trace to, so the two can be
    merged.
    """
    base = data.civs[0]
    families = build_upgrade_families(data)
    collisions: dict[str, set[int]] = defaultdict(set)

    def default_location(unit_id: int):
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
            same_family = families.get(unit_id, {unit_id})
            for building_id, button_id in unit_locations(data, civ_id, unit_id, overrides):
                if building_id == BUILD_MENU_ID:
                    continue
                building = buildings_by_id.get(building_id)
                if building is None:
                    continue
                for other in building.get('Units', []):
                    other_id = other.get('ID')
                    if other_id is None or other_id == unit_id or other_id in unit_ids or other_id in same_family:
                        continue
                    if default_location(other_id) == (building_id, button_id):
                        collisions[civ_key].add(other_id)
    return collisions


def build_donor_templates(available_units: dict) -> dict[int, dict]:
    """unit_id -> a representative {ID, Name, RequiredAge, ...} dict, copied
    from wherever it already appears (any civ) in the source json. Reused
    when adding that same unit to a newly-granted civ, so the added entry's
    Name/RequiredAge match the game's own data instead of being guessed.
    """
    templates: dict[int, dict] = {}
    for civ_entry in available_units.values():
        for building in civ_entry.get('Buildings', []):
            for unit in building.get('Units', []):
                uid = unit.get('ID')
                if uid is not None and uid not in templates:
                    templates[uid] = dict(unit)
    return templates


def building_names(available_units: dict) -> dict[int, str]:
    """building_id -> its display Name, scanned from the source json
    (consistent across every civ that already lists that building)."""
    names: dict[int, str] = {}
    for civ_entry in available_units.values():
        for building in civ_entry.get('Buildings', []):
            bid = building.get('ID')
            if bid is not None and bid not in names:
                names[bid] = building.get('Name')
    return names


def add_granted_units(data: DatFile, civ_filenames: dict[int, str], available_units: dict,
                       newly_enabled: dict[int, set[int]], upgraded: dict[int, set[int]],
                       overrides: dict[tuple[int, int], list[tuple[int, int]]]):
    """The other half of what this script needs to do: every unit
    enable_unit_for_civ/upgrade_unit_for_civ grants also needs a real entry
    added to futuravailableunits.json, or the civ never actually gains
    visible/tracked access to it - collision removals alone can leave a civ
    strictly worse off than vanilla (native unit removed, its replacement
    never added). Sources each entry from wherever the unit already exists
    for its real donor civ when possible (matches the game's own
    Name/RequiredAge); falls back to a reasonable guess (the .dat's own
    unit name, Castle/Imperial Age matching this mod's own TECH_CASTLE_BUILT
    /TECH_REQUIREMENT_IMPERIAL_AGE gates) only for genuinely unclaimed units
    with no existing donor entry anywhere (e.g. War Chariot 2150/2151).
    """
    templates = build_donor_templates(available_units)
    b_names = building_names(available_units)
    base = data.civs[0]

    def add_one(civ_id: int, unit_id: int, default_age: int):
        civ_key = civ_filenames.get(civ_id)
        civ_entry = available_units.get(civ_key)
        if civ_entry is None:
            return
        u = base.units[unit_id] if unit_id < len(base.units) else None
        unit_name = u.name if u is not None else str(unit_id)
        template = templates.get(unit_id) or {'ID': unit_id, 'Name': unit_name, 'RequiredAge': default_age}
        buildings = civ_entry.setdefault('Buildings', [])
        buildings_by_id = {b.get('ID'): b for b in buildings}
        for building_id, button_id in unit_locations(data, civ_id, unit_id, overrides):
            building = buildings_by_id.get(building_id)
            if building is None:
                building = {'ID': building_id, 'Name': b_names.get(building_id, ''), 'Techs': [], 'Units': []}
                buildings.append(building)
                buildings_by_id[building_id] = building
            existing_ids = {u.get('ID') for u in building.get('Units', [])}
            if unit_id not in existing_ids:
                building.setdefault('Units', []).append(dict(template))
                logging.info(f'{civ_key}: added {template.get("Name")} to {building.get("Name")}')

    for civ_id, unit_ids in newly_enabled.items():
        for unit_id in unit_ids:
            add_one(civ_id, unit_id, default_age=3)
    for civ_id, unit_ids in upgraded.items():
        for unit_id in unit_ids:
            add_one(civ_id, unit_id, default_age=4)


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
    newly_enabled, upgraded, disabled, overrides = trace_granted_units(data)

    with args.source.open(encoding='utf-8') as f:
        available_units = json.load(f)

    collisions = find_button_collisions(data, civ_filenames, newly_enabled, overrides, available_units)
    for civ_key, unit_ids in collisions.items():
        logging.info(f'{civ_key}: auto-detected button collision, disabling {sorted(unit_ids)}')

    add_granted_units(data, civ_filenames, available_units, newly_enabled, upgraded, overrides)

    disable_map: dict[str, set[int]] = defaultdict(set)
    for civ_id, unit_ids in disabled.items():
        civ_key = civ_filenames.get(civ_id)
        if civ_key is not None:
            disable_map[civ_key] |= unit_ids
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
