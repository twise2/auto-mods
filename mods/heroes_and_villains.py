import logging

from genieutils.civ import Civ
from genieutils.unit import Unit
from genieutils.effect import Effect, EffectCommand
from genieutils.tech import Tech, ResearchResourceCost, ResearchLocation
from genieutils.datfile import DatFile
from genieutils.techtree import UnitConnection, Common
from genieutils.unit import ResourceCost, ResourceStorage, TrainLocation
from mods.util import clone, enable_unit_for_civ, reskin_unit_for_civ
from mods.ids import TABINSHWEHTI, TSAR_KONSTANTIN, BELISARIUS, WILLIAM_WALLACE, WHITE_TIGER_YAN, \
    WANG_TONG, ALARIC_THE_GOTH, SUNDJATA, SHAH_ISHMAIL, SALADIN, HARALD_HARDRADA, QUTLUGH, \
    CUAUHTEMOC, ATTILA_THE_HUN, PACAL_II, EL_CID_CAMPEADOR, GENGHIS_KHAN, FRANCESCO_SFORZA, \
    MIKLOS_TOLDI, ALEXANDER_NEVSKI, TARIQ_IBN_ZIYAD, DAGNAJAN, SURYAVARMAN_I, KUSHLUK, \
    GAJAH_MADA, LE_LOI, KOTYAN_KHAN, VYTAUTAS_THE_GREAT, OSMAN, THEMISTOCLES_WARSHIP, \
    LEONIDAS, DARIUS, ARTEMISIA, MILTIADES, \
    JOHN_THE_FEARLESS, ROGER_BOSSO, JAN_ZIZKA, JOGAILA, IBRAHIM_LODI, PRITHVIRAJ, TAMAR, \
    THOROS, JOAN_OF_ARC, NOBUNAGA, ULRICH_VON_JUNGINGEN, PACHACUTI, RAJENDRA_CHOLA, POPE_LEO_I, \
    VASCO_DA_GAMA, ADMIRAL_YI_SHUN_SHIN, MIHIRA_BHOJA, LEIF_ERIKSON, EDWARD_LONGSHANKS, FRANSICO_DE_ORELLANA, \
    ALEXANDER_THE_GREAT, PORUS, THRACIAN_CHIEFTAIN, LAUTARO, PACANCHIQUE, ARARIBOIA, \
    TYPE_POPULATION_HEADROOM, TYPE_CURRENT_POPULATION, TYPE_TOTAL_UNITS_OWNED, TYPE_FOOD_STORAGE, \
    TYPE_GOLD_STORAGE, TYPE_CASTLE_TRAIN_LOCATION, TYPE_DOCK_TRAIN_LOCATION, TYPE_POPULATION_HEADROOM, \
    TECH_REQUIREMENT_IMPERIAL_AGE, TYPE_INFLUENCE_ABILITY, TYPE_TOTAL_UNITS_OWNED,\
    TYPE_SPAWN_UNIT, TOWN_CENTER, TYPE_TOWN_CENTER_BUILT, SPECIAL_UNIT_SPAWN_BASILIEUS_DEAD, CONQUISTADOR_CLASS, \
    WARSHIP_CLASS, CAVLARY_CLASS, INFANTRY_CLASS, ARCHER_CLASS, CAVALRY_ARCHER_CLASS, HAND_CANNONEER_CLASS, \
    HEALER_CLASS, MONK_CLASS, \
    CAO_CAO, LIU_BEI, SUN_JIAN, FORTIFIED_CHURCH, SUNDA_ROYAL_FIGHTER, GIRGEN_KHAN, SUMANGURU #auras

#reserve spaces for hidden resouces. Dont use 501 as its used for sparta already.
LAND_BASILIUS_RESOURCE_VALUE = 201  
WATER_BASILIUS_RESOURCE_VALUE = 202

NAME = 'heroes-and-villains'

CIVS_WITH_HEROES_ALREADY = ['Shu', 'Wu', 'Wei']

# At most one land hero and one water hero per civ - the dict schema below
# enforces this structurally (a civ can only have one "land" key and one
# "water" key), and validate_hero_for_civ() double-checks each unit's real
# class_ actually matches the slot it's declared under. Use None for a slot
# that's genuinely empty rather than omitting the key, so it's obvious at a
# glance which civs are still missing a water (or land) hero.
#
# A slot value is normally just a unit id. When a hero's own real look is
# good enough that another part of the mod wants to reuse it broadly as a
# skin (e.g. Gajah Mada's look reused for South Asian civs' Champions), that
# would leave the hero's owning civ standing next to a bunch of visually
# identical regular troops - use unit_skin_override(unit, skin) instead: the
# hero keeps its real name/stats/id (still Gajah Mada for Malay), it just
# renders using a different, same-class donor's graphics, freeing the
# hero's own original look to be reused elsewhere without a duplicate-look
# clash. Only worth doing for a hero whose look is actually earmarked for
# reuse and isn't itself so central to its own civ's identity that no
# stand-in would do (Le Loi/Vietnamese and Pachacuti/Incas were considered
# and declined for exactly that reason - no good same-class alternate
# existed, and both are genuinely iconic to their own civ specifically).
def unit_skin_override(unit: int, skin: int) -> tuple:
    return (unit, skin)


def _hero_unit_and_skin(value):
    if isinstance(value, tuple):
        return value
    return value, None


HERO_FOR_CIV = {
    "British": {"land": EDWARD_LONGSHANKS, "water": None},
    "Byzantine": {"land": BELISARIUS, "water": None},
    "Celts": {"land": WILLIAM_WALLACE, "water": None},
    "Chinese": {"land": WANG_TONG, "water": None},
    "French": {"land": JOAN_OF_ARC, "water": None},
    "Goths": {"land": ALARIC_THE_GOTH, "water": None},
    "Japanese": {"land": NOBUNAGA, "water": None},
    # Genghis Khan keeps the name/stats, but renders as Girgen Khan instead
    # of his own real look - Girgen Khan's model reads as more "hero-y."
    # Frees Genghis Khan's own iconic look from ever being used as a
    # regional skin, since seeing THE Genghis Khan standing next to a pile
    # of visually-identical mass-trained troops elsewhere would be jarring
    # in a way a more obscure look wouldn't be (same reasoning as Malay's
    # Gajah Mada -> Sunda Royal Fighter override above).
    "Mongols": {"land": unit_skin_override(GENGHIS_KHAN, GIRGEN_KHAN), "water": None},
    "Persians": {"land": SHAH_ISHMAIL, "water": None},
    "Saracens": {"land": SALADIN, "water": None},
    "Teutons": {"land": ULRICH_VON_JUNGINGEN, "water": None},
    "Turks": {"land": OSMAN, "water": None},
    "Vikings": {"land": HARALD_HARDRADA, "water": LEIF_ERIKSON},
    "Aztecs": {"land": CUAUHTEMOC, "water": None},
    "Huns": {"land": ATTILA_THE_HUN, "water": None},
    "Koreans": {"land": None, "water": ADMIRAL_YI_SHUN_SHIN},  # no land unit found yet, could add one later w/ lang file setup
    "Mayan": {"land": PACAL_II, "water": None},
    "Spanish": {"land": EL_CID_CAMPEADOR, "water": None},
    "Incas": {"land": PACHACUTI, "water": None},
    "Italians": {"land": FRANCESCO_SFORZA, "water": None},
    "Magyars": {"land": MIKLOS_TOLDI, "water": None},
    "Slavs": {"land": ALEXANDER_NEVSKI, "water": None},
    "Berbers": {"land": TARIQ_IBN_ZIYAD, "water": None},
    "Ethiopians": {"land": DAGNAJAN, "water": None},
    # Sundjata keeps the name/stats, but renders as Sumanguru - his real
    # historical rival, the sorcerer-king of Sosso, confirmed via the wiki
    # to have gotten his own genuinely unique DE model too (same African
    # Kingdoms art pass as Gidajan/Yodit/Sosso Guard). Frees Sundjata's own
    # look for reuse as a Paladin skin (regional_heritage.py).
    "Malians": {"land": unit_skin_override(SUNDJATA, SUMANGURU), "water": None},
    "Portuguese": {"land": FRANSICO_DE_ORELLANA, "water": VASCO_DA_GAMA},  # Orellana served the Spanish crown, but kept as a stand-in rather than leaving Portuguese with just one hero
    "Burmese": {"land": TABINSHWEHTI, "water": None},
    "Khmer": {"land": SURYAVARMAN_I, "water": None},
    # Gajah Mada's own real look is reused broadly as a Champion skin for
    # South Asian civs (regional_heritage.py) - Malay's own hero keeps the
    # name/stats but renders as Sunda Royal Fighter instead (a genuinely
    # distinct, unique model from the same Rise of the Rajas Indonesian
    # campaign, confirmed via the wiki), so Malay doesn't end up standing
    # next to a bunch of visually-identical regular Champions.
    "Malay": {"land": unit_skin_override(GAJAH_MADA, SUNDA_ROYAL_FIGHTER), "water": None},
    "Vietnamese": {"land": LE_LOI, "water": None},
    "Bulgarians": {"land": TSAR_KONSTANTIN, "water": None},
    "Cumans": {"land": KOTYAN_KHAN, "water": None},
    "Lithuanians": {"land": VYTAUTAS_THE_GREAT, "water": None},
    "Tatars": {"land": QUTLUGH, "water": None},
    "Burgundians": {"land": JOHN_THE_FEARLESS, "water": None},
    "Sicilians": {"land": ROGER_BOSSO, "water": None},
    "Bohemians": {"land": JAN_ZIZKA, "water": None},
    "Poles": {"land": JOGAILA, "water": None},
    "Hindustanis": {"land": IBRAHIM_LODI, "water": None},
    "Bengalis": {"land": PRITHVIRAJ, "water": None},
    "Gurjaras": {"land": MIHIRA_BHOJA, "water": None},  # Mihira Bhoja ruled the Gurjara-Pratihara dynasty - namesake fit
    "Dravidians": {"land": RAJENDRA_CHOLA, "water": None},
    "Romans": {"land": POPE_LEO_I, "water": None},  # could be improved if custom unit is added, or lang script updated
    "Armenians": {"land": THOROS, "water": None},
    "Georgians": {"land": TAMAR, "water": None},
    "Spartans": {"land": LEONIDAS, "water": None},
    "Achaemenids": {"land": DARIUS, "water": ARTEMISIA},  # Artemisia commanded ships for Xerxes, Darius's son, at Salamis
    "Athenians": {"land": MILTIADES, "water": THEMISTOCLES_WARSHIP},  # Miltiades was the actual victor of Marathon; Themistocles built the navy that won at Salamis
    "Khitans": {"land": KUSHLUK, "water": None},  # fine but not amazing
    "Jurchens": {"land": WHITE_TIGER_YAN, "water": None},  # not great but they dont have great #Aguda if they add him would be a perfect campaign
    "Macedonians": {"land": ALEXANDER_THE_GREAT, "water": None},
    "Thracians": {"land": THRACIAN_CHIEFTAIN, "water": None},
    "Puru": {"land": PORUS, "water": None},
    "Mapuche": {"land": LAUTARO, "water": None},
    "Muisca": {"land": PACANCHIQUE, "water": None},
    "Tupi": {"land": ARARIBOIA, "water": None},
    # Shu/Wu/Wei already have real native land heroes (Cao Cao/Liu Bei/Sun
    # Jian - see CIVS_WITH_HEROES_ALREADY, which skips them entirely below).
    # If a good water-only hero is ever found for one of them, add just the
    # "water" half here rather than uncommenting "land" too.
    #"Shu": {"land": None, "water": LIU_BEI},
    #"Wu": {"land": None, "water": SUN_JIAN},
    #"Wei": {"land": None, "water": CAO_CAO},
}


def validate_hero_for_civ(data: DatFile):
    base = data.civs[0]
    for civ_name, slots in HERO_FOR_CIV.items():
        for slot, value in slots.items():
            if value is None:
                continue
            unit_id, skin_override = _hero_unit_and_skin(value)
            is_water = base.units[unit_id].class_ == WARSHIP_CLASS
            if slot == 'water' and not is_water:
                raise ValueError(f'{civ_name}: unit {unit_id} is under "water" but is not WARSHIP_CLASS')
            if slot == 'land' and is_water:
                raise ValueError(f'{civ_name}: unit {unit_id} is under "land" but is WARSHIP_CLASS')
            if skin_override is not None and base.units[skin_override].class_ != base.units[unit_id].class_:
                raise ValueError(f'{civ_name}: skin_override {skin_override} does not match '
                                  f'unit {unit_id}\'s class_')

class auraClass:
      def __init__(self, data: DatFile):
        def getAuraFromUnit(unit_id: int, data: DatFile):
            auraTasks = [x for x in data.civs[0].units[unit_id].bird.tasks if x.action_type == 155]
            return auraTasks
        #rip from the units with avilities so we kinda can balance.
        self.workRate = getAuraFromUnit(FORTIFIED_CHURCH, data)
        self.healing = getAuraFromUnit(LIU_BEI, data)
        self.attackSpeed = getAuraFromUnit(CAO_CAO, data)
        self.movementSpeed = getAuraFromUnit(SUN_JIAN, data)


def addUnitToAllCivs(unit: Unit, data: DatFile):
    #add the unit to all civs
    for civ in data.civs:
         civ.units.append(clone(unit, data.version))

def enableUnitForCiv(civ_id: int, unit_id: int, data: DatFile):
    enable_unit_for_civ(data, civ_id, unit_id, TECH_REQUIREMENT_IMPERIAL_AGE)


def limitHeroesForCiv(data: DatFile, hidden_resource_id: int) -> int:
    logging.info(f'Settting up hero limit for civs')
    #copy dead basilius to give one of hiden resource at start of game.
    dead_basilius = clone(data.civs[0].units[SPECIAL_UNIT_SPAWN_BASILIEUS_DEAD], data.version)
    dead_basilius_id = len(data.civs[0].units)
    dead_basilius.id = dead_basilius_id
    dead_basilius.resource_storages = (
        ResourceStorage(type=12, amount=300.0, flag=0), 
        ResourceStorage(type=hidden_resource_id, amount=1.0, flag=1), 
        ResourceStorage(type=-1, amount=0.0, flag=0)  
    )
    #remove basilius graphic so the dead unit assignment isnt funky.
    dead_basilius.standing_graphic = (-1,-1)
    dead_basilius.dying_graphic = -1
    #add basilius to the civs unit list so it can be used in the effect.
    addUnitToAllCivs(dead_basilius, data)

    for civ_id, civ in enumerate(data.civs):
        if(civ.name in HERO_FOR_CIV):
            #create a dead basilieus at start to give one of needed resource for the unit. This one gives instant resource 501 when it dies instead of delayed
            give_resource_at_first_tc_effect_command = EffectCommand(type=TYPE_SPAWN_UNIT, a=dead_basilius_id, b=TOWN_CENTER, c=1, d=0.0)
            limit_unit_creatable_effect = Effect(
                name=f'Limit Hero for {data.civs[civ_id].name} resource {hidden_resource_id}',
                effect_commands=[give_resource_at_first_tc_effect_command]
            )
            limit_unit_creatable_effect_id = len(data.effects)
            data.effects.append(limit_unit_creatable_effect)
            #add the tech with the effect to the civ to give 1 hero value.
            logging.info(f'Making tech for hero unit limit for {data.civs[civ_id].name} - resource - {hidden_resource_id}')
            limit_hero_unit_creatable_effect = Tech(
                required_techs=(TYPE_TOWN_CENTER_BUILT, -1, -1, -1, -1, -1),
                resource_costs=(
                    ResearchResourceCost(type=-1, amount=0, flag=0),
                    ResearchResourceCost(type=-1, amount=0, flag=0),
                    ResearchResourceCost(type=-1, amount=0, flag=0)
                ),
                required_tech_count=1,
                civ=civ_id,
                full_tech_mode=0,
                language_dll_name=0,
                language_dll_description=0,
                effect_id=limit_unit_creatable_effect_id,
                type=0,
                icon_id=-1,
                language_dll_help=0,
                language_dll_tech_tree=0,
                research_locations=[ResearchLocation(location_id=-1, research_time=0, button_id=0, hot_key_id=-1)],
                name=f'Limit hero for {data.civs[civ_id].name} resource {hidden_resource_id}',
                repeatable=0,
            )
            data.techs.append(limit_hero_unit_creatable_effect)
    return dead_basilius_id

def extendTasks(unit: Unit, tasks) -> Unit:
    #extend the tasks of the unit with the new tasks
    for task in tasks:
        #get correct ids
        task.id = len(unit.bird.tasks) #set the id to be the next available id
        unit.bird.tasks.append(task)
    return unit


def fixHeroCreationText(unit: Unit) -> Unit:
    """Point the "training tooltip" text at the hero's own, already-valid
    name string instead of leaving it wrong or inventing a new one.

    Real, confirmed bug: this used to copy language_dll_creation/help/
    hotkey_text from whichever of Cao Cao/Liu Bei/Sun Jian donated the
    hero's aura ability - purely a code-reuse shortcut for stealing their
    aura task data, but it also dragged along their own real, defined
    "Create Cao Cao"/"Create Liu Bei"/"Create Sun Jian" text onto every
    hero of that aura class, regardless of who the hero actually is
    (confirmed directly in key-value-strings-utf8.txt).

    A custom key-value-modded-strings-utf8.txt override was considered,
    but this is a data-only mod meant for multiplayer - that file isn't
    part of the .dat, so there's no guarantee every client in a lobby has
    it, unlike every field on the Unit object itself, which is baked into
    the .dat and therefore identical for everyone. So instead of inventing
    new text, reuse text that's already guaranteed correct and present:
    the hero's own language_dll_name (e.g. "Belisarius") is real, defined,
    already shown as the unit's title, and ships with the base game on
    every client. Confirmed the hero's own original language_dll_help/
    hotkey_text ids resolve to nothing in the string table either way
    (same as the donor's), so there's no equivalent "already correct"
    value to redirect those to - leaving them as the hero's own (unused)
    values is no worse than before, and no longer borrows from an
    unrelated unit.
    """
    unit.language_dll_creation = unit.language_dll_name
    return unit

def giveAuraAndLangauge(unit: Unit, data: DatFile) -> Unit:
    auras = auraClass(data)

    #set unit to use aura abilities
    unit.type_50.break_off_combat = TYPE_INFLUENCE_ABILITY

    if(unit.class_ in [CAVLARY_CLASS, WARSHIP_CLASS]):
        logging.info("giving move speed aura to unit")
        extendTasks(unit, auras.movementSpeed)
    elif(unit.class_ in [CAVALRY_ARCHER_CLASS, CONQUISTADOR_CLASS]):
        logging.info("giving attack speed aura to unit")
        extendTasks(unit, auras.attackSpeed)
    elif(unit.class_ in [INFANTRY_CLASS, ARCHER_CLASS, HAND_CANNONEER_CLASS]):
        logging.info("giving move and attack speed aura to unit")
        extendTasks(unit, auras.attackSpeed)
        extendTasks(unit, auras.movementSpeed)
    elif(unit.class_ in [MONK_CLASS, HEALER_CLASS]):
        logging.info("giving healing aura to unit")
        extendTasks(unit, auras.healing)
    else:
        logging.error(f"Unit {unit.name} not given an aura")
    fixHeroCreationText(unit)
            
def makeHero(unitId: int, civ: Civ, data: DatFile, land_basilius_unit_id: int, water_basilius_unit_id: int) -> int:
    logging.info(f'Patching hero unit {unitId}')
    new_unit_id = len(civ.units)
    #clone the unit
    unit = clone(civ.units[unitId], data.version)
    #set id to be end of civ units
    unit.id = new_unit_id
    unit.creatable.hero_mode = 1

    #make sure unit take up population space
    unit.resource_storages = (
        ResourceStorage(type=TYPE_POPULATION_HEADROOM, amount=-1, flag=2),
        ResourceStorage(type=TYPE_CURRENT_POPULATION, amount=1, flag=2),
        ResourceStorage(type=TYPE_TOTAL_UNITS_OWNED, amount=1, flag=1),
    )

    #make unit trainable in the dock if waship and limit is with water basilius
    if(unit.class_ == WARSHIP_CLASS):
        logging.info(f'chose dock for hero unit {unit.name} for civ {civ.name}')
        #button 24 at the Dock is already the game's own "hero ship" slot (Leif
        #Erikson, Vasco da Gama, Yi Sun-sin, etc all use it) - nothing else does.
        unit.creatable.train_locations = [TrainLocation(train_time=30, unit_id=TYPE_DOCK_TRAIN_LOCATION, button_id=24, hot_key_id=-1)]
        #this gives back a resource when the unit dies that the unit costs to spawn. This limits us to one.
        unit.dead_unit_id = water_basilius_unit_id
        #make unit cost resources 
        unit.creatable.resource_costs = (
            #lock it into a water cost
            ResourceCost(type=WATER_BASILIUS_RESOURCE_VALUE, amount=1, flag=1),
            ResourceCost(type=TYPE_FOOD_STORAGE, amount=500, flag=1),
            ResourceCost(type=TYPE_GOLD_STORAGE, amount=500, flag=1),
        )
    #make unit trainable in the castle if other unit type and limit is with land basilius
    else:
        logging.info(f'chose castle for hero unit {unit.name} for civ {civ.name}')
        #button 2 at the Castle (Shu/Wu/Wei's own native hero slot) turned out NOT
        #to be safe for every other civ: confirmed via the .dat that tech 256
        #("Trebuchet", civ=-1 - the real, commonly-researched player tech) also
        #enables Packed Trebuchet (id 331) at that exact button for every civ that
        #researches it, so a hero placed there silently lost that collision in real
        #games (in-game testing showed no hero ever appeared anywhere). Button 4 is
        #genuinely unclaimed instead - confirmed via the .dat that its only two
        #occupants (MKIPCHAK, CRUSADERKNIGHT) are dead scenario-only units with no
        #tech anywhere that ever enables them for a real civ.
        unit.creatable.train_locations = [TrainLocation(train_time=60, unit_id=TYPE_CASTLE_TRAIN_LOCATION, button_id=4, hot_key_id=-1)]
        #this gives back a resource when the unit dies that the unit costs to spawn. This limits us to one.
        unit.dead_unit_id = land_basilius_unit_id
        #make unit cost resources 
        unit.creatable.resource_costs = (
            #lock it into a water cost
            ResourceCost(type=LAND_BASILIUS_RESOURCE_VALUE, amount=1, flag=1),
            ResourceCost(type=TYPE_FOOD_STORAGE, amount=500, flag=1),
            ResourceCost(type=TYPE_GOLD_STORAGE, amount=500, flag=1),
        ) 

    #add the new unit to the civ
    #give the unit an aura based on its class
    giveAuraAndLangauge(unit, data)
    addUnitToAllCivs(unit, data)
    logging.info(f'Patched hero unit {unit.name} for civ {civ.name}')
    return new_unit_id

def mod(data: DatFile):
    validate_hero_for_civ(data)
    civs_missing_hero = []
    water_basilius_unit_id = limitHeroesForCiv(data, WATER_BASILIUS_RESOURCE_VALUE)
    land_basilius_unit_id = limitHeroesForCiv(data, LAND_BASILIUS_RESOURCE_VALUE)
    for civ_id, civ in enumerate(data.civs):
        if civ.name in HERO_FOR_CIV:
            for slot, value in HERO_FOR_CIV[civ.name].items():
                if value is None:
                    continue
                unit_id, skin_override = _hero_unit_and_skin(value)
                logging.info(f'Creating {slot} hero for civ {civ.name} - hero: {unit_id}')
                hero_unit_id = makeHero(unit_id, civ, data, land_basilius_unit_id, water_basilius_unit_id)
                if skin_override is not None:
                    reskin_unit_for_civ(data, civ_id, hero_unit_id, skin_override)
                logging.info(f'Enabling unit for civ {civ.name} - hero: {unit_id}')
                enableUnitForCiv(civ_id, hero_unit_id, data)

        else:
            if(civ.name not in CIVS_WITH_HEROES_ALREADY):
                # If the civ is not in the list, log an error message
                civs_missing_hero.append(civ.name)

    for civ in civs_missing_hero:
        logging.error(f'No hero for civ {civ}')
