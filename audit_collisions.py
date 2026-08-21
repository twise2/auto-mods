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
    any real tech ever makes available there. civ_id -1 means "every civ"
    (a civ=-1 tech) - callers should treat that as applying universally in
    addition to whatever a specific civ_id maps to.

    Checks *every* train_location a unit has, not just the first - missing
    this hid a real collision all session (Huns' native "Elite Tarkan"
    upgrades unit 886 -> 887, and 887's second train_location is the exact
    same Stable button 4 this mod's Steppe Lancer grant uses; 886/887 never
    showed up in any check that only looked at index 0). Also checks
    TYPE_UPGRADE_UNIT (type=3) targets, not just TYPE_ENABLE_DISABLE_UNIT
    (type=2) - a unit that only ever appears as an upgrade *target* (like
    887 above) is real and trainable once the upgrade fires, even though no
    tech ever directly "enables" it.
    """
    base = data.civs[0]

    def locations(unit_id: int):
        u = base.units[unit_id] if unit_id < len(base.units) else None
        if u is None or not u.creatable or not u.creatable.train_locations:
            return []
        return [(tl.unit_id, tl.button_id) for tl in u.creatable.train_locations if tl.unit_id != -1]

    slots: dict[tuple[int, int], dict[int, set[int]]] = defaultdict(lambda: defaultdict(set))
    for t in data.techs:
        if t is None or t.effect_id < 0:
            continue
        for cmd in data.effects[t.effect_id].effect_commands:
            if cmd.type == 2 and cmd.b == 1:
                target = cmd.a
            elif cmd.type == 3:
                target = cmd.b
            else:
                continue
            for loc in locations(target):
                slots[loc][t.civ].add(target)
    return slots


def real_competitors(data: DatFile, slots: dict[tuple[int, int], dict[int, set[int]]],
                      civ_id: int, building_id: int, button_id: int,
                      exclude: set[int], families: dict[int, set[int]]) -> tuple[set[int], set[int]]:
    """(civ_specific, universal) competitors at (building_id, button_id),
    other than the units in `exclude` (the grant itself) or in their
    upgrade family. Split rather than merged because the two have very
    different confidence: a civ-specific tech unambiguously means that
    exact civ really has that unit, while a civ=-1 tech only means it's
    *reachable* somewhere in the full tech tree - confirmed unreliable as
    "this civ really has it" on its own (Steppe Lancer's own "make avail"
    tech is civ=-1 and gated only on Feudal Age, identical in shape to
    Knight's, yet Steppe Lancer is genuinely Cuman/Mongol-exclusive - the
    real per-civ restriction for civ=-1 content isn't visible in the tech
    system at all, see REGIONAL-HERITAGE-PLAYBOOK.md section 3.7).
    """
    if building_id == BUILD_MENU_ID:
        return set(), set()
    by_civ = slots.get((building_id, button_id), {})

    def filtered(candidates):
        result = set()
        for unit_id in candidates:
            if unit_id in exclude:
                continue
            same_family = families.get(unit_id, {unit_id})
            if same_family & exclude:
                continue
            result.add(unit_id)
        return result

    return filtered(by_civ.get(civ_id, set())), filtered(by_civ.get(-1, set()))


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
    confirmed = []
    possible = []
    for civ_id, unit_ids in sorted(combined.items()):
        for unit_id in sorted(unit_ids):
            for building_id, button_id in unit_locations(data, civ_id, unit_id, overrides):
                total_checked += 1
                civ_specific, universal = real_competitors(data, slots, civ_id, building_id, button_id,
                                                             unit_ids | {unit_id}, families)
                granted_name = base.units[unit_id].name if unit_id < len(base.units) else unit_id
                if civ_specific:
                    names = ', '.join(sorted(base.units[c].name for c in civ_specific if c < len(base.units)))
                    confirmed.append(f'{civ_names.get(civ_id)}: granted {granted_name} at building='
                                      f'{building_id} button={button_id} really competes with [{names}] '
                                      f'(civ-specific - confirmed real)')
                if universal:
                    names = ', '.join(sorted(base.units[c].name for c in universal if c < len(base.units)))
                    possible.append(f'{civ_names.get(civ_id)}: granted {granted_name} at building='
                                     f'{building_id} button={button_id} might compete with [{names}] '
                                     f'(civ=-1 sourced - unconfirmed, see section 3.7)')

    print('=== CONFIRMED (civ-specific tech - real, act on these) ===')
    for line in confirmed:
        print(line)
    print('\n=== POSSIBLE (civ=-1 sourced - worth a second look, not proven) ===')
    for line in possible:
        print(line)
    print(f'\nChecked {total_checked} (civ, unit, location) grants: '
          f'{len(confirmed)} confirmed, {len(possible)} possible.')


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
