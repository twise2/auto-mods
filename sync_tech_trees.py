#! /usr/bin/env python3
"""Patch the CivTechTrees/<CIV>.json files so the in-game F11 tech tree screen
correctly shows every unit/building this mod's civs have been given.

The .dat file (what auto-mod.py edits) controls what a civ can actually build.
The F11 tech tree popup is generated from a *separate* set of JSON files
(resources/_common/dat/CivTechTrees/<CIV>.json) that auto-mod.py never
touches - without this script, every grant from regional_heritage.py/
heroes_and_villains.py would work in a real game but not show up when a
player checks the tech tree screen.

For each civ+unit this mod grants, find an existing civ that already has a
tech-tree entry for that same unit (its Node ID always matches the real .dat
unit id) and copy that entry into the new civ's file, marking it
"ResearchedCompleted" - the same status vanilla uses for units a civ can
already build without a research click, which matches exactly how every
grant in this mod is unlocked (see mods/util.py::enable_unit_for_civ).
"""
import argparse
import json
import logging
import shutil
from collections import defaultdict
from pathlib import Path

from genieutils.datfile import DatFile

from mods import heroes_and_villains, regional_heritage

# Node IDs that are buildings (live in civ_techs_buildings) rather than units
# (civ_techs_units). Everything else this mod grants is a unit.
BUILDING_NODE_IDS = {
    1021,  # Feitoria
    1665,  # Donjon
    1251,  # Krepost
    1189,  # Harbor
    1734, 1711, 1720,  # Folwark 1/2/3
    2556, 2558, 2560,  # Settlement 1/2/3
    1754,  # Caravanserai
    1808,  # Mule Cart
    1806,  # Fortified Church
}


# A handful of CivTechTrees filenames don't just match civilizations.json's
# internal_name.upper() - confirmed by diffing against the real directory
# listing rather than assumed.
FILENAME_OVERRIDES = {
    'MAGYARS': 'MAGYAR',
}

# These 3 node ids are granted by this mod but have no template anywhere in
# the real CivTechTrees data - not a bug, just no donor civ happens to own
# this exact age tier natively (confirmed: Poles' own Folwark file only has
# the base tier, Wu's own Jian Swordsman file only has the base tier, Incas'
# own Settlement file only has the base tier - the middle Age 2 tiers are
# missing too, but this mod never grants those, so they never get flagged).
# Derived from each one's own base-tier template instead of skipping them,
# so the output CivTechTrees data actually matches what the .dat grants
# rather than silently omitting it.
DERIVED_FROM_BASE_TIER = {
    1720: 1734,  # Folwark3 <- Folwark1 (Poles)
    2560: 2556,  # Settlement Age3 <- Settlement1 (Incas)
    1976: 1974,  # Elite Jian Swordsman <- Jian Swordsman (Wu)
}

# Elite/final-tier display name overrides - buildings (Folwark/Settlement)
# keep the same name across age tiers in the real data (confirmed: Folwark's
# own Age 2/3 upgrade techs don't rename it), units get the standard "Elite"
# prefix used everywhere else in this mod.
DERIVED_NODE_NAMES = {
    1976: 'Elite Jian Swordsman',
}


def civ_name_to_filename_map(data: DatFile, civilizations_json_path: Path) -> dict[int, str]:
    """civ_id -> CivTechTrees filename stem (e.g. 'BRITONS'), sourced from
    civilizations.json's internal_name - confirmed same list order as the
    .dat's own civs list, offset by Gaia at index 0."""
    with civilizations_json_path.open(encoding='utf-8') as f:
        civ_entries = json.load(f)['civilization_list']
    names = {civ_id: civ_entries[civ_id]['internal_name'].upper() for civ_id in range(len(data.civs))}
    return {civ_id: FILENAME_OVERRIDES.get(name, name) for civ_id, name in names.items()}


def trace_grants(data: DatFile) -> dict[int, set[int]]:
    """Re-run both mods with their unit-granting calls intercepted instead of
    applied, returning {civ_id: {unit_id, ...}} for every unit each civ ends
    up able to build. Mirrors the collision-checker technique used throughout
    this branch's development.
    """
    grants: dict[int, set[int]] = defaultdict(set)

    def record(civ_id: int, unit_id: int):
        grants[civ_id].add(unit_id)

    def rec_enable(data, civ_id, unit_id, required_tech):
        record(civ_id, unit_id)

    def rec_upgrade(data, civ_id, base_unit_id, upgraded_unit_id, required_tech):
        record(civ_id, upgraded_unit_id)

    def rec_grant_effect(data, civ_id, effect_commands, required_tech, name):
        for cmd in effect_commands:
            if cmd.type == 2 and cmd.b == 1:
                record(civ_id, cmd.a)
            elif cmd.type == 3:
                record(civ_id, cmd.b)
        return -1

    def noop_button(data, civ_id, unit_id, locations):
        pass

    def noop_reskin(data, civ_id, unit_id, donor_unit_id):
        pass

    import mods.util as util
    orig = (util.enable_unit_for_civ, util.upgrade_unit_for_civ, util.grant_effect_to_civ,
            util.set_train_locations_for_civ, util.reskin_unit_for_civ)
    regional_heritage.enable_unit_for_civ = rec_enable
    regional_heritage.upgrade_unit_for_civ = rec_upgrade
    regional_heritage.grant_effect_to_civ = rec_grant_effect
    regional_heritage.set_train_locations_for_civ = noop_button
    regional_heritage.reskin_unit_for_civ = noop_reskin
    heroes_and_villains.enable_unit_for_civ = rec_enable
    regional_heritage.mod(data)
    (util.enable_unit_for_civ, util.upgrade_unit_for_civ, util.grant_effect_to_civ,
     util.set_train_locations_for_civ, util.reskin_unit_for_civ) = orig

    return grants


def build_node_templates(tech_trees_dir: Path) -> dict[int, tuple[dict, str]]:
    """node_id -> (template node dict, array key it lives in). Scans every
    civ's file and keeps the first template found for each node id - the
    node's own fields (name, building, age, picture) are civ-independent.
    Also synthesizes templates for DERIVED_FROM_BASE_TIER node ids, which
    have no real donor anywhere in the source data.
    """
    templates: dict[int, tuple[dict, str]] = {}
    for path in tech_trees_dir.glob('*.json'):
        with path.open(encoding='utf-8') as f:
            tree = json.load(f)
        for array_key in ('civ_techs_units', 'civ_techs_buildings'):
            for node in tree.get(array_key, []):
                node_id = node.get('Node ID')
                if node_id is not None and node_id not in templates:
                    templates[node_id] = (node, array_key)

    for derived_id, base_id in DERIVED_FROM_BASE_TIER.items():
        if derived_id in templates or base_id not in templates:
            continue
        base_node, array_key = templates[base_id]
        derived_node = dict(base_node)
        derived_node['Node ID'] = derived_id
        derived_node['Age ID'] = 4  # Imperial - every grant using this lands on TECH_REQUIREMENT_IMPERIAL_AGE
        if derived_node.get('Building ID') == base_id:
            # Buildings self-reference their own Node ID as Building ID (confirmed
            # via Folwark1/Settlement1's own real templates) - keep that pattern.
            derived_node['Building ID'] = derived_id
        if derived_id in DERIVED_NODE_NAMES:
            derived_node['Name'] = DERIVED_NODE_NAMES[derived_id]
        templates[derived_id] = (derived_node, array_key)
        logging.info(f'Derived a tech-tree template for node {derived_id} from base tier {base_id}')

    return templates


def make_granted_node(template: dict) -> dict:
    node = dict(template)
    node['Node Status'] = 'ResearchedCompleted'
    # Trigger Tech ID references a specific vanilla tech id tied to the
    # donor civ's own unlock tech, which doesn't apply the same way here -
    # drop it rather than point at something that won't make sense for the
    # new civ. Link ID (pointing to a sibling node's Node ID) stays, since
    # unit ids are global and the sibling node gets added too.
    node.pop('Trigger Tech ID', None)
    return node


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dat_filename', type=Path, help='The base .dat file to trace grants against')
    parser.add_argument('civ_tech_trees_dir', type=Path,
                         help='Source CivTechTrees directory to use as node templates')
    parser.add_argument('civilizations_json', type=Path, help='Source civilizations.json')
    parser.add_argument('output_dir', type=Path, help='Where to write the patched CivTechTrees/<CIV>.json files')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    data = DatFile.parse(args.dat_filename)
    civ_filenames = civ_name_to_filename_map(data, args.civilizations_json)
    grants = trace_grants(data)
    templates = build_node_templates(args.civ_tech_trees_dir)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    missing_templates = set()
    patched_civs = 0

    for civ_id, unit_ids in grants.items():
        filename = civ_filenames[civ_id]
        source_path = args.civ_tech_trees_dir / f'{filename}.json'
        with source_path.open(encoding='utf-8') as f:
            tree = json.load(f)
        existing_node_ids = {n.get('Node ID') for n in tree.get('civ_techs_units', [])} | \
            {n.get('Node ID') for n in tree.get('civ_techs_buildings', [])}

        changed = False
        for unit_id in sorted(unit_ids):
            if unit_id in existing_node_ids:
                continue  # already has a tree entry (e.g. it's a real native unique)
            if unit_id not in templates:
                missing_templates.add(unit_id)
                continue
            template, array_key = templates[unit_id]
            tree.setdefault(array_key, []).append(make_granted_node(template))
            changed = True
            logging.info(f'{filename}: added {template["Name"]!r} (node {unit_id}) to {array_key}')

        if changed:
            patched_civs += 1
        out_path = args.output_dir / f'{filename}.json'
        with out_path.open('w', encoding='utf-8') as f:
            json.dump(tree, f, indent=2)

    # Copy through the untouched civs' files too, so the output dir is a
    # complete, valid CivTechTrees directory a mod can ship as an override.
    for path in args.civ_tech_trees_dir.glob('*.json'):
        dest = args.output_dir / path.name
        if not dest.exists():
            shutil.copy(path, dest)

    logging.info(f'Patched {patched_civs} civ tech tree files')
    if missing_templates:
        logging.warning(f'No existing tech-tree template found for node ids: {sorted(missing_templates)}')


if __name__ == '__main__':
    main()
