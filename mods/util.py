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
    TYPE_ENABLE_DISABLE_UNIT, TYPE_DISABLE_REGIONAL_TECH, RESOURCE_STARTING_SCOUT_UNIT, \
    TECH_REQUIREMENT_IMPERIAL_AGE

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


def set_starting_scout_for_civ(data: DatFile, civ_id: int, unit_id: int):
    """Change which unit this civ's player starts scouting with (e.g.
    Camel Scout instead of the default Scout Cavalry). Not a tech/effect -
    a plain per-civ static value: Civ.resources[RESOURCE_STARTING_SCOUT_UNIT]
    holds the starting scout's unit id, read once at game start rather
    than triggered by any research. Confirmed via direct .dat comparison
    against Gurjaras' own real bonus (resources[263]=1755, Camel Scout) vs.
    a normal civ's resources[263]=448 (Scout Cavalry).
    """
    civ = data.civs[civ_id]
    logging.info(f'Starting {civ.name} scouting with unit {unit_id} ({civ.units[unit_id].name})')
    civ.resources[RESOURCE_STARTING_SCOUT_UNIT] = float(unit_id)


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
    that civ's normal researchable tech tree. Returns the new tech's own id (not
    the effect's) - callers that need to reference this specific grant as a
    prerequisite for something else (see research_elite_upgrade_for_civ) need the
    tech id, not the effect id.
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
    tech_id = len(data.techs)
    data.techs.append(unlock_tech)
    return tech_id


def enable_unit_for_civ(data: DatFile, civ_id: int, unit_id: int, required_tech: int) -> int:
    """Make an existing (but disabled) unit trainable for one civ. Returns the
    new tech's id, so a following research_elite_upgrade_for_civ call can
    require it explicitly - without that, an elite-tier tech gated only on
    (say) Imperial Age could complete before this enable does, since the two
    triggers are otherwise independent (confirmed real bug: Huns could reach
    Imperial Age without ever building a Castle, completing the elite upgrade
    while the base tier had never actually been enabled).
    """
    civ = data.civs[civ_id]
    unit_name = civ.units[unit_id].name
    logging.info(f'Enabling {unit_name} for {civ.name}')
    enable_command = EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=unit_id, b=1, c=-1, d=0.0)
    return grant_effect_to_civ(data, civ_id, [enable_command], required_tech, f'Enable {unit_name} for {civ.name}')


def upgrade_unit_for_civ(data: DatFile, civ_id: int, base_unit_id: int, upgraded_unit_id: int, required_tech: int):
    """Give one civ the free upgrade from `base_unit_id` to `upgraded_unit_id`
    once `required_tech` is satisfied. Only correct for things that are
    genuinely free/automatic in real vanilla too - building age-tiers
    (confirmed: Settlement's and Folwark's own real age-upgrade techs both
    have zero cost and no research location) and same-line unit growth
    (confirmed: Camel Scout's own real upgrade into Camel Rider is also free).
    A unit's real Elite tier is NOT free in vanilla - use
    research_elite_upgrade_for_civ for that instead.
    """
    civ = data.civs[civ_id]
    base_name = civ.units[base_unit_id].name
    logging.info(f'Upgrading {base_name} to {civ.units[upgraded_unit_id].name} for {civ.name}')
    upgrade_command = EffectCommand(type=TYPE_UPGRADE_UNIT, a=base_unit_id, b=upgraded_unit_id, c=-1, d=0.0)
    grant_effect_to_civ(data, civ_id, [upgrade_command], required_tech, f'Upgrade {base_name} for {civ.name}')


def research_elite_upgrade_for_civ(data: DatFile, civ_id: int, upgrade_pairs: list[tuple[int, int]],
                                    extra_required_techs: list[int], building_id: int, button_id: int,
                                    resource_costs: list[tuple[int, int]], research_time: int, name: str,
                                    donor_tech_id: int, age_tech: int = TECH_REQUIREMENT_IMPERIAL_AGE):
    """Give one civ a REAL, player-researched Elite-tier upgrade - a visible,
    costed button at a real building, matching vanilla's own convention for
    every actual Elite-tier tech checked this session (Elite Steppe Lancer:
    600 food/550 gold at the Stable; Elite War Chariot: 600 food/500 wood;
    Legionary: 800 food/400 gold; etc - see NOTES-civ-identity-expansion.md
    for the full list). This is NOT the same as upgrade_unit_for_civ, which
    is a free, instant, hidden background tech - correct for adding a new
    base-tier unit or a building's age-tier (vanilla's own "X (make avail)"
    techs work exactly that way), but wrong for an Elite tier, which real
    civs always pay for and actively research.

    `upgrade_pairs` is a list of (base_unit_id, upgraded_unit_id), not just
    one - several real grants (Winged Hussar, Legionary, Harbor) upgrade
    more than one source unit/building tier into the same target, and the
    real vanilla techs for those bundle every command into ONE researchable
    tech rather than offering several duplicate research buttons (confirmed:
    Malay's own real Harbor tech has 4 separate upgrade commands in a single
    tech). A single-pair grant just passes a 1-item list.

    required_techs is always TECH_REQUIREMENT_IMPERIAL_AGE plus whatever's
    in `extra_required_techs` (1-4 more tech ids, matching how many real
    vanilla Elite techs are gated - most need just one more, e.g. the tech
    id enable_unit_for_civ returned for the base unit, but Legionary's real
    tech also requires "Long Swordsman" researched and Winged Hussar's
    requires "Light Cavalry" researched, neither of which is an enable-tech
    case). This also fixes the real bug that motivated this function:
    without an explicit dependency on whatever makes the base tier real,
    the two triggers are otherwise independent, so a civ could complete the
    Elite tier via Imperial Age alone while the base tier had never actually
    been enabled (confirmed happening for civs that reached Imperial Age
    without ever building a Castle).

    `donor_tech_id` is the id of the real vanilla tech this grant is modeled
    on (e.g. 715 for Elite Steppe Lancer) - its language_dll_name/
    description/help/tech_tree and icon_id are copied directly onto the new
    tech, so the research button shows real, correct text and a real icon
    instead of blank ones. Confirmed as a real bug (user report: "no
    wording or icon"): every tech this function built left these at the
    same 0/0/-1 placeholder grant_effect_to_civ uses for hidden background
    techs - fine there since those are never actually shown in the UI, but
    wrong here since this is a real, visible, clickable research button. A
    custom string-file override was considered and rejected for the same
    reason as the hero tooltip fix - this is a data-only mod for
    multiplayer, and a loose key-value string file isn't guaranteed to be
    on every client the way a `.dat` field is. Reusing the real vanilla
    tech's own already-correct, already-shipped text and icon needs no new
    strings and is guaranteed present everywhere.
    """
    donor = data.techs[donor_tech_id]
    civ = data.civs[civ_id]
    for base_unit_id, upgraded_unit_id in upgrade_pairs:
        logging.info(f'Researching {civ.units[upgraded_unit_id].name} '
                      f'(from {civ.units[base_unit_id].name}) for {civ.name}')
    upgrade_commands = [EffectCommand(type=TYPE_UPGRADE_UNIT, a=base_unit_id, b=upgraded_unit_id, c=-1, d=0.0)
                         for base_unit_id, upgraded_unit_id in upgrade_pairs]
    effect = Effect(name=name, effect_commands=upgrade_commands)
    effect_id = len(data.effects)
    data.effects.append(effect)

    costs = [ResearchResourceCost(type=t, amount=a, flag=1) for t, a in resource_costs]
    while len(costs) < 3:
        costs.append(ResearchResourceCost(type=-1, amount=0, flag=0))

    required = [age_tech] + list(extra_required_techs)
    while len(required) < 6:
        required.append(-1)

    unlock_tech = Tech(
        required_techs=tuple(required[:6]),
        resource_costs=tuple(costs[:3]),
        required_tech_count=1 + len(extra_required_techs),
        civ=civ_id,
        full_tech_mode=0,
        language_dll_name=donor.language_dll_name,
        language_dll_description=donor.language_dll_description,
        effect_id=effect_id,
        type=0,
        icon_id=donor.icon_id,
        language_dll_help=donor.language_dll_help,
        language_dll_tech_tree=donor.language_dll_tech_tree,
        research_locations=[ResearchLocation(location_id=building_id, research_time=research_time,
                                              button_id=button_id, hot_key_id=-1)],
        name=name,
        repeatable=0,
    )
    data.techs.append(unlock_tech)


def reskin_unit_for_civ(data: DatFile, civ_id: int, unit_id: int, donor_unit_id: int):
    """Give one civ's copy of a unit a different appearance, borrowed from
    `donor_unit_id`, without changing its name, stats, or upgrade path.

    Purely cosmetic - the donor unit itself is untouched and can still be used
    (or reused as a donor) elsewhere. genieutils-py can't rewrite language-file
    strings, so the unit's displayed name can't change this way, only how it
    looks - matches how the old regionalAdditions branch did civ skins.

    Real, confirmed bug fixed here: this used to only copy standing/dying/
    undead/damage/attack graphics, never `dead_fish.walking_graphic` or
    `running_graphic` - so every reskin this project has ever made (going
    back to the original Frankish Paladin/Crusader Knight skins) looked
    right standing still, attacking, or dying, but reverted to the
    *original* unit's own walk animation the moment it moved (user report:
    "the skins dont seem to be working for any units when they are
    moving"). Confirmed directly in the .dat: Champion's real
    walking_graphic (2906) and Norse Warrior's (7630) are completely
    different values, and the old version of this function never touched
    that field at all. Also now copies `type_50.attack_graphic_2` and
    `creatable`'s idle_attack/special/garrison graphics while at it, since
    those are exactly the same class of "extra animation state" field and
    at least one (special_graphic) was already confirmed to sometimes
    carry a real, different value between donor and target.
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
    unit.type_50.attack_graphic_2 = donor.type_50.attack_graphic_2
    if unit.dead_fish is not None and donor.dead_fish is not None:
        unit.dead_fish.walking_graphic = donor.dead_fish.walking_graphic
        unit.dead_fish.running_graphic = donor.dead_fish.running_graphic
    if unit.creatable is not None and donor.creatable is not None:
        unit.creatable.idle_attack_graphic = donor.creatable.idle_attack_graphic
        unit.creatable.special_graphic = donor.creatable.special_graphic
        unit.creatable.garrison_graphic = donor.creatable.garrison_graphic


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
