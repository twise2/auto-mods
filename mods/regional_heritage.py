import dataclasses
import logging

from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand
from genieutils.unit import AttackOrArmor

from mods.util import enable_unit_for_civ, upgrade_unit_for_civ, grant_effect_to_civ, reskin_unit_for_civ, \
    disable_unit_line_for_civ, set_train_locations_for_civ, disable_tech_for_civ, set_starting_scout_for_civ, \
    research_elite_upgrade_for_civ
from mods.ids import TECH_REQUIREMENT_IMPERIAL_AGE, TYPE_TOWN_CENTER_BUILT, FEUDAL_AGE, \
    CASTLE_AGE, \
    TYPE_ENABLE_DISABLE_UNIT, TYPE_FOOD, TYPE_WOOD, TYPE_GOLD, \
    STEPPE_LANCER, ELITE_STEPPE_LANCER, ELEPHANT_ARCHER, ELITE_ELEPHANT_ARCHER, ARMORED_ELEPHANT, \
    SIEGE_ELEPHANT, GENITOUR, ELITE_GENITOUR, CAMEL_RIDER, \
    CAMEL_SCOUT, CARAVANSERAI, MULE_CART, LEGIONARY, MILITIA, MAN_AT_ARMS, LONG_SWORDSMAN, TECH_LONG_SWORDSMAN, \
    WARRIOR_PRIEST, MISSIONARY, SCOUT_CAVALRY, \
    LIGHT_CAVALRY, TECH_LIGHT_CAVALRY, HUSSAR, WINGED_HUSSAR, \
    SETTLEMENT, SETTLEMENT_AGE_3, FIRE_LANCER, ELITE_FIRE_LANCER, MILL, LUMBER_CAMP, MINING_CAMP, \
    KNIGHT, CAVALIER, PALADIN, TECH_CAVALIER, TECH_PALADIN, FRANKISH_PALADIN_SKIN, CRUSADER_KNIGHT_SKIN, \
    FEITORIA, DONJON, KREPOST, HARBOR, FOLWARK1, FOLWARK3, MILL_AGE2, MILL_AGE3, MILL_AGE4, \
    DOCK_AGE2, DOCK_AGE3, DOCK_AGE4, TYPE_DOCK_TRAIN_LOCATION, \
    CHURCH, CHURCH_AGE2, CHURCH_AGE3, CHURCH_AGE4, FORTIFIED_CHURCH, \
    THIRISADAI, CONDOTTIERO, SLINGER, \
    SAMURAI, ELITE_SAMURAI, FIRE_ARCHER, ELITE_FIRE_ARCHER, ATTACK_CLASS_UNIQUE_UNIT, \
    LONGBOAT, ELITE_LONGBOAT, CLASS_TRANSPORT_BOAT, TRANSPORT_SHIP, \
    ROCKET_CART, HEAVY_ROCKET_CART, TRACTION_TREBUCHET, LOU_CHUAN, \
    HEI_KUANG_CAVALRY, ELITE_HEI_KUANG_CAVALRY, GRENADIER, HAND_CANNONEER, \
    JIAN_SWORDSMAN, ELITE_JIAN_SWORDSMAN, TEMPLE_GUARD, ELITE_TEMPLE_GUARD, \
    WAR_CHARIOT, ELITE_WAR_CHARIOT

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
    #
    # Huns: real, previously-hidden collision at the default Stable button 4,
    # found via a fix to audit_collisions.py (it only ever checked a unit's
    # *first* train_location and only TYPE_ENABLE_DISABLE_UNIT targets,
    # missing units that only ever appear as a TYPE_UPGRADE_UNIT target with
    # a second location). Huns' own real, correctly-gated native tech
    # ("Elite Tarkan", civ=17) upgrades unit 886 -> 887 (UTARK) alongside its
    # main 755 -> 757 upgrade, and 887's own second train_location is the
    # exact same Stable button 4 this grant otherwise defaults to. Rather
    # than dropping Huns entirely, keep the grant but relocate their own
    # copy to Stable button 3 - confirmed free for Huns (their camel line,
    # the other real occupant of button 3, was never given/native to them).
    civs = ['Chinese', 'Bulgarians', 'Lithuanians', 'Hindustanis', 'Magyars', 'Slavs', 'Persians', 'Turks', 'Huns']
    for civ_id in civ_ids_named(data, civs):
        enable_tech = enable_unit_for_civ(data, civ_id, STEPPE_LANCER, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Elite Steppe Lancer"
        # tech exactly (600 food/550 gold, Stable button 9, 55s) - a real,
        # player-researched upgrade, not the free/instant default. Also
        # fixes the real bug that motivated this: requiring enable_tech
        # explicitly means the elite tier can never complete before the
        # base tier was actually enabled (confirmed happening for civs that
        # reached Imperial Age without ever building a Castle).
        research_elite_upgrade_for_civ(data, civ_id, [(STEPPE_LANCER, ELITE_STEPPE_LANCER)], [enable_tech],
                                        101, 9, [(TYPE_FOOD, 600), (TYPE_GOLD, 550)], 55,
                                        f'Elite Steppe Lancer for {data.civs[civ_id].name}', 715)
    huns_id, = civ_ids_named(data, ['Huns'])
    set_train_locations_for_civ(data, huns_id, STEPPE_LANCER, [(101, 3)])
    set_train_locations_for_civ(data, huns_id, ELITE_STEPPE_LANCER, [(101, 3)])


def give_elephant_archers_to_civs_with_elephant_heritage(data: DatFile):
    # Elephant Archers are currently Bengali/Dravidian/Gurjaran only, despite several
    # other civs having a strong historical elephant-warfare tradition.
    # https://www.reddit.com/r/aoe2/comments/10mqm64/sotl_should_more_civs_get_elephant_archers/
    civs = ['Persians', 'Burmese', 'Malay', 'Khmer', 'Vietnamese']
    for civ_id in civ_ids_named(data, civs):
        enable_tech = enable_unit_for_civ(data, civ_id, ELEPHANT_ARCHER, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Elite Elephant Archer"
        # (900 food/500 gold, Archery Range button 8, 80s).
        research_elite_upgrade_for_civ(data, civ_id, [(ELEPHANT_ARCHER, ELITE_ELEPHANT_ARCHER)], [enable_tech],
                                        87, 8, [(TYPE_FOOD, 900), (TYPE_GOLD, 500)], 80,
                                        f'Elite Elephant Archer for {data.civs[civ_id].name}', 481)


def give_armored_elephants_to_other_elephant_civs(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/ubkjoa/armored_elephants_for_khmer_burmese_and_malay
    civs = ['Khmer', 'Burmese', 'Malay', 'Ethiopians', 'Vietnamese']
    for civ_id in civ_ids_named(data, civs):
        enable_tech = enable_unit_for_civ(data, civ_id, ARMORED_ELEPHANT, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Elite Battle Elephant"
        # tech (1100 food/700 gold, Stable button 9, 100s) - the real name
        # of Armored Elephant's own elite upgrade in the actual data.
        research_elite_upgrade_for_civ(data, civ_id, [(ARMORED_ELEPHANT, SIEGE_ELEPHANT)], [enable_tech],
                                        101, 9, [(TYPE_FOOD, 1100), (TYPE_GOLD, 700)], 100,
                                        f'Elite Battle Elephant for {data.civs[civ_id].name}', 631)


def give_genitours_to_civs_with_light_cavalry_heritage(data: DatFile):
    # Genitours (Iberian/North African light skirmish cavalry) are currently
    # Berber-only despite the broader Mediterranean/Islamic world using them -
    # Italy and Sicily both had deep, centuries-long Muslim-Mediterranean contact
    # (Norman-Arab-Byzantine Sicily especially) that fits the same light-cavalry
    # tradition.
    # https://www.reddit.com/r/aoe2/comments/106i52l/genitours_for_middle_eastern_civs/
    civs = ['Spanish', 'Portuguese', 'Persians', 'Saracens', 'Malians', 'Turks', 'Italians', 'Sicilians']
    for civ_id in civ_ids_named(data, civs):
        enable_tech = enable_unit_for_civ(data, civ_id, GENITOUR, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Elite Genitour" tech
        # (500 food/450 wood, Archery Range button 0, 60s).
        research_elite_upgrade_for_civ(data, civ_id, [(GENITOUR, ELITE_GENITOUR)], [enable_tech],
                                        87, 0, [(TYPE_FOOD, 500), (TYPE_WOOD, 450)], 60,
                                        f'Elite Genitour for {data.civs[civ_id].name}', 599)


# give_camel_line_to_steppe_civs_without_camels was removed - user decided it
# made no sense. Cumans keep their real, native cavalry access unmodified
# (Cumans genuinely lack Paladin in vanilla, a well-known real limitation,
# not something this mod should paper over with an invented camel
# substitute). Huns' Knight/Cavalier/Paladin was restored at the time for
# the same reason - the removal back then leaned on this same invented
# camel line as their substitute, which didn't hold up.
#
# That's since changed: Huns now have a real, non-invented substitute -
# their own Steppe Lancer/Elite Steppe Lancer grant (see
# give_steppe_lancers_to_civs_with_horse_archer_heritage above), Stable-
# trained for Food+Gold same as Knight, satisfying the exact two-part test
# remove_knight_line_from_true_steppe_and_camel_civs below already applies
# to Turks. Huns are back in that removal - see there for the current
# reasoning.


def give_caravanserai_to_silk_road_civs(data: DatFile):
    # Caravanserai are currently Hindustani/Persian only; the wider Silk Road trade
    # network ran straight through these civs too.
    # https://www.reddit.com/r/aoe2/comments/10a3jg9/historically_persian_should_also_have_access_to/
    civs = ['Saracens', 'Chinese', 'Mongols', 'Turks', 'Tatars']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, CARAVANSERAI, TECH_REQUIREMENT_IMPERIAL_AGE)


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
    # Real cost/location, matching vanilla's own "Legionary" tech (800
    # food/400 gold, Barracks button 6, 100s). No enable_unit_for_civ here -
    # Militia/Man-at-Arms/Long Swordsman are already real, normal trainable
    # units for Byzantines, not something this mod separately introduces -
    # so the real prerequisite is TECH_LONG_SWORDSMAN (has the player
    # actually researched that tier), matching vanilla's own real Legionary
    # tech exactly (it requires Imperial Age + "Long Swordsman" researched,
    # not an enable tech).
    for civ_id in civ_ids_named(data, ['Byzantine']):
        research_elite_upgrade_for_civ(
            data, civ_id,
            [(MILITIA, LEGIONARY), (MAN_AT_ARMS, LEGIONARY), (LONG_SWORDSMAN, LEGIONARY)],
            [TECH_LONG_SWORDSMAN], 12, 6, [(TYPE_FOOD, 800), (TYPE_GOLD, 400)], 100,
            f'Legionary for {data.civs[civ_id].name}', 885)


def give_winged_hussars_to_other_eastern_european_civs(data: DatFile):
    # Winged Hussars are currently Polish/Lithuanian only, but Hungary and the Cuman
    # cavalry tradition both fed directly into the same eastern-European hussar style.
    # https://www.reddit.com/r/aoe2/comments/qu6b4a/should_magyars_get_winged_hussars_too/
    #
    # Real cost/location, matching vanilla's own "Winged Hussar" tech (600
    # food/800 gold, Stable button 0, 60s). Like Legionary above, no
    # enable_unit_for_civ - Scout Cavalry/Light Cavalry/Hussar are already
    # real, normal trainable units for these civs. Vanilla's own real
    # Winged Hussar tech requires Imperial Age + Light Cavalry researched +
    # (Poles' or Lithuanians' own specific unlock tech, an OR-style
    # threshold that doesn't generalize to a new civ) - using just
    # TECH_LIGHT_CAVALRY here, the one part of that gating that's actually
    # about the player's own progress rather than someone else's civ-
    # specific content.
    for civ_id in civ_ids_named(data, ['Magyars', 'Cumans']):
        research_elite_upgrade_for_civ(
            data, civ_id,
            [(SCOUT_CAVALRY, WINGED_HUSSAR), (LIGHT_CAVALRY, WINGED_HUSSAR), (HUSSAR, WINGED_HUSSAR)],
            [TECH_LIGHT_CAVALRY], 101, 0, [(TYPE_FOOD, 600), (TYPE_GOLD, 800)], 60,
            f'Winged Hussar for {data.civs[civ_id].name}', 786)


def give_slingers_to_other_american_civs(data: DatFile):
    # Slinger is a `civ=-1` "make available" unit just like Steppe Lancer/
    # Elephant Archer/Genitour - currently native to Incas, Mapuche, Muisca,
    # and Tupi (confirmed via the real CivTechTrees), the four Andean/Amazonian
    # civs. Aztecs and Mayans are the same pre-Columbian American world (already
    # tied to Incas via Settlement/Warrior Priest in this mod) and share the
    # same documented Mesoamerican sling-warfare tradition.
    civs = ['Aztecs', 'Mayan']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, SLINGER, CASTLE_AGE)


def give_missionaries_to_civs_with_missionary_heritage(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/ka4jvi/why_dont_portuguese_have_access_to_missionaries/
    # Teutons (a crusading Catholic military order) and Romans (birthplace of the
    # Catholic Church itself) fit at least as well as the original three. French
    # inherit the same Frankish-Crusader-kingdoms Catholic tradition. British
    # (eventual global colonial-missionary reach) and Burgundians (devout
    # Catholic patrons of the Crusades) round out the Catholic-Europe theme.
    civs = ['Italians', 'Portuguese', 'Byzantine', 'Teutons', 'Romans', 'French', 'British', 'Burgundians']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, MISSIONARY, CASTLE_AGE)


def give_warrior_priests_to_civs_with_shamanic_heritage(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/17egkrm/for_fun_what_if_the_new_warrior_priest_from/
    # Mayans and Incas share the same Mesoamerican/Andean shamanic-religious
    # tradition Aztecs already have this from; Goths fit the same Germanic
    # pagan-warband religion already represented by Vikings/Celts here. Koreans
    # fit the same "shamanic tradition alongside an organized religion" pattern
    # Japanese/Chinese already represent, via Korean mudang shamanism. Teutons
    # dropped from this list - confirmed via audit_collisions.py that they
    # also receive Missionary (give_missionaries_to_civs_with_missionary_heritage
    # above), and both units train from the exact same Monastery button 14, a
    # genuine self-inflicted collision. Missionary's reasoning for Teutons (a
    # crusading Catholic military order) is the more specific, better-reasoned
    # fit of the two, so it wins.
    civs = ['Vikings', 'Celts', 'Aztecs', 'Dravidians', 'Malians', 'Japanese', 'Chinese',
            'Mayan', 'Incas', 'Goths', 'Koreans']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, WARRIOR_PRIEST, CASTLE_AGE)


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
    # Confirmed via Muisca's own real futuravailableunits.json entry that their
    # Builder menu lists neither Mill, Lumber Camp, nor Mining Camp - Settlement
    # is a full economic-building replacement for all three, not just Mill.
    # Bundled into one tech so all three disappear at the exact moment Settlement
    # becomes available, not before.
    #
    # Gated on TYPE_TOWN_CENTER_BUILT (fires essentially immediately - every
    # civ starts with a Town Center), not TECH_CASTLE_BUILT. Settlement is
    # meant to be these civs' primary early-game economic building, the same
    # way it genuinely is for Muisca/Mapuche/Tupi - gating it behind actually
    # constructing a Castle (confirmed via user testing: never fires unless a
    # real Castle is built, not just Castle Age reached) would leave Aztecs/
    # Mayans/Incas stuck on plain Mill through most of a normal game, the
    # opposite of the intent. Matches give_mule_carts_to_nomadic_civs above,
    # which already correctly uses this same immediate trigger.
    civs = ['Aztecs', 'Mayan', 'Incas']
    for civ_id in civ_ids_named(data, civs):
        commands = [
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=SETTLEMENT, b=1, c=-1, d=0.0),
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=MILL, b=0, c=-1, d=0.0),
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=LUMBER_CAMP, b=0, c=-1, d=0.0),
            EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=MINING_CAMP, b=0, c=-1, d=0.0),
        ]
        grant_effect_to_civ(data, civ_id, commands, TYPE_TOWN_CENTER_BUILT,
                             f'Swap Mill/Lumber Camp/Mining Camp for Settlement for {data.civs[civ_id].name}')
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
        enable_tech = enable_unit_for_civ(data, civ_id, FIRE_LANCER, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Elite Fire Lancer"
        # tech (750 food/400 gold, Barracks button 9, 50s).
        research_elite_upgrade_for_civ(data, civ_id, [(FIRE_LANCER, ELITE_FIRE_LANCER)], [enable_tech],
                                        12, 9, [(TYPE_FOOD, 750), (TYPE_GOLD, 400)], 50,
                                        f'Elite Fire Lancer for {data.civs[civ_id].name}', 982)


def give_rocket_cart_to_japanese(data: DatFile):
    # Rocket Cart (`civ=-1` regional siege) is currently Chinese/Jurchen/
    # Khitan/Korean only - the exact same East Asian gunpowder-contact group
    # Fire Lancer above already extends to Japan.
    for civ_id in civ_ids_named(data, ['Japanese']):
        enable_tech = enable_unit_for_civ(data, civ_id, ROCKET_CART, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Heavy Rocket Cart"
        # tech (800 wood/600 gold, Siege Workshop button 7, 75s).
        research_elite_upgrade_for_civ(data, civ_id, [(ROCKET_CART, HEAVY_ROCKET_CART)], [enable_tech],
                                        49, 7, [(TYPE_WOOD, 800), (TYPE_GOLD, 600)], 75,
                                        f'Heavy Rocket Cart for {data.civs[civ_id].name}', 980)


def give_traction_trebuchet_to_east_asian_civs(data: DatFile):
    # Traction Trebuchet (`civ=-1` regional siege) is currently Shu/Wu/Wei
    # only - narrow Three Kingdoms Chronicles content, where it deliberately
    # replaces the standard Trebuchet entirely (a real, historically correct
    # design choice - counterweight trebuchets didn't reach China until
    # Mongol-era contact centuries later). Chinese (the main civ, spanning a
    # much longer timeline that plausibly reaches that later contact too)
    # gets it as an additional option alongside their standard Trebuchet,
    # not a replacement. Jurchens and Khitans are Song-dynasty-era rival/
    # successor states with the same plausible technology exposure, already
    # tied to Chinese in this mod via Fire Lancer/Rocket Cart. For Khitans
    # specifically this is actually a real replacement, not a pure addition:
    # Khitans' own native second unique unit, Mounted Trebuchet (id 1923),
    # trains from the exact same Siege Workshop button 4 as Traction
    # Trebuchet - confirmed via disable_unit_lines.py's auto-collision
    # detector, which correctly removes Mounted Trebuchet in favor of this
    # grant rather than leaving both fighting over one button.
    for civ_id in civ_ids_named(data, ['Chinese', 'Jurchens', 'Khitans']):
        enable_unit_for_civ(data, civ_id, TRACTION_TREBUCHET, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_lou_chuan_to_other_east_asian_civs(data: DatFile):
    # Lou Chuan (`civ=-1` regional warship) is currently Chinese/Jurchen/Shu/
    # Wu/Wei only. Khitans, Koreans, and Vietnamese are the same East Asian
    # naval/gunpowder-contact group this mod already ties together via Fire
    # Lancer/Rocket Cart.
    for civ_id in civ_ids_named(data, ['Khitans', 'Koreans', 'Vietnamese']):
        enable_unit_for_civ(data, civ_id, LOU_CHUAN, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_hei_kuang_cavalry_to_chinese(data: DatFile):
    # Hei-Kuang Cavalry (`civ=-1` regional cavalry) is currently Shu/Wei/Wu
    # only - Chinese (the main civ) represents the same broader Chinese
    # military tradition those three Three Kingdoms sub-civs split out of.
    # Unlike Traction Trebuchet above, this replaces Knight/Cavalier/Paladin
    # outright rather than sitting alongside it - it trains from the exact
    # same Stable button 2 Knight does, for the same Food+Gold cost, so it's
    # a genuine drop-in swap, not an addition. See
    # remove_knight_line_from_chinese_for_hei_kuang_cavalry below.
    for civ_id in civ_ids_named(data, ['Chinese']):
        enable_tech = enable_unit_for_civ(data, civ_id, HEI_KUANG_CAVALRY, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Heavy Hei-Kuang
        # Cavalry" tech (350 food/250 gold, Stable button 7, 70s).
        research_elite_upgrade_for_civ(data, civ_id, [(HEI_KUANG_CAVALRY, ELITE_HEI_KUANG_CAVALRY)], [enable_tech],
                                        101, 7, [(TYPE_FOOD, 350), (TYPE_GOLD, 250)], 70,
                                        f'Heavy Hei-Kuang Cavalry for {data.civs[civ_id].name}', 1033)


def give_grenadier_to_gunpowder_civs_without_hand_cannoneer(data: DatFile):
    # Grenadier (`civ=-1` regional gunpowder infantry) is currently Jurchens
    # only - and Jurchens genuinely lack Hand Cannoneer natively (confirmed
    # via CivTechTrees), so it's already a real replacement for them, not an
    # addition. Grenadier trains from the exact same Archery Range button 4
    # as Hand Cannoneer, for a near-identical cost - a genuine drop-in swap.
    # Chinese, Khitans, Vietnamese, and Mongols are in the exact same
    # position (confirmed lacking Hand Cannoneer natively) and China is the
    # actual historical origin of gunpowder/grenade weapons in the first
    # place. Koreans and Turks DO have real native Hand Cannoneer access,
    # but both have a genuine, well-documented grenade tradition of their
    # own distinct from generic hand cannon infantry - Korea's
    # "Bigyeokjincheolloe" exploding-shell device, and the Ottoman
    # "Humbaraci" grenadier corps (a real branch distinct from the
    # Janissaries - Janissary trains from the Castle at button 1, the
    # universal true-unique slot, completely unrelated to this building/
    # button, so this doesn't touch or dilute that identity at all).
    civs = ['Chinese', 'Khitans', 'Vietnamese', 'Mongols', 'Koreans', 'Turks']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, GRENADIER, CASTLE_AGE)
        disable_unit_line_for_civ(data, civ_id, {HAND_CANNONEER}, CASTLE_AGE)


def give_jian_swordsman_to_other_three_kingdoms_civs(data: DatFile):
    # Jian Swordsman (`civ=-1` regional infantry) is currently Wu only -
    # Shu and Wei are the other two Three Kingdoms Chronicles civs, the same
    # broader Han-Chinese swordsman tradition Wu's own unit represents.
    # Trains from the exact same Barracks button 4 Wu already uses, free for
    # both - a pure addition, not a replacement of anything.
    # Left as the free/instant upgrade (not research_elite_upgrade_for_civ,
    # unlike every other unit elite-tier grant in this file) - checked and
    # confirmed there's no real "Elite Jian Swordsman" tech anywhere in the
    # actual data to copy a cost/location from. Wu's own real
    # futuravailableunits.json entry never listed their own Elite Jian
    # Swordsman either, only the base tier - this looks like a genuine gap
    # in the vanilla data itself, not something to invent a cost for.
    for civ_id in civ_ids_named(data, ['Shu', 'Wei']):
        enable_unit_for_civ(data, civ_id, JIAN_SWORDSMAN, CASTLE_AGE)
        upgrade_unit_for_civ(data, civ_id, JIAN_SWORDSMAN, ELITE_JIAN_SWORDSMAN, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_temple_guard_to_andean_and_mesoamerican_civs(data: DatFile):
    # Temple Guard (`civ=-1` regional infantry) is currently Muisca only,
    # training from both Barracks button 4 and Monastery button 14 - Sun-
    # temple warrior-priests fit Inca religious identity at least as well as
    # Muisca's. Restricted to Barracks-only for both civs below (dropping
    # the Monastery location) since Monastery button 14 is already occupied
    # by their own granted Warrior Priest (give_warrior_priests_to_civs_with_
    # shamanic_heritage already covers both Incas and Aztecs) - a real
    # collision, not a free second slot.
    #
    # Real cost/location for the research itself, matching vanilla's own
    # "Elite Temple Guard" tech (500 food/650 gold, Barracks button 9, 60s) -
    # note this research button is separate from wherever the unit itself
    # trains (button 4 for Incas, button 3 for Aztecs, set below), the same
    # way a training slot and a research slot are always independent
    # buttons at the same building.
    #
    # Incas: Barracks button 4 is free - a plain addition.
    incas_id, = civ_ids_named(data, ['Incas'])
    enable_tech = enable_unit_for_civ(data, incas_id, TEMPLE_GUARD, CASTLE_AGE)
    research_elite_upgrade_for_civ(data, incas_id, [(TEMPLE_GUARD, ELITE_TEMPLE_GUARD)], [enable_tech],
                                    12, 9, [(TYPE_FOOD, 500), (TYPE_GOLD, 650)], 60,
                                    f'Elite Temple Guard for {data.civs[incas_id].name}', 1401)
    set_train_locations_for_civ(data, incas_id, TEMPLE_GUARD, [(12, 4)])
    set_train_locations_for_civ(data, incas_id, ELITE_TEMPLE_GUARD, [(12, 4)])
    #
    # Aztecs: button 4 is already their own native Eagle Warrior's slot -
    # Temple Guard moves to button 3 (unused for Aztecs; the only other
    # Barracks-button-3 content anywhere is Condottiero, granted only to
    # mercenary-tradition civs, not Aztecs).
    aztecs_id, = civ_ids_named(data, ['Aztecs'])
    enable_tech = enable_unit_for_civ(data, aztecs_id, TEMPLE_GUARD, CASTLE_AGE)
    research_elite_upgrade_for_civ(data, aztecs_id, [(TEMPLE_GUARD, ELITE_TEMPLE_GUARD)], [enable_tech],
                                    12, 9, [(TYPE_FOOD, 500), (TYPE_GOLD, 650)], 60,
                                    f'Elite Temple Guard for {data.civs[aztecs_id].name}', 1401)
    set_train_locations_for_civ(data, aztecs_id, TEMPLE_GUARD, [(12, 3)])
    set_train_locations_for_civ(data, aztecs_id, ELITE_TEMPLE_GUARD, [(12, 3)])


def give_war_chariot_to_celts(data: DatFile):
    # War Chariot/Elite War Chariot (ids 2150/2151, Stable button 4) really
    # is Achaemenids' real native unit (tech 1169, civ=46) - the earlier
    # give_war_chariot_to_persians was reverted for wrongly assuming it was
    # unclaimed. But unlike Phalangite/Sannahya (explicitly named "Macedonian
    # Unique Unit"/"Puru Unique Unit" in their own enabling techs), War
    # Chariot's tech is just named "Enable War Chariot" - no "unique"
    # designation anywhere in the real data. That's a genuine distinction,
    # not just a rationalization: it reads as regional flavor (like Steppe
    # Lancer/Battle Elephant) that happens to be scoped to one civ so far,
    # not a labeled identity marker.
    #
    # Celts: ancient Celtic/British war chariots are about as well-attested
    # a historical chariot tradition as exists (Julius Caesar's own accounts
    # of British chariot tactics). Added alongside their full native Knight
    # line, not as a replacement - that's genuinely ancient-era heritage,
    # not still their real medieval military identity by the period AoE2's
    # Celts represent, so framing it as a bonus option rather than claiming
    # it defines them. Stable button 4 confirmed free (only Scout Cavalry/
    # Light Cavalry/Hussar/Knight/Cavalier/Paladin listed).
    for civ_id in civ_ids_named(data, ['Celts']):
        enable_tech = enable_unit_for_civ(data, civ_id, WAR_CHARIOT, CASTLE_AGE)
        # Real cost/location, matching vanilla's own "Elite War Chariot"
        # tech (600 food/500 wood, Stable button 9, 90s).
        research_elite_upgrade_for_civ(data, civ_id, [(WAR_CHARIOT, ELITE_WAR_CHARIOT)], [enable_tech],
                                        101, 9, [(TYPE_FOOD, 600), (TYPE_WOOD, 500)], 90,
                                        f'Elite War Chariot for {data.civs[civ_id].name}', 1171)


def _configure_samurai_ranged_form(base_unit, ranged_unit):
    # Port of the old regionalAdditions branch's SwapSamuraiUnitToRanged
    # (patches/regional_additions.cpp, commit 99abeaf) - the `nothing`/`trait`
    # fields are the same DE-native "activate to swap unit" mechanic
    # Achaemenids' own real Immortal <-> Immortal Ranged uses, just applied to
    # Samurai/Elite Samurai instead of inventing a new mechanic.
    #
    # Deliberately weak everywhere except the anti-unique-unit niche Samurai
    # already has (real class-30 bonus, currently amount=0 on the base unit) -
    # this is a situational tool against enemy unique units, not a second
    # full-time attack mode.
    base_unit.nothing = ranged_unit.id
    base_unit.trait = base_unit.trait | 8

    ranged_unit.nothing = base_unit.id
    ranged_unit.trait = ranged_unit.trait | 8
    ranged_unit.icon_id = base_unit.icon_id
    ranged_unit.creatable.hero_glow_graphic = -1
    ranged_unit.creatable.hero_mode = 0
    ranged_unit.hit_points = base_unit.hit_points
    ranged_unit.type_50.armours = base_unit.type_50.armours
    ranged_unit.type_50.base_armor = base_unit.type_50.base_armor
    ranged_unit.type_50.displayed_melee_armour = base_unit.type_50.displayed_melee_armour
    ranged_unit.creatable.displayed_pierce_armour = base_unit.creatable.displayed_pierce_armour
    ranged_unit.type_50.displayed_attack = 1
    # A base Archer has range 4 - one less than that, on top of the gutted
    # base attack below, keeps this a worse choice than actually training
    # Archers whenever there's no enemy unique unit around to punish.
    ranged_unit.type_50.displayed_range = 3
    ranged_unit.type_50.max_range = 3.0
    ranged_unit.type_50.reload_time = 5.0
    ranged_unit.type_50.displayed_reload_time = 5.0
    ranged_unit.type_50.attacks = [
        AttackOrArmor(class_=3, amount=1),
        AttackOrArmor(class_=ATTACK_CLASS_UNIQUE_UNIT, amount=30),
    ]
    ranged_unit.speed = 0.8


def give_samurai_a_ranged_mode_swap(data: DatFile):
    # Samurai's whole civ identity is already "extra damage vs enemy unique
    # units" - letting them swap to a weak ranged stance that ONLY helps in
    # that same niche (a poor attacker against everything else) extends that
    # identity instead of adding an unrelated new one.
    # Fire Archer/Elite Fire Archer are used purely as graphic donors here
    # (their own real stats are irrelevant, this fully overwrites them) -
    # visually distinct from standard Arbalester, unlike Archer of the
    # Eyes/Luu Nhan Chu, which both turned out to share Arbalester's exact
    # graphic.
    for civ_id in civ_ids_named(data, ['Japanese']):
        civ = data.civs[civ_id]
        _configure_samurai_ranged_form(civ.units[SAMURAI], civ.units[FIRE_ARCHER])
        _configure_samurai_ranged_form(civ.units[ELITE_SAMURAI], civ.units[ELITE_FIRE_ARCHER])


def give_camel_scout_start_to_true_camel_civs(data: DatFile):
    # Gurjaras start scouting with a Camel Scout instead of a normal Scout
    # Cavalry, which then grows into the same Camel Rider line. Restricted to
    # civs with genuinely deep, native camel identity - not just "some camel
    # flavor exists somewhere in this mod." Narrowed from an earlier version
    # of this list (Cumans/Huns/Berbers/Saracens/Turks) after checking each
    # civ's real ownership directly rather than trusting an earlier comment
    # here, which turned out to be wrong:
    #
    # - Berbers, Saracens: genuine native Camel Rider/Heavy Camel Rider -
    #   Almoravid/Almohad and early-Islamic camel-cavalry identity, real
    #   enough that this mod's own Knight-line removal already leans on it
    #   (see remove_knight_line_from_true_steppe_and_camel_civs above).
    # - Hindustanis: added - arguably the deepest native camel identity of
    #   any civ. Tech 521 "Heavy Camel" (civ=20/Hindustanis specifically,
    #   not civ=-1) upgrades Camel Scout, Camel Rider, *and* Heavy Camel
    #   Rider all directly into Imperial Camel Rider - a real, exclusive,
    #   civ-specific tech object, the same unambiguous signal this file
    #   already trusts for Savar (tech 526, civ=8/Persians). Nobody else in
    #   the game has Imperial Camel Rider at all.
    # - Turks: dropped. The old comment justified them via "the Imperial
    #   Camel Rider grant below" - that grant was fully reverted earlier
    #   this session, and the claim was never re-verified. Direct .dat
    #   inspection (tech 521 above) shows Imperial Camel Rider is natively
    #   Hindustanis-only, not Berber/Saracen/Turk. Turks' real identity is
    #   gunpowder/Janissary, not camels.
    # - Cumans, Huns: dropped. give_camel_line_to_steppe_civs_without_camels
    #   above already grants them Camel Rider/Heavy Camel Rider, but its own
    #   comment says this is "historical flavor only" for Huns and a gap-
    #   filling Paladin substitute for Cumans, not deep native identity -
    #   this mod's own addition, not something to also treat as their
    #   starting-unit heritage.
    # - Ethiopians: added. Their real unique tech (574, "Ethiopian UT" /
    #   "Royal Heirs") has 4 dedicated commands explicitly buffing Camel
    #   Scout, Camel Rider, Heavy Camel Rider, *and* Imperial Camel Rider by
    #   id, civ-scoped to Ethiopians specifically - the same unambiguous
    #   civ-specific-tech standard as Hindustanis/Savar above.
    # - Malians: checked and declined. A web search suggested their real
    #   unique tech "Farimba" unlocks Heavy Camel Rider for them - checked
    #   directly against the .dat and that's wrong: Farimba (tech 605) and
    #   their other unique tech Tigui (606) affect Town Center regeneration/
    #   garrison and an unrelated stat, nothing camel-related at all. Not
    #   adding based on a claim the real data contradicts.
    # - Persians: considered, not added. CivTechTrees shows Camel Rider/
    #   Heavy Camel Rider as "ResearchedCompleted" for them, but that exact
    #   same status also shows for Turks and Mongols - civs already
    #   confirmed to NOT have real camel identity - so it's evidently a
    #   "reachable somewhere in the full tech tree" signal, not a true-
    #   identity one. No civ-specific tech found. Left out for lack of real
    #   evidence, not ruled out for good - worth another look if a
    #   better signal turns up.
    #
    # The actual starting-unit swap isn't a tech/effect at all - confirmed via
    # direct .dat comparison that it's a plain per-civ static value,
    # Civ.resources[RESOURCE_STARTING_SCOUT_UNIT], read once at game start.
    # Gurjaras has it set to Camel Scout's own unit id; every other civ has it
    # set to Scout Cavalry's. set_starting_scout_for_civ replicates that
    # exactly. Still also enabling Camel Scout early via a real tech (Town
    # Center built, i.e. immediately) so it stays trainable as a replacement
    # once the starting one is lost, not just present as a one-off.
    civs = ['Berbers', 'Saracens', 'Hindustanis', 'Ethiopians']
    for civ_id in civ_ids_named(data, civs):
        set_starting_scout_for_civ(data, civ_id, CAMEL_SCOUT)
        enable_unit_for_civ(data, civ_id, CAMEL_SCOUT, TYPE_TOWN_CENTER_BUILT)
        upgrade_unit_for_civ(data, civ_id, CAMEL_SCOUT, CAMEL_RIDER, CASTLE_AGE)


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
        enable_unit_for_civ(data, civ_id, FEITORIA, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_folwark_to_bohemians(data: DatFile):
    # Folwark (Poland's Mill-replacing farm-manor building) fits Bohemians
    # just as well - Dawn of the Dukes introduced Poles and Bohemians as a
    # pair, and they share the same Central European agrarian economy.
    # Lithuanians fit at least as well, if not better - Poland-Lithuania were
    # literally one unified Commonwealth for centuries.
    #
    # Gated on TYPE_TOWN_CENTER_BUILT, not TECH_CASTLE_BUILT - same fix as
    # give_settlements_to_mesoamerican_and_andean_civs above and for the same
    # reason: Folwark is a primary early-game economic building, and gating
    # it behind actually constructing a Castle (confirmed via user testing
    # that the analogous Settlement bug left Mayans on plain Mill for an
    # entire normal game) would defeat the point.
    for civ_id in civ_ids_named(data, ['Bohemians', 'Lithuanians']):
        for mill_tier in (MILL, MILL_AGE2, MILL_AGE3, MILL_AGE4):
            upgrade_unit_for_civ(data, civ_id, mill_tier, FOLWARK1, TYPE_TOWN_CENTER_BUILT)
        # Skip the intermediate tier, same simplification used everywhere else
        # in this file - straight to the final tier once Imperial is reached.
        upgrade_unit_for_civ(data, civ_id, FOLWARK1, FOLWARK3, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_donjon_to_italians(data: DatFile):
    # Donjon (Sicily's cheap mini-Castle) fits Italians just as well - same
    # Mediterranean peninsula, already sharing Genitour with Sicilians in this mod.
    for civ_id in civ_ids_named(data, ['Italians']):
        enable_unit_for_civ(data, civ_id, DONJON, TYPE_TOWN_CENTER_BUILT)


def give_krepost_to_slavs(data: DatFile):
    # Krepost (Bulgaria's defensive tower) fits Slavs just as well - the same
    # Orthodox Balkan-Slavic connection both civs already share.
    for civ_id in civ_ids_named(data, ['Slavs']):
        enable_unit_for_civ(data, civ_id, KREPOST, CASTLE_AGE)


def give_harbor_to_vietnamese(data: DatFile):
    # Harbor (Malay's unique Dock upgrade) fits Vietnamese just as well - the
    # same coastal Southeast Asian maritime-trade economy already tying
    # Vietnamese to Malay/Khmer/Burmese throughout this mod. Vikings fit the
    # same idea from a completely different angle - Norse maritime trade routes
    # were just as central to their identity.
    # Real cost/location, matching vanilla's own "Malay UT" tech that grants
    # Harbor (300 food/300 gold, Castle button 7, 40s) - unlike every other
    # elite-tier grant in this file, the real tech only requires Feudal Age
    # (not Imperial), so age_tech overrides the default here to match.
    for civ_id in civ_ids_named(data, ['Vietnamese', 'Vikings']):
        research_elite_upgrade_for_civ(
            data, civ_id,
            [(dock_tier, HARBOR) for dock_tier in (TYPE_DOCK_TRAIN_LOCATION, DOCK_AGE2, DOCK_AGE3, DOCK_AGE4)],
            [], 82, 7, [(TYPE_FOOD, 300), (TYPE_GOLD, 300)], 40,
            f'Harbor for {data.civs[civ_id].name}', 624, age_tech=FEUDAL_AGE)


def give_longboats_the_ability_to_transport_units(data: DatFile):
    # Longboats were real Viking troop transports historically, not just
    # warships - the game's own Transport Ship already has this exact
    # capability (garrison_capacity, TRANSPORT_BOAT class, an unload task), so
    # this borrows that real, working task definition rather than guessing at
    # one. Ported from the old regionalAdditions branch's makeLongboatsTransports
    # (patches/regional_additions.cpp) - applies to every civ's own copy since
    # Longboat is a real trainable unit for Vikings only anyway, matching the
    # old branch's own civ-agnostic loop rather than hardcoding a civ list.
    unload_task = next(t for t in data.civs[0].units[TRANSPORT_SHIP].bird.tasks if t.action_type == 109)
    for civ in data.civs:
        for unit_id in (LONGBOAT, ELITE_LONGBOAT):
            unit = civ.units[unit_id]
            unit.garrison_capacity = 5
            unit.class_ = CLASS_TRANSPORT_BOAT
            unit.trait = 3
            unit.bird.tasks.append(dataclasses.replace(unload_task, id=len(unit.bird.tasks)))


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
        enable_unit_for_civ(data, civ_id, THIRISADAI, TECH_REQUIREMENT_IMPERIAL_AGE)


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
        enable_unit_for_civ(data, civ_id, CONDOTTIERO, TECH_REQUIREMENT_IMPERIAL_AGE)


def remove_knight_line_from_true_steppe_and_camel_civs(data: DatFile):
    # Two-part test for every disable_unit_line_for_civ call in this file:
    # (1) the civ has its own distinct gold-cost unit line training from the
    # SAME building as the line being removed - not just "some regional
    # flavor exists," a genuine mechanical substitute, verified against the
    # real train_locations/resource_costs, not assumed - and (2) the line
    # being removed doesn't fit the civ's real historical military identity.
    # Both have to hold. Steppe Lancer and Camel Rider/Heavy Camel Rider
    # both train from the Stable (101) for Food+Gold, identical to Knight's
    # own building/resource profile.
    #
    # Gated on TYPE_TOWN_CENTER_BUILT (essentially immediate), not
    # TECH_CASTLE_BUILT - real user report: Huns could still train Knight
    # for the entire early-mid game and only lost it once a Castle
    # happened to get built, well after their Steppe Lancer substitute
    # was already available. Tried gating on CASTLE_AGE next (matching
    # the substitute's own trigger) - works, but depends on staying in
    # sync with whatever the substitute grant uses, forever. Simpler and
    # strictly safer: confirmed real vanilla Knight itself (tech 166,
    # civ=-1) requires Castle Age and nothing earlier for every civ, so
    # these civs could never actually train Knight before Castle Age
    # anyway, regardless of when this disable fires - gating it immediate
    # produces the identical practical result with no ongoing dependency
    # on any other grant's trigger.
    #
    # Turks: fully-upgraded Steppe Lancer from this mod; Janissary/Sipahi and
    # gunpowder identity, not Western knights.
    #
    # Huns: back in this removal. Dropped once already this session when the
    # only substitute on offer was an invented camel line (a real overreach -
    # taking away Huns' own well-known Knight/Cavalier/Paladin access for
    # something made up was the wrong call, so it was reverted). Since then
    # Huns picked up a real, non-invented substitute of their own: Steppe
    # Lancer/Elite Steppe Lancer (give_steppe_lancers_to_civs_with_horse_
    # archer_heritage above), Stable-trained for Food+Gold - the exact same
    # mechanical substitute Turks already satisfy this test with. The Huns
    # are the textbook nomadic horse-archer civ historically, an even
    # cleaner fit for rule 2 than Turks.
    for civ_id in civ_ids_named(data, ['Turks', 'Huns']):
        disable_unit_line_for_civ(data, civ_id, {KNIGHT, CAVALIER, PALADIN}, TYPE_TOWN_CENTER_BUILT)
        # Cavalier/Paladin are real, player-researched techs (not just the
        # units) - without this, the now-pointless upgrade research still
        # shows up. Uses DE's own real "[FTT]" mechanism (tech 527, "[FTT]
        # Disable Paladin", civ=8/Persians, hides Paladin for them since
        # Savar replaces it - confirmed via direct .dat inspection).
        disable_tech_for_civ(data, civ_id, {TECH_CAVALIER, TECH_PALADIN}, TYPE_TOWN_CENTER_BUILT)
    # Berbers and Saracens: native Camel Rider/Heavy Camel Rider (not
    # granted by this mod - they've always had it); Almoravid/Almohad and
    # early-Islamic camel-cavalry identity, not knights.
    for civ_id in civ_ids_named(data, ['Berbers', 'Saracens']):
        disable_unit_line_for_civ(data, civ_id, {KNIGHT, CAVALIER, PALADIN}, TYPE_TOWN_CENTER_BUILT)
        # Cavalier/Paladin are real, player-researched techs (not just the
        # units) - without this, the now-pointless upgrade research still
        # shows up. Uses DE's own real "[FTT]" mechanism (tech 527, "[FTT]
        # Disable Paladin", civ=8/Persians, hides Paladin for them since
        # Savar replaces it - confirmed via direct .dat inspection).
        disable_tech_for_civ(data, civ_id, {TECH_CAVALIER, TECH_PALADIN}, TYPE_TOWN_CENTER_BUILT)


def remove_knight_line_from_true_elephant_civs(data: DatFile):
    # Same two-part test as remove_knight_line_from_true_steppe_and_camel_civs
    # above. Battle Elephant trains from the Stable (101) for Food+Gold,
    # identical to Knight - and it's each of these civs' own real native
    # unit with the Elite tier already, not something this mod granted
    # (confirmed via CivTechTrees). Ethiopians was considered and dropped -
    # they only have Armored Elephant (Siege Workshop, a different building
    # entirely), so rule 1 doesn't hold for them despite rule 2 clearly
    # fitting.
    for civ_id in civ_ids_named(data, ['Malay', 'Burmese', 'Khmer', 'Vietnamese']):
        disable_unit_line_for_civ(data, civ_id, {KNIGHT, CAVALIER, PALADIN}, TYPE_TOWN_CENTER_BUILT)
        # Cavalier/Paladin are real, player-researched techs (not just the
        # units) - without this, the now-pointless upgrade research still
        # shows up. Uses DE's own real "[FTT]" mechanism (tech 527, "[FTT]
        # Disable Paladin", civ=8/Persians, hides Paladin for them since
        # Savar replaces it - confirmed via direct .dat inspection).
        disable_tech_for_civ(data, civ_id, {TECH_CAVALIER, TECH_PALADIN}, TYPE_TOWN_CENTER_BUILT)


def remove_knight_line_from_chinese_for_hei_kuang_cavalry(data: DatFile):
    # Same two-part test again. Hei-Kuang Cavalry (see
    # give_hei_kuang_cavalry_to_chinese above) trains from the exact same
    # Stable button 2 as Knight, for the same Food+Gold cost, with a real
    # Elite tier - a genuine drop-in replacement, not just "some regional
    # flavor exists." A dedicated function rather than folding into either
    # group above since the reasoning (a specific regional cavalry unit,
    # not a steppe/camel or elephant identity) is its own thing.
    for civ_id in civ_ids_named(data, ['Chinese']):
        disable_unit_line_for_civ(data, civ_id, {KNIGHT, CAVALIER, PALADIN}, TYPE_TOWN_CENTER_BUILT)
        # Cavalier/Paladin are real, player-researched techs (not just the
        # units) - without this, the now-pointless upgrade research still
        # shows up. Uses DE's own real "[FTT]" mechanism (tech 527, "[FTT]
        # Disable Paladin", civ=8/Persians, hides Paladin for them since
        # Savar replaces it - confirmed via direct .dat inspection).
        disable_tech_for_civ(data, civ_id, {TECH_CAVALIER, TECH_PALADIN}, TYPE_TOWN_CENTER_BUILT)


def mod(data: DatFile):
    logging.info('Applying regional heritage grants')
    give_steppe_lancers_to_civs_with_horse_archer_heritage(data)
    give_elephant_archers_to_civs_with_elephant_heritage(data)
    give_armored_elephants_to_other_elephant_civs(data)
    give_genitours_to_civs_with_light_cavalry_heritage(data)
    give_caravanserai_to_silk_road_civs(data)
    give_mule_carts_to_nomadic_civs(data)
    give_legionaries_to_byzantines(data)
    give_winged_hussars_to_other_eastern_european_civs(data)
    give_slingers_to_other_american_civs(data)
    give_missionaries_to_civs_with_missionary_heritage(data)
    give_warrior_priests_to_civs_with_shamanic_heritage(data)
    give_settlements_to_mesoamerican_and_andean_civs(data)
    give_fire_lancers_to_japanese(data)
    give_rocket_cart_to_japanese(data)
    give_traction_trebuchet_to_east_asian_civs(data)
    give_lou_chuan_to_other_east_asian_civs(data)
    give_hei_kuang_cavalry_to_chinese(data)
    give_grenadier_to_gunpowder_civs_without_hand_cannoneer(data)
    give_jian_swordsman_to_other_three_kingdoms_civs(data)
    give_temple_guard_to_andean_and_mesoamerican_civs(data)
    give_war_chariot_to_celts(data)
    give_samurai_a_ranged_mode_swap(data)
    give_camel_scout_start_to_true_camel_civs(data)
    give_franks_a_frankish_paladin_skin(data)
    give_crusader_knight_skin_to_crusader_states(data)
    give_thirisadai_to_other_indian_ocean_civs(data)
    give_condottiero_to_other_mercenary_civs(data)
    remove_knight_line_from_true_steppe_and_camel_civs(data)
    remove_knight_line_from_true_elephant_civs(data)
    remove_knight_line_from_chinese_for_hei_kuang_cavalry(data)
    give_feitoria_to_spanish(data)
    give_folwark_to_bohemians(data)
    give_donjon_to_italians(data)
    give_krepost_to_slavs(data)
    give_harbor_to_vietnamese(data)
    give_longboats_the_ability_to_transport_units(data)
    give_fortified_church_to_teutons_and_spanish(data)
