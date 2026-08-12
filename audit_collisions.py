#! /usr/bin/env python3
"""Ground-truth button-collision audit for every regional_heritage.py/
heroes_and_villains.py grant, replacing the futuravailableunits.json-based
check in disable_unit_lines.py.find_button_collisions.

Why this exists: that JSON file is confirmed NOT load-bearing for real
in-game training (Chinese still trained Knight instead of the granted
Hei-Kuang Cavalry despite disable_unit_line_for_civ "removing" Knight from
the JSON), and separately confirmed unreliable even as a collision-
detection SOURCE - it missed the real Packed Trebuchet vs hero collision
at Castle button 2 entirely, because Packed Trebuchet was never listed
under any civ's Castle building in that file even though a real, commonly-
researched civ=-1 tech (256, "Trebuchet") enables it there for every civ.

Ground truth instead: scan every tech's real effect commands directly.
A civ=-1 tech's TYPE_ENABLE_DISABLE_UNIT(b=1) command enables that unit at
its train_location for EVERY civ once the tech's prereqs are met - which
is how Packed Trebuchet actually gets discovered. A civ=X tech's command
only affects that one civ. This is exactly the manual check that found
the real hero/Packed-Trebuchet collision and confirmed Castle button 4 /
Dock button 24 were genuinely free - now applied systematically to every
grant this mod makes.
"""
import logging
from collections import defaultdict

from genieutils.datfile import DatFile

from disable_unit_lines import trace_granted_units, unit_locations, build_upgrade_families, BUILD_MENU_ID


def build_slot_enablers(data: DatFile) -> dict[tuple[int, int], dict[int, set[int]]]:
    """(building_id, button_id) -> {civ_id: {unit_id, ...}} for every unit
    any real tech ever enables there. civ_id -1 means "every civ" (a
    civ=-1 tech) - callers should treat that as applying universally in
    addition to whatever a specific civ_id maps to.
    """
    base = data.civs[0]

    def location(unit_id: int):
        u = base.units[unit_id] if unit_id < len(base.units) else None
        if u is None or not u.creatable or not u.creatable.train_locations:
            return None
        tl = u.creatable.train_locations[0]
        return (tl.unit_id, tl.button_id) if tl.unit_id != -1 else None

    slots: dict[tuple[int, int], dict[int, set[int]]] = defaultdict(lambda: defaultdict(set))
    for t in data.techs:
        if t is None or t.effect_id < 0:
            continue
        for cmd in data.effects[t.effect_id].effect_commands:
            if cmd.type != 2 or cmd.b != 1:
                continue
            loc = location(cmd.a)
            if loc is None:
                continue
            slots[loc][t.civ].add(cmd.a)
    return slots


def real_competitors(data: DatFile, slots: dict[tuple[int, int], dict[int, set[int]]],
                      civ_id: int, building_id: int, button_id: int,
                      exclude: set[int], families: dict[int, set[int]]) -> set[int]:
    """Every unit_id genuinely enabled (universally or for this specific
    civ) at (building_id, button_id), other than the units in `exclude`
    (the grant itself) or in their upgrade family."""
    if building_id == BUILD_MENU_ID:
        return set()
    by_civ = slots.get((building_id, button_id), {})
    candidates = set(by_civ.get(-1, set())) | set(by_civ.get(civ_id, set()))
    result = set()
    for unit_id in candidates:
        if unit_id in exclude:
            continue
        same_family = families.get(unit_id, {unit_id})
        if same_family & exclude:
            continue
        result.add(unit_id)
    return result


def audit(data: DatFile) -> None:
    civ_names = {i: c.name for i, c in enumerate(data.civs)}
    base = data.civs[0]
    slots = build_slot_enablers(data)
    families = build_upgrade_families(data)
    newly_enabled, upgraded, _disabled, overrides = trace_granted_units(data)

    combined: dict[int, set[int]] = defaultdict(set)
    for civ_id, ids in newly_enabled.items():
        combined[civ_id] |= ids
    for civ_id, ids in upgraded.items():
        combined[civ_id] |= ids

    total_checked = 0
    total_bad = 0
    for civ_id, unit_ids in sorted(combined.items()):
        for unit_id in sorted(unit_ids):
            for building_id, button_id in unit_locations(data, civ_id, unit_id, overrides):
                total_checked += 1
                competitors = real_competitors(data, slots, civ_id, building_id, button_id,
                                                unit_ids | {unit_id}, families)
                if competitors:
                    total_bad += 1
                    names = ', '.join(sorted(base.units[c].name for c in competitors if c < len(base.units)))
                    granted_name = base.units[unit_id].name if unit_id < len(base.units) else unit_id
                    print(f'COLLISION: {civ_names.get(civ_id)}: granted {granted_name} at building='
                          f'{building_id} button={button_id} really competes with [{names}]')
    print(f'\nChecked {total_checked} (civ, unit, location) grants, {total_bad} real collisions found.')


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dat_filename')
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)
    data = DatFile.parse(args.dat_filename)
    audit(data)


if __name__ == '__main__':
    main()
