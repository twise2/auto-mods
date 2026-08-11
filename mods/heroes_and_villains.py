import logging

from genieutils.civ import Civ
from genieutils.unit import Unit
from genieutils.effect import Effect, EffectCommand
from genieutils.tech import Tech, ResearchResourceCost, ResearchLocation
from genieutils.datfile import DatFile
from genieutils.techtree import UnitConnection, Common
from genieutils.unit import ResourceCost, ResourceStorage, TrainLocation
from mods.util import clone, enable_unit_for_civ
from mods.ids import TABINSHWEHTI, TSAR_KONSTANTIN, BELISARIUS, WILLIAM_WALLACE, WHITE_TIGER_YAN, \
    WANG_TONG, ALARIC_THE_GOTH, SUNDJATA, SHAH_ISHMAIL, SALADIN, HARALD_HARDRADA, QUTLUGH, \
    CUAUHTEMOC, ATTILA_THE_HUN, PACAL_II, EL_CID_CAMPEADOR, GENGHIS_KHAN, FRANCESCO_SFORZA, \
    MIKLOS_TOLDI, ALEXANDER_NEVSKI, TARIQ_IBN_ZIYAD, DAGNAJAN, SURYAVARMAN_I, KUSHLUK, \
    GAJAH_MADA, LE_LOI, KOTYAN_KHAN, VYTAUTAS_THE_GREAT, OSMAN, THEMISTOCLES, THEMISTOCLES_WARSHIP, \
    LEONIDAS, DARIUS, ARTEMISIA, DATIS, MILTIADES, BRASIDAS, PARMENION, HEPHAISTION, \
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
    CAO_CAO, LIU_BEI, SUN_JIAN, FORTIFIED_CHURCH #auras

#reserve spaces for hidden resouces. Dont use 501 as its used for sparta already.
LAND_BASILIUS_RESOURCE_VALUE = 201  
WATER_BASILIUS_RESOURCE_VALUE = 202

NAME = 'heroes-and-villains'

CIVS_WITH_HEROES_ALREADY = ['Shu', 'Wu', 'Wei']

HERO_FOR_CIV = {
    "British": [EDWARD_LONGSHANKS],
    "Byzantine": [BELISARIUS],
    "Celts": [WILLIAM_WALLACE],
    "Chinese": [WANG_TONG],
    "French": [JOAN_OF_ARC],
    "Goths": [ALARIC_THE_GOTH],
    "Japanese": [NOBUNAGA],
    "Mongols": [GENGHIS_KHAN],
    "Persians": [SHAH_ISHMAIL],
    "Saracens": [SALADIN],
    "Teutons": [ULRICH_VON_JUNGINGEN],
    "Turks": [OSMAN],
    "Vikings": [HARALD_HARDRADA, LEIF_ERIKSON],
    "Aztecs": [CUAUHTEMOC],
    "Huns": [ATTILA_THE_HUN],
    "Koreans": [ADMIRAL_YI_SHUN_SHIN], #no lnad unit, could add one later i lang file setup.
    "Mayan": [PACAL_II],
    "Spanish": [EL_CID_CAMPEADOR],
    "Incas": [PACHACUTI],
    "Italians": [FRANCESCO_SFORZA],
    "Magyars": [MIKLOS_TOLDI],
    "Slavs": [ALEXANDER_NEVSKI],
    "Berbers": [TARIQ_IBN_ZIYAD],
    "Ethiopians": [DAGNAJAN],
    "Malians": [SUNDJATA],
    "Portuguese": [FRANSICO_DE_ORELLANA, VASCO_DA_GAMA],  # Orellana served the Spanish crown, but kept as a stand-in rather than leaving Portuguese with just one hero
    "Burmese": [TABINSHWEHTI],
    "Khmer": [SURYAVARMAN_I],
    "Malay": [GAJAH_MADA],
    "Vietnamese": [LE_LOI],
    "Bulgarians": [TSAR_KONSTANTIN],
    "Cumans": [KOTYAN_KHAN],
    "Lithuanians": [VYTAUTAS_THE_GREAT],
    "Tatars": [QUTLUGH],
    "Burgundians": [JOHN_THE_FEARLESS],
    "Sicilians": [ROGER_BOSSO],
    "Bohemians": [JAN_ZIZKA],
    "Poles": [JOGAILA],
    "Hindustanis": [IBRAHIM_LODI],
    "Bengalis": [PRITHVIRAJ],
    "Gurjaras": [MIHIRA_BHOJA],  # Mihira Bhoja ruled the Gurjara-Pratihara dynasty - namesake fit
    "Dravidians": [RAJENDRA_CHOLA],
    "Romans": [POPE_LEO_I], #could be improved if custom unit is added. or lang script updated.
    "Armenians": [THOROS],
    "Georgians": [TAMAR],
    "Spartans": [LEONIDAS, BRASIDAS],
    "Achaemenids": [DARIUS, ARTEMISIA, DATIS],  # Artemisia commanded ships for Xerxes, Darius's son, at Salamis; Datis co-commanded at Marathon with Artaphernes
    "Athenians": [THEMISTOCLES, THEMISTOCLES_WARSHIP, MILTIADES],  # architect of the navy that won at Salamis; Miltiades was the actual victor of Marathon
    "Khitans": [KUSHLUK], #fine but not amazing
    "Jurchens": [WHITE_TIGER_YAN], #not great but they dont have great #Aguda if they add him would be a perfect campaign.
    "Macedonians": [ALEXANDER_THE_GREAT, PARMENION, HEPHAISTION],
    "Thracians": [THRACIAN_CHIEFTAIN],
    "Puru": [PORUS],
    "Mapuche": [LAUTARO],
    "Muisca": [PACANCHIQUE],
    "Tupi": [ARARIBOIA],
    #"Shu": [LIU_BEI],
    #"Wu": [SUN_JIAN],
    #"Wei": [CAO_CAO],  
}

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


def giveLanguage(unit: Unit, unitGiver: Unit) -> Unit:
    #unit.language_dll_name = unitGiver.language_dll_creation
    unit.language_dll_creation = unitGiver.language_dll_creation
    unit.language_dll_help = unitGiver.language_dll_help
    unit.language_dll_hotkey_text = unitGiver.language_dll_hotkey_text

def giveAuraAndLangauge(unit: Unit, data: DatFile) -> Unit:
    auras = auraClass(data)

    #TODO see if you can change the names somehow?
    #this is not currently possible because genieUtils.py does not support language files.
    #can see about adding langfile support from genieUtils to genieutils.py
    #https://github.com/Tapsa/genieutils/blob/master/src/lang/LangFile.cpp
    attackSpeedLanguageUnit = data.civs[0].units[CAO_CAO]
    healingLanguageUnit = data.civs[0].units[LIU_BEI]
    movementSpeedLanguageUnit = data.civs[0].units[SUN_JIAN]

    #set unit to use aura abilities
    unit.type_50.break_off_combat = TYPE_INFLUENCE_ABILITY

    if(unit.class_ in [CAVLARY_CLASS, WARSHIP_CLASS]):
        logging.info("giving move speed aura to unit")
        extendTasks(unit, auras.movementSpeed)
        giveLanguage(unit, movementSpeedLanguageUnit)
    elif(unit.class_ in [CAVALRY_ARCHER_CLASS, CONQUISTADOR_CLASS]):
        logging.info("giving attack speed aura to unit")
        extendTasks(unit, auras.attackSpeed)
        giveLanguage(unit, attackSpeedLanguageUnit)
    elif(unit.class_ in [INFANTRY_CLASS, ARCHER_CLASS, HAND_CANNONEER_CLASS]):
        logging.info("giving move and attack speed aura to unit")
        extendTasks(unit, auras.attackSpeed)
        extendTasks(unit, auras.movementSpeed)
        giveLanguage(unit, attackSpeedLanguageUnit)
    elif(unit.class_ in [MONK_CLASS, HEALER_CLASS]):
        logging.info("giving healing aura to unit")
        extendTasks(unit, auras.healing)
        giveLanguage(unit, healingLanguageUnit)
    else:
        logging.error(f"Unit {unit.name} not given an aura")
            
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
        #button 2 at the Castle is already the game's own "hero" slot - this mod's
        #whole hero model is built on how Shu/Wu/Wei's own native heroes (Cao Cao,
        #Liu Bei, Sun Jian) already work in real multiplayer, so match their exact
        #train_time/hot_key, not just the button.
        unit.creatable.train_locations = [TrainLocation(train_time=60, unit_id=TYPE_CASTLE_TRAIN_LOCATION, button_id=2, hot_key_id=16381)]
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
    civs_missing_hero = []
    water_basilius_unit_id = limitHeroesForCiv(data, WATER_BASILIUS_RESOURCE_VALUE)
    land_basilius_unit_id = limitHeroesForCiv(data, LAND_BASILIUS_RESOURCE_VALUE)
    for civ_id, civ in enumerate(data.civs):
        if civ.name in HERO_FOR_CIV:
            for unit_id in HERO_FOR_CIV[civ.name]:
                logging.info(f'Creating hero for civ {civ.name} - hero: {unit_id}')
                hero_unit_id = makeHero(unit_id, civ, data, land_basilius_unit_id, water_basilius_unit_id)
                logging.info(f'Enabling unit for civ {civ.name} - hero: {unit_id}')
                enableUnitForCiv(civ_id, hero_unit_id, data)
    
        else:
            if(civ.name not in CIVS_WITH_HEROES_ALREADY):
                # If the civ is not in the list, log an error message
                civs_missing_hero.append(civ.name)
    
    for civ in civs_missing_hero:
        logging.error(f'No hero for civ {civ}')
