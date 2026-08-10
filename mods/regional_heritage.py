import logging

from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand

from mods.util import enable_unit_for_civ, upgrade_unit_for_civ, grant_effect_to_civ, reskin_unit_for_civ
from mods.ids import TECH_CASTLE_BUILT, TECH_REQUIREMENT_IMPERIAL_AGE, TYPE_TOWN_CENTER_BUILT, \
    TYPE_ENABLE_DISABLE_UNIT, \
    STEPPE_LANCER, ELITE_STEPPE_LANCER, ELEPHANT_ARCHER, ELITE_ELEPHANT_ARCHER, ARMORED_ELEPHANT, \
    SIEGE_ELEPHANT, GENITOUR, ELITE_GENITOUR, CAMEL_RIDER, HEAVY_CAMEL_RIDER, IMPERIAL_CAMEL_RIDER, \
    CAMEL_SCOUT, CARAVANSERAI, MULE_CART, LEGIONARY, MILITIA, MAN_AT_ARMS, LONG_SWORDSMAN, WARRIOR_PRIEST, \
    MISSIONARY, SCOUT_CAVALRY, \
    LIGHT_CAVALRY, HUSSAR, WINGED_HUSSAR, SKIRMISHER, ELITE_SKIRMISHER, IMPERIAL_SKIRMISHER, \
    SETTLEMENT, SETTLEMENT_AGE_3, FIRE_LANCER, ELITE_FIRE_LANCER, MILL, LUMBER_CAMP, MINING_CAMP, \
    PALADIN, FRANKISH_PALADIN_SKIN, CRUSADER_KNIGHT_SKIN, \
    FEITORIA, DONJON, KREPOST, HARBOR, FOLWARK1, FOLWARK3, MILL_AGE2, MILL_AGE3, MILL_AGE4, \
    DOCK_AGE2, DOCK_AGE3, DOCK_AGE4, TYPE_DOCK_TRAIN_LOCATION, \
    CHURCH, CHURCH_AGE2, CHURCH_AGE3, CHURCH_AGE4, FORTIFIED_CHURCH, \
    THIRISADAI, CONDOTTIERO, SLINGER

# The idea behind this mod, in the spirit of the earlier `regionalAdditions` branch:
# give civs units/buildings they plausibly would have fielded historically, focused on
# regional identity rather than balance. Every grant below cites the community
# discussion it's drawn from. New units become trainable once a civ has built a
# Castle (or, for early economic helpers, a Town Center) - no manual research click
# needed, the same mechanism the game itself uses to unlock hero units.
#
# Boundary rule (see NOTES-civ-identity-expansion.md for the full writeup): a civ's
# own true unique unit trained from the Castle - the one thing that's exclusively
# theirs, win or lose - is never handed to another civ by this file. That's a step
# too far into diluting what makes a civ its own civ. A unit that's real and
# unique but trains from somewhere other than the Castle (a Dock, a Barracks) is
# a different story - it was never sitting in the "core identity" slot to begin
# with, so sharing it doesn't touch that. What *is* fair game: regional units
# already shared by design (Steppe Lancer, Elephant Archer, Genitour, Fire Lancer
# - all `civ=-1` "make available" pairs vanilla itself treats as regional, not
# exclusive), unique economic/defensive buildings, starting-unit swaps (Camel
# Scout), line upgrades/replacements that reskin or re-route an existing unit
# line rather than adding a brand new one (Legionary replacing Long Swordsman for
# Byzantines, the same way Savar already reskins Paladin for Persians natively),
# purely cosmetic reskins, and true uniques that don't train from the Castle.

NAME = 'regional-heritage'


def civ_ids_named(data: DatFile, names: list[str]) -> list[int]:
    return [civ_id for civ_id, civ in enumerate(data.civs) if civ.name in names]


def give_steppe_lancers_to_civs_with_horse_archer_heritage(data: DatFile):
    # Steppe Lancers are currently a Cuman/Mongol-family exclusive, but plenty of
    # other horse-archer and steppe-adjacent civs would plausibly have fielded them.
    # https://www.reddit.com/r/aoe2/comments/y6b17r/disproportionate_spread_of_regional_units/
    civs = ['Chinese', 'Bulgarians', 'Lithuanians', 'Hindustanis', 'Magyars', 'Slavs', 'Persians', 'Huns', 'Turks']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, STEPPE_LANCER, TECH_CASTLE_BUILT)
        upgrade_unit_for_civ(data, civ_id, STEPPE_LANCER, ELITE_STEPPE_LANCER, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_elephant_archers_to_civs_with_elephant_heritage(data: DatFile):
    # Elephant Archers are currently Bengali/Dravidian/Gurjaran only, despite several
    # other civs having a strong historical elephant-warfare tradition.
    # https://www.reddit.com/r/aoe2/comments/10mqm64/sotl_should_more_civs_get_elephant_archers/
    civs = ['Persians', 'Burmese', 'Malay', 'Khmer', 'Vietnamese']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, ELEPHANT_ARCHER, TECH_CASTLE_BUILT)
        upgrade_unit_for_civ(data, civ_id, ELEPHANT_ARCHER, ELITE_ELEPHANT_ARCHER, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_armored_elephants_to_other_elephant_civs(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/ubkjoa/armored_elephants_for_khmer_burmese_and_malay
    civs = ['Khmer', 'Burmese', 'Malay', 'Ethiopians', 'Vietnamese']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, ARMORED_ELEPHANT, TECH_CASTLE_BUILT)
        upgrade_unit_for_civ(data, civ_id, ARMORED_ELEPHANT, SIEGE_ELEPHANT, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_genitours_to_civs_with_light_cavalry_heritage(data: DatFile):
    # Genitours (Iberian/North African light skirmish cavalry) are currently
    # Berber-only despite the broader Mediterranean/Islamic world using them -
    # Italy and Sicily both had deep, centuries-long Muslim-Mediterranean contact
    # (Norman-Arab-Byzantine Sicily especially) that fits the same light-cavalry
    # tradition.
    # https://www.reddit.com/r/aoe2/comments/106i52l/genitours_for_middle_eastern_civs/
    civs = ['Spanish', 'Portuguese', 'Persians', 'Saracens', 'Malians', 'Turks', 'Italians', 'Sicilians']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, GENITOUR, TECH_CASTLE_BUILT)
        upgrade_unit_for_civ(data, civ_id, GENITOUR, ELITE_GENITOUR, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_camel_line_to_steppe_civs_without_camels(data: DatFile):
    # Cumans genuinely lack Paladin in the current game, so this is a real
    # gap-filling alternative late-game answer for them, not just flavor. Huns
    # already have full Paladin access (one of only two "fully upgraded" Paladin
    # civs), so for them this is historical flavor only - steppe peoples had
    # plausible camel contact, but it isn't fixing a mechanical gap the way it is
    # for Cumans.
    # https://forums.ageofempires.com/t/give-cumans-heavy-camel-riders-and-remove-paladins-and-maybe-chevaliers/196455
    for civ_id in civ_ids_named(data, ['Cumans', 'Huns']):
        enable_unit_for_civ(data, civ_id, CAMEL_RIDER, TECH_CASTLE_BUILT)
        upgrade_unit_for_civ(data, civ_id, CAMEL_RIDER, HEAVY_CAMEL_RIDER, TECH_REQUIREMENT_IMPERIAL_AGE)
        # Complete the line to the same finishing tier Berbers/Saracens/Turks get
        # below, rather than stopping one tier short of a full late-game answer.
        upgrade_unit_for_civ(data, civ_id, HEAVY_CAMEL_RIDER, IMPERIAL_CAMEL_RIDER, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_imperial_camel_riders_to_other_camel_civs(data: DatFile):
    # https://forums.ageofempires.com/t/imperial-camels-for-saracens-turks-and-berbers/245239
    civs = ['Berbers', 'Saracens', 'Turks']
    for civ_id in civ_ids_named(data, civs):
        upgrade_unit_for_civ(data, civ_id, CAMEL_RIDER, IMPERIAL_CAMEL_RIDER, TECH_REQUIREMENT_IMPERIAL_AGE)
        upgrade_unit_for_civ(data, civ_id, HEAVY_CAMEL_RIDER, IMPERIAL_CAMEL_RIDER, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_caravanserai_to_silk_road_civs(data: DatFile):
    # Caravanserai are currently Hindustani/Persian only; the wider Silk Road trade
    # network ran straight through these civs too.
    # https://www.reddit.com/r/aoe2/comments/10a3jg9/historically_persian_should_also_have_access_to/
    civs = ['Saracens', 'Chinese', 'Mongols', 'Turks', 'Tatars']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, CARAVANSERAI, TECH_CASTLE_BUILT)


def give_mule_carts_to_nomadic_civs(data: DatFile):
    # Mule carts (a mobile drop-off point) are currently Georgian/Armenian only, but
    # the mechanic fits any historically nomadic/steppe civ just as well.
    # https://www.reddit.com/r/aoe2/comments/17stxfy/should_all_nomad_civs_be_given_mule_carts/
    #
    # Vanilla's own Mule Cart tech doesn't just enable it - it also disables the
    # Lumber Camp and Mining Camp, since Mule Cart replaces that build-menu slot
    # for Georgians/Armenians rather than sitting alongside it. Matching that
    # exactly rather than bolting Mule Cart on as a pure addition. All three
    # commands are bundled into one tech so the swap happens atomically - the
    # civ never has a moment with neither the camps nor Mule Cart available.
    civs = ['Mongols', 'Huns', 'Tatars', 'Cumans', 'Magyars']
    for civ_id in civ_ids_named(data, civs):
        commands = [
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=MULE_CART, b=1, c=-1, d=0.0),
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=LUMBER_CAMP, b=0, c=-1, d=0.0),
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=MINING_CAMP, b=0, c=-1, d=0.0),
        ]
        grant_effect_to_civ(data, civ_id, commands, TYPE_TOWN_CENTER_BUILT,
                             f'Swap Lumber/Mining Camp for Mule Cart for {data.civs[civ_id].name}')


def give_legionaries_to_byzantines(data: DatFile):
    # The Byzantine Empire was the direct continuation of Rome and kept fielding
    # legions long after the west fell; Legionary is currently Roman-only. This is
    # a line replacement, not a new unit - Byzantines' Militia/Man-at-Arms/Long
    # Swordsman line becomes Legionary the same way Persians' Paladin becomes Savar,
    # not a second, separate unique unit sitting alongside their existing one.
    # https://www.reddit.com/r/aoe2/comments/13tw143/so_i_read_some_comments_about_how_byzantine_civ/
    for civ_id in civ_ids_named(data, ['Byzantine']):
        for base_unit in (MILITIA, MAN_AT_ARMS, LONG_SWORDSMAN):
            upgrade_unit_for_civ(data, civ_id, base_unit, LEGIONARY, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_winged_hussars_to_other_eastern_european_civs(data: DatFile):
    # Winged Hussars are currently Polish/Lithuanian only, but Hungary and the Cuman
    # cavalry tradition both fed directly into the same eastern-European hussar style.
    # https://www.reddit.com/r/aoe2/comments/qu6b4a/should_magyars_get_winged_hussars_too/
    for civ_id in civ_ids_named(data, ['Magyars', 'Cumans']):
        for base_unit in (SCOUT_CAVALRY, LIGHT_CAVALRY, HUSSAR):
            upgrade_unit_for_civ(data, civ_id, base_unit, WINGED_HUSSAR, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_imperial_skirmisher_to_civs_with_great_skirmishers(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/17h70lv/imperial_skirmisher_would_be_nice_if_it_wasnt/
    # Byzantines (cheaper Skirmisher+Pikeman), Lithuanians (faster-training
    # Skirmisher+Pikeman), and Dravidians (faster Skirmisher/Elephant Archer
    # attack) all have a real, dedicated civ bonus built around Skirmishers
    # specifically - the same "this civ's whole identity already points here"
    # signal Malians/Romans were picked on originally.
    civs = ['Malians', 'Romans', 'Byzantine', 'Lithuanians', 'Dravidians']
    for civ_id in civ_ids_named(data, civs):
        upgrade_unit_for_civ(data, civ_id, SKIRMISHER, IMPERIAL_SKIRMISHER, TECH_REQUIREMENT_IMPERIAL_AGE)
        upgrade_unit_for_civ(data, civ_id, ELITE_SKIRMISHER, IMPERIAL_SKIRMISHER, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_slingers_to_other_american_civs(data: DatFile):
    # Slinger is a `civ=-1` "make available" unit just like Steppe Lancer/
    # Elephant Archer/Genitour - currently native to Incas, Mapuche, Muisca,
    # and Tupi (confirmed via the real CivTechTrees), the four Andean/Amazonian
    # civs. Aztecs and Mayans are the same pre-Columbian American world (already
    # tied to Incas via Settlement/Warrior Priest in this mod) and share the
    # same documented Mesoamerican sling-warfare tradition.
    civs = ['Aztecs', 'Mayan']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, SLINGER, TECH_CASTLE_BUILT)


def give_missionaries_to_civs_with_missionary_heritage(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/ka4jvi/why_dont_portuguese_have_access_to_missionaries/
    # Teutons (a crusading Catholic military order) and Romans (birthplace of the
    # Catholic Church itself) fit at least as well as the original three. French
    # inherit the same Frankish-Crusader-kingdoms Catholic tradition. British
    # (eventual global colonial-missionary reach) and Burgundians (devout
    # Catholic patrons of the Crusades) round out the Catholic-Europe theme.
    civs = ['Italians', 'Portuguese', 'Byzantine', 'Teutons', 'Romans', 'French', 'British', 'Burgundians']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, MISSIONARY, TECH_CASTLE_BUILT)


def give_warrior_priests_to_civs_with_shamanic_heritage(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/17egkrm/for_fun_what_if_the_new_warrior_priest_from/
    # Mayans and Incas share the same Mesoamerican/Andean shamanic-religious
    # tradition Aztecs already have this from; Goths fit the same Germanic
    # pagan-warband religion already represented by Vikings/Celts here. Koreans
    # fit the same "shamanic tradition alongside an organized religion" pattern
    # Japanese/Chinese already represent, via Korean mudang shamanism.
    civs = ['Vikings', 'Celts', 'Aztecs', 'Dravidians', 'Malians', 'Teutons', 'Japanese', 'Chinese',
            'Mayan', 'Incas', 'Goths', 'Koreans']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, WARRIOR_PRIEST, TECH_CASTLE_BUILT)


def give_settlements_to_mesoamerican_and_andean_civs(data: DatFile):
    # The Settlement (a scaling frontier outpost) is the signature building of the
    # newest South American civs (Muisca, Mapuche, Tupi). Aztecs, Mayans, and Incas
    # are the same Mesoamerican/Andean world but predate the mechanic entirely -
    # they'd plausibly have it too if designed today. Their civ-specific bonus techs
    # (cheaper/healing, garrison, combat bonuses) stay exclusive to the three newer
    # civs; this just gives the base building and its age upgrades.
    # Settlement occupies the same build-menu slot as the Mill (Poland's Folwark,
    # the other Mill-replacement building in the game, uses the same slot for the
    # same reason) - it's a replacement, not an addition, same as Mule Cart above.
    # Bundled into one tech so Mill disappears at the exact moment Settlement
    # becomes available, not before.
    civs = ['Aztecs', 'Mayan', 'Incas']
    for civ_id in civ_ids_named(data, civs):
        commands = [
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=SETTLEMENT, b=1, c=-1, d=0.0),
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=MILL, b=0, c=-1, d=0.0),
        ]
        grant_effect_to_civ(data, civ_id, commands, TECH_CASTLE_BUILT,
                             f'Swap Mill for Settlement for {data.civs[civ_id].name}')
        # Skip the intermediate Age 2 tier - jump straight to the final tier once
        # Imperial is reached, same simplification used for every other elite/upgrade
        # grant in this file.
        upgrade_unit_for_civ(data, civ_id, SETTLEMENT, SETTLEMENT_AGE_3, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_fire_lancers_to_japanese(data: DatFile):
    # Fire Lancers (East Asian gunpowder cavalry) are currently Chinese/Jurchen/
    # Khitan/Korean/Vietnamese only. Japan had plausible gunpowder-technology
    # contact with China/Korea and hasn't been given any gunpowder-flavored unit
    # by this mod yet.
    for civ_id in civ_ids_named(data, ['Japanese']):
        enable_unit_for_civ(data, civ_id, FIRE_LANCER, TECH_CASTLE_BUILT)
        upgrade_unit_for_civ(data, civ_id, FIRE_LANCER, ELITE_FIRE_LANCER, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_camel_scout_start_to_true_camel_civs(data: DatFile):
    # Gurjaras start scouting with a Camel Scout instead of a normal Scout
    # Cavalry, which then grows into the same Camel Rider line. Civs whose whole
    # identity is already built around camels in this mod (Cumans/Huns via the
    # camel line above, Berbers/Saracens/Turks via the Imperial Camel Rider grant
    # below) would plausibly scout the same way from the very start, not just
    # field camels once a Castle goes up.
    civs = ['Cumans', 'Huns', 'Berbers', 'Saracens', 'Turks']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, CAMEL_SCOUT, TYPE_TOWN_CENTER_BUILT)
        upgrade_unit_for_civ(data, civ_id, CAMEL_SCOUT, CAMEL_RIDER, TECH_CASTLE_BUILT)


def give_franks_a_frankish_paladin_skin(data: DatFile):
    # Persians already do exactly this: Savar is a cosmetic swap-in for Paladin,
    # not a new unit with new stats. Franks' Paladin (already their civ bonus -
    # cheaper, no Blacksmith upgrades needed) gets the same treatment: same
    # name, same stats, same upgrade path, different look. Purely visual -
    # doesn't touch balance at all.
    for civ_id in civ_ids_named(data, ['French']):
        reskin_unit_for_civ(data, civ_id, PALADIN, FRANKISH_PALADIN_SKIN)


def give_crusader_knight_skin_to_crusader_states(data: DatFile):
    # The Teutonic Order, and the Italian maritime republics (Genoa, Venice,
    # Sicily's own Norman-Crusader kingdom) were the civs that actually shipped,
    # funded, fought, and in the Teutons' case were literally founded by the
    # Crusades - the "Crusader Knight" look fits all three at least as well as
    # any single one of them alone. Their own real unique units (Teutonic
    # Knight for Teutons, Genoese Crossbowman for Italians/Sicilians via other
    # grants in this file) are untouched - this is only their Paladin's look.
    for civ_id in civ_ids_named(data, ['Teutons', 'Italians', 'Sicilians']):
        reskin_unit_for_civ(data, civ_id, PALADIN, CRUSADER_KNIGHT_SKIN)


def give_feitoria_to_spanish(data: DatFile):
    # Feitoria (Portuguese's passive-resource-generating trade post) is the
    # signature building of Iberian colonial trade. Spanish share the exact
    # same Age-of-Exploration period and already have their own Conquistador -
    # this is the other half of the same historical picture.
    for civ_id in civ_ids_named(data, ['Spanish']):
        enable_unit_for_civ(data, civ_id, FEITORIA, TECH_CASTLE_BUILT)


def give_folwark_to_bohemians(data: DatFile):
    # Folwark (Poland's Mill-replacing farm-manor building) fits Bohemians
    # just as well - Dawn of the Dukes introduced Poles and Bohemians as a
    # pair, and they share the same Central European agrarian economy.
    # Lithuanians fit at least as well, if not better - Poland-Lithuania were
    # literally one unified Commonwealth for centuries.
    for civ_id in civ_ids_named(data, ['Bohemians', 'Lithuanians']):
        for mill_tier in (MILL, MILL_AGE2, MILL_AGE3, MILL_AGE4):
            upgrade_unit_for_civ(data, civ_id, mill_tier, FOLWARK1, TECH_CASTLE_BUILT)
        # Skip the intermediate tier, same simplification used everywhere else
        # in this file - straight to the final tier once Imperial is reached.
        upgrade_unit_for_civ(data, civ_id, FOLWARK1, FOLWARK3, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_donjon_to_italians(data: DatFile):
    # Donjon (Sicily's cheap mini-Castle) fits Italians just as well - same
    # Mediterranean peninsula, already sharing Genitour with Sicilians in this mod.
    for civ_id in civ_ids_named(data, ['Italians']):
        enable_unit_for_civ(data, civ_id, DONJON, TECH_CASTLE_BUILT)


def give_krepost_to_slavs(data: DatFile):
    # Krepost (Bulgaria's defensive tower) fits Slavs just as well - the same
    # Orthodox Balkan-Slavic connection both civs already share.
    for civ_id in civ_ids_named(data, ['Slavs']):
        enable_unit_for_civ(data, civ_id, KREPOST, TECH_CASTLE_BUILT)


def give_harbor_to_vietnamese(data: DatFile):
    # Harbor (Malay's unique Dock upgrade) fits Vietnamese just as well - the
    # same coastal Southeast Asian maritime-trade economy already tying
    # Vietnamese to Malay/Khmer/Burmese throughout this mod. Vikings fit the
    # same idea from a completely different angle - Norse maritime trade routes
    # were just as central to their identity.
    for civ_id in civ_ids_named(data, ['Vietnamese', 'Vikings']):
        for dock_tier in (TYPE_DOCK_TRAIN_LOCATION, DOCK_AGE2, DOCK_AGE3, DOCK_AGE4):
            upgrade_unit_for_civ(data, civ_id, dock_tier, HARBOR, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_fortified_church_to_teutons_and_spanish(data: DatFile):
    # Fortified Church (a Church that can garrison and fight back) is already
    # shared natively by Armenians and Georgians - a genuinely regional Caucasus
    # tech, not a single-civ unique. Teutons (a crusading military-religious
    # Order literally built around fortified churches) and Spanish (Reconquista-
    # era militant Catholicism) both fit the theme at least as well.
    # https://www.reddit.com/r/aoe2/comments/17lanmw/
    for civ_id in civ_ids_named(data, ['Teutons', 'Spanish']):
        for church_tier in (CHURCH, CHURCH_AGE2, CHURCH_AGE3, CHURCH_AGE4):
            upgrade_unit_for_civ(data, civ_id, church_tier, FORTIFIED_CHURCH, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_thirisadai_to_other_indian_ocean_civs(data: DatFile):
    # Thirisadai is Dravidians' real unique unit, but it trains from the Dock,
    # not the Castle - it was never occupying Dravidians' "core identity" slot,
    # so sharing it doesn't touch that the way handing out a Castle unique
    # would. Fits the wider medieval Indian Ocean maritime-trade world: Bengalis
    # and Gurjaras share the same subcontinental coastline, while Persians (Gulf
    # trade through Siraf/Hormuz) and Saracens (Arab dhow trade across the
    # Arabian Sea to Malabar and beyond) were the other two major trading blocs
    # that same network ran through. No Elite tier exists to worry about.
    civs = ['Bengalis', 'Gurjaras', 'Persians', 'Saracens']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, THIRISADAI, TECH_CASTLE_BUILT)


def give_condottiero_to_other_mercenary_civs(data: DatFile):
    # Condottiero is Italians' real unique unit, but it trains from the
    # Barracks, not the Castle - same reasoning as Thirisadai above, this was
    # never sitting in Italians' core-identity slot. Sicily's own Mediterranean
    # mercenary-captain tradition overlaps heavily with Italy's, already sharing
    # Genitour in this mod on the same "Mediterranean multicultural contact"
    # logic. Byzantines fit for a much more specific reason: in the Empire's
    # final century it leaned directly on hired Italian condottieri-style
    # captains - most famously Giovanni Giustiniani Longo's Genoese mercenary
    # company, who led the defense of Constantinople itself in 1453. No Elite
    # tier exists to worry about.
    civs = ['Sicilians', 'Byzantine']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, CONDOTTIERO, TECH_CASTLE_BUILT)


def mod(data: DatFile):
    logging.info('Applying regional heritage grants')
    give_steppe_lancers_to_civs_with_horse_archer_heritage(data)
    give_elephant_archers_to_civs_with_elephant_heritage(data)
    give_armored_elephants_to_other_elephant_civs(data)
    give_genitours_to_civs_with_light_cavalry_heritage(data)
    give_camel_line_to_steppe_civs_without_camels(data)
    give_imperial_camel_riders_to_other_camel_civs(data)
    give_caravanserai_to_silk_road_civs(data)
    give_mule_carts_to_nomadic_civs(data)
    give_legionaries_to_byzantines(data)
    give_winged_hussars_to_other_eastern_european_civs(data)
    give_imperial_skirmisher_to_civs_with_great_skirmishers(data)
    give_slingers_to_other_american_civs(data)
    give_missionaries_to_civs_with_missionary_heritage(data)
    give_warrior_priests_to_civs_with_shamanic_heritage(data)
    give_settlements_to_mesoamerican_and_andean_civs(data)
    give_fire_lancers_to_japanese(data)
    give_camel_scout_start_to_true_camel_civs(data)
    give_franks_a_frankish_paladin_skin(data)
    give_crusader_knight_skin_to_crusader_states(data)
    give_thirisadai_to_other_indian_ocean_civs(data)
    give_condottiero_to_other_mercenary_civs(data)
    give_feitoria_to_spanish(data)
    give_folwark_to_bohemians(data)
    give_donjon_to_italians(data)
    give_krepost_to_slavs(data)
    give_harbor_to_vietnamese(data)
    give_fortified_church_to_teutons_and_spanish(data)
