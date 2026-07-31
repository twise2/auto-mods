import logging

from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand

from mods.util import enable_unit_for_civ, upgrade_unit_for_civ, set_train_button_for_civ, grant_effect_to_civ, \
    reskin_unit_for_civ
from mods.ids import TECH_CASTLE_BUILT, TECH_REQUIREMENT_IMPERIAL_AGE, TYPE_TOWN_CENTER_BUILT, \
    TYPE_CASTLE_TRAIN_LOCATION, TYPE_ENABLE_DISABLE_UNIT, \
    STEPPE_LANCER, ELITE_STEPPE_LANCER, ELEPHANT_ARCHER, ELITE_ELEPHANT_ARCHER, ARMORED_ELEPHANT, \
    SIEGE_ELEPHANT, GENITOUR, ELITE_GENITOUR, CAMEL_RIDER, HEAVY_CAMEL_RIDER, IMPERIAL_CAMEL_RIDER, \
    CAMEL_SCOUT, CARAVANSERAI, MULE_CART, LEGIONARY, MILITIA, MAN_AT_ARMS, LONG_SWORDSMAN, WARRIOR_PRIEST, \
    CONQUISTADOR, MISSIONARY, WAR_ELEPHANT, SCOUT_CAVALRY, \
    LIGHT_CAVALRY, HUSSAR, WINGED_HUSSAR, SKIRMISHER, ELITE_SKIRMISHER, IMPERIAL_SKIRMISHER, \
    SETTLEMENT, SETTLEMENT_AGE_3, FIRE_LANCER, ELITE_FIRE_LANCER, MILL, LUMBER_CAMP, MINING_CAMP, \
    CENTURION, PALADIN, FRANKISH_PALADIN_SKIN, CRUSADER_KNIGHT_SKIN, \
    KARAMBIT_WARRIOR, RATTAN_ARCHER, THIRISADAI, \
    CONDOTTIERO, KONNIK, BOYAR, CAMEL_ARCHER, \
    KIPCHAK, URUMI_SWORDSMAN, RATHA, \
    CHAKRAM_THROWER, COMPOSITE_BOWMAN, \
    MONASPA, IRON_PAGODA, LIAO_DAO, \
    FEITORIA, DONJON, KREPOST, HARBOR, FOLWARK1, FOLWARK3, MILL_AGE2, MILL_AGE3, MILL_AGE4, \
    DOCK_AGE2, DOCK_AGE3, DOCK_AGE4, TYPE_DOCK_TRAIN_LOCATION

# The idea behind this mod, in the spirit of the earlier `regionalAdditions` branch:
# give civs units/buildings they plausibly would have fielded historically, focused on
# regional identity rather than balance. Every grant below cites the community
# discussion it's drawn from. New units become trainable once a civ has built a
# Castle (or, for early economic helpers, a Town Center) - no manual research click
# needed, the same mechanism the game itself uses to unlock hero units.

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
    # Vietnamese is the one mainland Southeast Asian elephant civ that didn't
    # have this already - also doubles as their thank-you for Rattan Archer (a
    # Vietnamese native unique unit) no longer being exclusive to them, now
    # that Malay has it too.
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
    # legions long after the west fell; Legionary is currently Roman-only.
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
    civs = ['Malians', 'Romans']
    for civ_id in civ_ids_named(data, civs):
        upgrade_unit_for_civ(data, civ_id, SKIRMISHER, IMPERIAL_SKIRMISHER, TECH_REQUIREMENT_IMPERIAL_AGE)
        upgrade_unit_for_civ(data, civ_id, ELITE_SKIRMISHER, IMPERIAL_SKIRMISHER, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_war_elephants_to_ethiopians(data: DatFile):
    # War Elephant is Persians' real native unique unit (civilizations.json).
    # https://forums.ageofempires.com/t/should-ethiopians-get-war-elephants/202217/12
    for civ_id in civ_ids_named(data, ['Ethiopians']):
        enable_unit_for_civ(data, civ_id, WAR_ELEPHANT, TECH_CASTLE_BUILT)
        # Deliberately no Elite tier - Persians keep the more complete version of
        # their own unique unit, matching the principle that a unique unit given
        # to a second civ should still stay a notch behind the original owner.
        # War Elephant's vanilla Castle button (1) is the universal unique-unit
        # slot - Ethiopians' own Shotel Warrior already lives there. Move to
        # button 4, confirmed unused by any Ethiopian content.
        set_train_button_for_civ(data, civ_id, WAR_ELEPHANT, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_conquistadors_to_portuguese(data: DatFile):
    # Portugal ran its own conquistador-style expeditions in the Americas and Africa;
    # Conquistador is Spanish's real native unique unit (civilizations.json).
    # https://www.reddit.com/r/aoe2/comments/snpt20/how_unbalanced_would_making_the_conq_a_regional/
    for civ_id in civ_ids_named(data, ['Portuguese']):
        enable_unit_for_civ(data, civ_id, CONQUISTADOR, TECH_CASTLE_BUILT)
        # No Elite tier - keeps Spanish's own version the more complete one.
        # Conquistador's vanilla Castle button (1) is the universal unique-unit
        # slot - Portugal's own Organ Gun already lives there. Move to button 4.
        set_train_button_for_civ(data, civ_id, CONQUISTADOR, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_missionaries_to_civs_with_missionary_heritage(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/ka4jvi/why_dont_portuguese_have_access_to_missionaries/
    civs = ['Italians', 'Portuguese', 'Byzantine']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, MISSIONARY, TECH_CASTLE_BUILT)


def give_warrior_priests_to_civs_with_shamanic_heritage(data: DatFile):
    # https://www.reddit.com/r/aoe2/comments/17egkrm/for_fun_what_if_the_new_warrior_priest_from/
    civs = ['Vikings', 'Celts', 'Aztecs', 'Dravidians', 'Malians', 'Teutons', 'Japanese', 'Chinese']
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


def give_centurions_to_byzantines(data: DatFile):
    # Rome fields two separate unique units: Legionary (already given to
    # Byzantines above) and Centurion, a standalone Castle-trained unit, not an
    # upgrade of the sword-infantry line. Byzantium inherited the whole legion
    # system from Rome, not just half of it. Centurion is Romans' real native
    # unique unit though, so no Elite tier here - Rome keeps the fuller version.
    for civ_id in civ_ids_named(data, ['Byzantine']):
        enable_unit_for_civ(data, civ_id, CENTURION, TECH_CASTLE_BUILT)
        # Centurion's vanilla Castle button (1) is the universal unique-unit slot;
        # move to button 4, same fix as Conquistador/War Elephant above.
        set_train_button_for_civ(data, civ_id, CENTURION, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_franks_a_frankish_paladin_skin(data: DatFile):
    # Persians already do exactly this: Savar is a cosmetic swap-in for Paladin,
    # not a new unit with new stats. Franks' Paladin (already their civ bonus -
    # cheaper, no Blacksmith upgrades needed) gets the same treatment: same
    # name, same stats, same upgrade path, different look. Purely visual -
    # doesn't touch balance at all.
    for civ_id in civ_ids_named(data, ['French']):
        reskin_unit_for_civ(data, civ_id, PALADIN, FRANKISH_PALADIN_SKIN)


def give_teutons_a_crusader_knight_skin(data: DatFile):
    # Same idea for the Teutonic Order's own Paladins - the Teutons already have
    # a separate, real "Teutonic Knight" unique unit (infantry), so this isn't a
    # duplicate of that; it's their mounted knights visually matching the
    # crusading-Order identity their whole civ is built around.
    for civ_id in civ_ids_named(data, ['Teutons']):
        reskin_unit_for_civ(data, civ_id, PALADIN, CRUSADER_KNIGHT_SKIN)


def give_karambit_warriors_to_other_southeast_asian_civs(data: DatFile):
    # Karambit Warrior is currently Malay-only. Khmer and Vietnamese are the
    # same Southeast Asian world already tied together by the Elephant Archer/
    # Armored Elephant/Battle Elephant grants above.
    # No Elite tier - Malay keeps the fuller version of their own unique unit.
    for civ_id in civ_ids_named(data, ['Khmer', 'Vietnamese']):
        enable_unit_for_civ(data, civ_id, KARAMBIT_WARRIOR, TECH_CASTLE_BUILT)
        # Vanilla Castle button 1 is the universal unique-unit slot - both civs'
        # own native unique already lives there.
        set_train_button_for_civ(data, civ_id, KARAMBIT_WARRIOR, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_rattan_archers_to_malay(data: DatFile):
    # Malay's own Karambit Warrior is no longer exclusive (see above) - Rattan
    # Archer (Vietnamese's real native unique, not Burmese's as originally
    # thought - verified against civilizations.json) is the natural thing to
    # trade back the other way in the same regional group.
    # No Elite tier - Vietnamese keeps the fuller version of their own unique.
    for civ_id in civ_ids_named(data, ['Malay']):
        enable_unit_for_civ(data, civ_id, RATTAN_ARCHER, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, RATTAN_ARCHER, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_thirisadai_to_other_indian_ocean_civs(data: DatFile):
    # Thirisadai (a Dravidian warship) fits the same Indian Ocean/Bay of Bengal
    # naval tradition Bengalis and Gurjaras already share culturally. No elite
    # tier exists in the game to extend. Low risk - it's a ship, not a
    # land-army staple.
    for civ_id in civ_ids_named(data, ['Bengalis', 'Gurjaras']):
        enable_unit_for_civ(data, civ_id, THIRISADAI, TECH_CASTLE_BUILT)


def give_condottiero_to_sicilians(data: DatFile):
    # Sicily's Mediterranean mercenary-captain tradition overlaps heavily with
    # Italy's - Sicilians already get Genitour in this mod on the same
    # "Mediterranean multicultural contact" logic. No elite tier exists.
    for civ_id in civ_ids_named(data, ['Sicilians']):
        enable_unit_for_civ(data, civ_id, CONDOTTIERO, TECH_CASTLE_BUILT)


def give_konnik_and_boyar_to_each_other(data: DatFile):
    # Konnik is actually Bulgarians' own native unique unit (not Slavs', as
    # originally thought - verified against civilizations.json), and Boyar is
    # Slavs' own native unique. Both are heavy Orthodox-Slavic cavalry from the
    # same shared heritage, so rather than a one-way grant, trade them: Slavs
    # get access to Konnik too, Bulgarians get access to Boyar too. Neither side
    # gets the Elite tier of the borrowed unit - each civ's own version stays
    # the more complete one.
    for civ_id in civ_ids_named(data, ['Slavs']):
        enable_unit_for_civ(data, civ_id, KONNIK, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, KONNIK, TYPE_CASTLE_TRAIN_LOCATION, 4)
    for civ_id in civ_ids_named(data, ['Bulgarians']):
        enable_unit_for_civ(data, civ_id, BOYAR, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, BOYAR, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_camel_archers_to_other_camel_civs(data: DatFile):
    # Camel Archer is currently Berber-only. Saracens, Turks, Cumans, and Huns
    # are the same "true camel civs" this mod already built out (camel line,
    # camel scout, imperial camel). Gated to Imperial Age only, unlike Berbers'
    # own Castle-Age access, so it stays a late-game bonus option for these four
    # rather than diluting what makes it special for Berbers specifically.
    # No Elite tier either, on top of the Imperial-Age gate - Berbers keep both
    # the earlier access and the more complete version of their own unique.
    civs = ['Saracens', 'Turks', 'Cumans', 'Huns']
    for civ_id in civ_ids_named(data, civs):
        enable_unit_for_civ(data, civ_id, CAMEL_ARCHER, TECH_REQUIREMENT_IMPERIAL_AGE)
        set_train_button_for_civ(data, civ_id, CAMEL_ARCHER, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_kipchak_to_tatars(data: DatFile):
    # Kipchak (Cumans' own unique) fits the Tatars just as well - the Cuman-
    # Kipchak confederation and the Golden Horde/Tatars are one continuous
    # steppe people. No reciprocal grant back to Cumans here - Cumans are
    # already the most heavily-served civ in this mod (camel line, camel
    # scout, imperial camel, winged hussar, camel archer), so this one is
    # one-way rather than forcing a trade that isn't needed.
    # No Elite tier - Cumans keep the fuller version of their own unique unit.
    for civ_id in civ_ids_named(data, ['Tatars']):
        enable_unit_for_civ(data, civ_id, KIPCHAK, TECH_CASTLE_BUILT)
        # Tatars already have Camel Archer at Castle button 4 from this mod -
        # button 5 is confirmed free (nothing native uses Castle buttons 5+).
        set_train_button_for_civ(data, civ_id, KIPCHAK, TYPE_CASTLE_TRAIN_LOCATION, 5)


def give_urumi_swordsman_to_hindustanis(data: DatFile):
    # Urumi Swordsman is Dravidians' real primary unique unit (a flexible South
    # Indian sword) - Hindustanis are the broader Indian-subcontinent civ in
    # this mod that hasn't received a true-unique-unit grant yet.
    # No Elite tier - Dravidians keep the fuller version of their own unique.
    for civ_id in civ_ids_named(data, ['Hindustanis']):
        enable_unit_for_civ(data, civ_id, URUMI_SWORDSMAN, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, URUMI_SWORDSMAN, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_ratha_and_chakram_to_each_other(data: DatFile):
    # Ratha (Bengalis' unique war chariot) and Chakram Thrower (Gurjaras'
    # unique disc-thrower) are both Indian-subcontinent regional neighbors
    # already sharing Thirisadai from this mod - trade their land uniques too.
    # Neither side gets the Elite tier of the borrowed unit.
    for civ_id in civ_ids_named(data, ['Bengalis']):
        enable_unit_for_civ(data, civ_id, CHAKRAM_THROWER, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, CHAKRAM_THROWER, TYPE_CASTLE_TRAIN_LOCATION, 4)
    for civ_id in civ_ids_named(data, ['Gurjaras']):
        enable_unit_for_civ(data, civ_id, RATHA, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, RATHA, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_composite_bowman_and_monaspa_to_each_other(data: DatFile):
    # Composite Bowman (Armenians) and Monaspa (Georgians) are both Caucasus
    # neighbors with deeply intertwined history - trade their uniques the same
    # way Konnik/Boyar were traded between Bulgarians and Slavs.
    # Neither side gets the Elite tier of the borrowed unit.
    for civ_id in civ_ids_named(data, ['Armenians']):
        enable_unit_for_civ(data, civ_id, MONASPA, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, MONASPA, TYPE_CASTLE_TRAIN_LOCATION, 4)
    for civ_id in civ_ids_named(data, ['Georgians']):
        enable_unit_for_civ(data, civ_id, COMPOSITE_BOWMAN, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, COMPOSITE_BOWMAN, TYPE_CASTLE_TRAIN_LOCATION, 4)


def give_iron_pagoda_and_liao_dao_to_each_other(data: DatFile):
    # Iron Pagoda (Jurchens) and Liao Dao (Khitans) are the two Liao/Jin-era
    # Manchurian rival-then-successor states - same trade pattern again.
    # Neither side gets the Elite tier of the borrowed unit.
    for civ_id in civ_ids_named(data, ['Jurchens']):
        enable_unit_for_civ(data, civ_id, LIAO_DAO, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, LIAO_DAO, TYPE_CASTLE_TRAIN_LOCATION, 4)
    for civ_id in civ_ids_named(data, ['Khitans']):
        enable_unit_for_civ(data, civ_id, IRON_PAGODA, TECH_CASTLE_BUILT)
        set_train_button_for_civ(data, civ_id, IRON_PAGODA, TYPE_CASTLE_TRAIN_LOCATION, 4)


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
    for civ_id in civ_ids_named(data, ['Bohemians']):
        for mill_tier in (MILL, MILL_AGE2, MILL_AGE3, MILL_AGE4):
            upgrade_unit_for_civ(data, civ_id, mill_tier, FOLWARK1, TECH_CASTLE_BUILT)
        # Skip the intermediate tier, same simplification used everywhere else
        # in this file - straight to the final tier once Imperial is reached.
        upgrade_unit_for_civ(data, civ_id, FOLWARK1, FOLWARK3, TECH_REQUIREMENT_IMPERIAL_AGE)


def give_donjon_to_italians(data: DatFile):
    # Donjon (Sicily's cheap mini-Castle that also trains Serjeants) fits
    # Italians just as well - same Mediterranean peninsula, already sharing
    # Genitour with Sicilians in this mod.
    for civ_id in civ_ids_named(data, ['Italians']):
        enable_unit_for_civ(data, civ_id, DONJON, TECH_CASTLE_BUILT)


def give_krepost_to_slavs(data: DatFile):
    # Krepost (Bulgaria's defensive tower that also trains Konnik) fits Slavs
    # just as well - the same Orthodox Balkan-Slavic connection already behind
    # the Konnik/Boyar trade between these two civs.
    for civ_id in civ_ids_named(data, ['Slavs']):
        enable_unit_for_civ(data, civ_id, KREPOST, TECH_CASTLE_BUILT)


def give_harbor_to_vietnamese(data: DatFile):
    # Harbor (Malay's unique Dock upgrade) fits Vietnamese just as well - the
    # same coastal Southeast Asian maritime-trade economy already tying
    # Vietnamese to Malay/Khmer/Burmese throughout this mod.
    for civ_id in civ_ids_named(data, ['Vietnamese']):
        for dock_tier in (TYPE_DOCK_TRAIN_LOCATION, DOCK_AGE2, DOCK_AGE3, DOCK_AGE4):
            upgrade_unit_for_civ(data, civ_id, dock_tier, HARBOR, TECH_REQUIREMENT_IMPERIAL_AGE)


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
    give_war_elephants_to_ethiopians(data)
    give_conquistadors_to_portuguese(data)
    give_missionaries_to_civs_with_missionary_heritage(data)
    give_warrior_priests_to_civs_with_shamanic_heritage(data)
    give_settlements_to_mesoamerican_and_andean_civs(data)
    give_fire_lancers_to_japanese(data)
    give_camel_scout_start_to_true_camel_civs(data)
    give_centurions_to_byzantines(data)
    give_franks_a_frankish_paladin_skin(data)
    give_teutons_a_crusader_knight_skin(data)
    give_karambit_warriors_to_other_southeast_asian_civs(data)
    give_rattan_archers_to_malay(data)
    give_thirisadai_to_other_indian_ocean_civs(data)
    give_condottiero_to_sicilians(data)
    give_konnik_and_boyar_to_each_other(data)
    give_camel_archers_to_other_camel_civs(data)
    give_kipchak_to_tatars(data)
    give_urumi_swordsman_to_hindustanis(data)
    give_ratha_and_chakram_to_each_other(data)
    give_composite_bowman_and_monaspa_to_each_other(data)
    give_iron_pagoda_and_liao_dao_to_each_other(data)
    give_feitoria_to_spanish(data)
    give_folwark_to_bohemians(data)
    give_donjon_to_italians(data)
    give_krepost_to_slavs(data)
    give_harbor_to_vietnamese(data)
