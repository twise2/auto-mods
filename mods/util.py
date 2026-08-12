import logging
from typing import TypeVar

from genieutils.civ import Civ
from genieutils.common import GenieClass, ByteHandler
from genieutils.datfile import DatFile
from genieutils.effect import Effect, EffectCommand
from genieutils.tech import Tech, ResearchResourceCost, ResearchLocation
from genieutils.unit import Unit, TrainLocation
from genieutils.versions import Version

from mods.ids import CLASS_PETARD, MONUMENT, CLASS_HERO, TYPE_UPGRADE_UNIT, TYPE_COMBATANT, \
    TYPE_ENABLE_DISABLE_UNIT, TYPE_DISABLE_REGIONAL_TECH

GC = TypeVar('GC', bound=GenieClass)

def clone(item: GC, version: str) -> GC:
    packed = item.to_bytes(Version(version))
    byte_handler = ByteHandler(memoryview(packed))
    byte_handler.version = Version(version)
    return item.__class__.from_bytes(byte_handler)

def disable_unit(data: DatFile, unit_id: int):
    logging.info(f'Disabling unit with id {unit_id} ({data.civs[0].units[unit_id].name}) for all civs')
    for civ in data.civs:
        civ.units[unit_id].enabled = 0


def disable_unit_for_civ(data: DatFile, civ_id: int, unit_id: int):
    civ = data.civs[civ_id]
    logging.info(f'Disabling {civ.units[unit_id].name} for {civ.name}')
    civ.units[unit_id].enabled = 0


def disable_unit_line_for_civ(data: DatFile, civ_id: int, unit_ids: set[int], required_tech: int):
    """Remove a civ's native access to a unit line (e.g. Knight/Cavalier/
    Paladin) for historical-identity reasons - Turks/Huns keeping their
    fully-upgraded Steppe Lancer instead of also having Western knights,
    etc. A REAL .dat mutation: researches a self-triggering tech (same
    grant_effect_to_civ mechanism enable_unit_for_civ uses) whose effect
    commands are TYPE_ENABLE_DISABLE_UNIT with b=0 for each unit - matches
    vanilla's own proven pattern exactly (Mule Cart's real tech, id 932/940
    for Georgians/Armenians, disables Lumber Camp/Mining Camp this same
    way). Confirmed via real in-game testing this session that the earlier
    version of this function - a no-op that only patched
    futuravailableunits.json - did NOT work: Chinese kept training Knight
    instead of the granted Hei-Kuang Cavalry, because Knight was never
    actually disabled in the .dat and the game doesn't consult that JSON
    file for real training access (see NOTES-civ-identity-expansion.md).
    """
    civ = data.civs[civ_id]
    names = ', '.join(civ.units[uid].name for uid in sorted(unit_ids))
    logging.info(f'Disabling unit line [{names}] for {civ.name}')
    disable_commands = [EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=uid, b=0, c=-1, d=0.0)
                         for uid in sorted(unit_ids)]
    grant_effect_to_civ(data, civ_id, disable_commands, required_tech, f'Disable [{names}] for {civ.name}')


def disable_tech_for_civ(data: DatFile, civ_id: int, tech_ids: set[int], required_tech: int):
    """Remove a civ's real access to an upgrade *tech* (as opposed to the
    unit it produces) - e.g. hiding the Cavalier/Paladin research buttons
    for a civ whose Knight/Cavalier/Paladin units are already disabled via
    disable_unit_line_for_civ, so the now-pointless upgrade research
    doesn't still show up. Uses TYPE_DISABLE_REGIONAL_TECH, DE's own real
    "[FTT]" (Future Tech Tree) mechanism - confirmed via direct .dat
    inspection that Persians has exactly this: tech 527, "[FTT] Disable
    Paladin", civ=8, disables the generic Paladin tech (265) for them
    specifically since Savar replaces it (Persians keep the real, working
    Cavalier tech though - Savar only replaces the final tier, unlike a
    full-line removal like Chinese/Hei-Kuang Cavalry).
    """
    civ = data.civs[civ_id]
    names = ', '.join(data.techs[tid].name for tid in sorted(tech_ids))
    logging.info(f'Disabling tech(s) [{names}] for {civ.name}')
    disable_commands = [EffectCommand(type=TYPE_DISABLE_REGIONAL_TECH, a=-1, b=-1, c=-1, d=float(tid))
                         for tid in sorted(tech_ids)]
    grant_effect_to_civ(data, civ_id, disable_commands, required_tech, f'Disable tech [{names}] for {civ.name}')


def disable_tech_effect(data: DatFile, tech_id: int):
    logging.info(f'Disabling the effect of tech with id {tech_id} ({data.techs[tech_id].name})')
    data.techs[tech_id].effect_id = -1


def disable_tech_research_location(data: DatFile, tech_id: int):
    logging.info(f'Disabling the research location of tech with id {tech_id} ({data.techs[tech_id].name})')
    for research_location in data.techs[tech_id].research_locations:
        research_location.location_id = -1

def patch_unit_for_explosion(unit_it: int, attack_indexes: list[int], range_: int, civ: Civ):
    unit = civ.units[unit_it]
    unit.class_ = CLASS_PETARD
    for index in attack_indexes:
        unit.type_50.attacks[index].amount = 5000
    unit.type_50.max_range = range_
    unit.type_50.blast_width = range_
    unit.type_50.blast_attack_level = 0
    unit.wwise_train_sound_id = 0
    logging.info(f'Patched unit {unit.id} ({unit.name}) for civ {civ.name}')


def patch_monument_to_keep_it_from_exploding(civ: Civ):
    monument = civ.units[MONUMENT]
    monument.hit_points = 30000
    monument.type_50.base_armor = 10000


def is_trebuchet(unit: Unit) -> bool:
    return unit.class_ in (51, 54)


def prevent_hp_increase(unit: Unit):
    unit.type_50.armours = []
    if not is_trebuchet(unit):  # Trebuchets don't die right if they have another class
        unit.class_ = CLASS_HERO


def is_unit_upgrade(effect_command: EffectCommand) -> bool:
    return effect_command.type == TYPE_UPGRADE_UNIT and effect_command.c == -1


def is_unit(data: DatFile, unit_id: int) -> bool:
    return data.civs[0].units[unit_id] and data.civs[0].units[unit_id].type == TYPE_COMBATANT


def grant_effect_to_civ(data: DatFile, civ_id: int, effect_commands: list, required_tech: int, name: str) -> int:
    """Give one civ a self-triggering tech that fires `effect_commands` as soon as
    `required_tech` is satisfied (e.g. Castle built, Imperial Age reached).

    This is how the game itself grants hero units, so it's a proven way to hand a
    civ something (a unit, an upgrade) without needing it to already be wired into
    that civ's normal researchable tech tree.
    """
    effect = Effect(name=name, effect_commands=effect_commands)
    effect_id = len(data.effects)
    data.effects.append(effect)

    unlock_tech = Tech(
        required_techs=(required_tech, -1, -1, -1, -1, -1),
        resource_costs=(
            ResearchResourceCost(type=-1, amount=0, flag=0),
            ResearchResourceCost(type=-1, amount=0, flag=0),
            ResearchResourceCost(type=-1, amount=0, flag=0),
        ),
        required_tech_count=1,
        civ=civ_id,
        full_tech_mode=0,
        language_dll_name=0,
        language_dll_description=0,
        effect_id=effect_id,
        type=0,
        icon_id=-1,
        language_dll_help=0,
        language_dll_tech_tree=0,
        research_locations=[ResearchLocation(location_id=-1, research_time=0, button_id=0, hot_key_id=-1)],
        name=name,
        repeatable=0,
    )
    data.techs.append(unlock_tech)
    return effect_id


def enable_unit_for_civ(data: DatFile, civ_id: int, unit_id: int, required_tech: int):
    """Make an existing (but disabled) unit trainable for one civ."""
    civ = data.civs[civ_id]
    unit_name = civ.units[unit_id].name
    logging.info(f'Enabling {unit_name} for {civ.name}')
    enable_command = EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=unit_id, b=1, c=-1, d=0.0)
    grant_effect_to_civ(data, civ_id, [enable_command], required_tech, f'Enable {unit_name} for {civ.name}')


def upgrade_unit_for_civ(data: DatFile, civ_id: int, base_unit_id: int, upgraded_unit_id: int, required_tech: int):
    """Give one civ the free upgrade from `base_unit_id` to `upgraded_unit_id`
    (e.g. a unit's Elite tier) once `required_tech` is satisfied."""
    civ = data.civs[civ_id]
    base_name = civ.units[base_unit_id].name
    logging.info(f'Upgrading {base_name} to {civ.units[upgraded_unit_id].name} for {civ.name}')
    upgrade_command = EffectCommand(type=TYPE_UPGRADE_UNIT, a=base_unit_id, b=upgraded_unit_id, c=-1, d=0.0)
    grant_effect_to_civ(data, civ_id, [upgrade_command], required_tech, f'Upgrade {base_name} for {civ.name}')


def reskin_unit_for_civ(data: DatFile, civ_id: int, unit_id: int, donor_unit_id: int):
    """Give one civ's copy of a unit a different appearance, borrowed from
    `donor_unit_id`, without changing its name, stats, or upgrade path.

    Purely cosmetic - the donor unit itself is untouched and can still be used
    (or reused as a donor) elsewhere. genieutils-py can't rewrite language-file
    strings, so the unit's displayed name can't change this way, only how it
    looks - matches how the old regionalAdditions branch did civ skins.
    """
    civ = data.civs[civ_id]
    unit = civ.units[unit_id]
    donor = civ.units[donor_unit_id]
    logging.info(f'Reskinning {unit.name} to look like {donor.name} for {civ.name}')
    unit.standing_graphic = donor.standing_graphic
    unit.dying_graphic = donor.dying_graphic
    unit.undead_graphic = donor.undead_graphic
    unit.damage_graphics = donor.damage_graphics
    unit.type_50.attack_graphic = donor.type_50.attack_graphic


def set_train_locations_for_civ(data: DatFile, civ_id: int, unit_id: int, locations: list[tuple[int, int]]):
    """Move where one civ's copy of a unit trains from, without affecting any
    other civ's copy of the same unit. Takes one or more (building_id,
    button_id) pairs, since some units (e.g. Temple Guard, trainable from
    both Barracks and Monastery) train from more than one building.

    Needed when a granted unit's vanilla training button collides with
    something the target civ already has at that same building (its own
    native unique unit, or another grant) - each civ owns its own unit
    objects, so this only touches the one civ's copy. disable_unit_lines.py
    traces calls to this (see its trace_granted_units) so
    futuravailableunits.json reflects the overridden location(s) rather than
    the unit's generic default.
    """
    unit = data.civs[civ_id].units[unit_id]
    train_time = unit.creatable.train_locations[0].train_time
    logging.info(f'Moving {unit.name} to {locations} for {data.civs[civ_id].name}')
    unit.creatable.train_locations = [
        TrainLocation(train_time=train_time, unit_id=building_id, button_id=button_id, hot_key_id=-1)
        for building_id, button_id in locations
    ]


def affects_units(data: DatFile, effect_command: EffectCommand) -> bool:
    return is_unit(data, effect_command.a) and is_unit(data, effect_command.b)
