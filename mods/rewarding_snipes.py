import logging

from genieutils.civ import Civ
from genieutils.datfile import DatFile

from mods.ids import KING, RELIC_CART, EMPEROR_IN_A_LITTER, TYPE_POPULATION_HEADROOM, TYPE_GIVE_AND_TAKE, \
    TYPE_BONUS_POPULATION_CAP
from mods.util import clone

NAME = 'rewarding-snipes'


def clone_and_patch_relic_cart(civ: Civ, version: str):
    clone_unit_id = len(civ.units)
    cloned_unit = clone(civ.units[RELIC_CART], version)
    cloned_unit.id = clone_unit_id
    cloned_unit.fog_visibility = 1  # always visible
    cloned_unit.hit_points = 30_000  # don't die from exploding kings

    # Cosmetic: look like a king's own palanquin instead of a plain supply
    # cart. EMPERORLITTER (real unit 1988) only has a standing + walking
    # graphic in the real data (no dying/undead/attack frames) - the stock
    # Relic Cart doesn't have those either (confirmed: dying=-1, undead=-1),
    # so nothing is lost by only copying what the donor actually has.
    donor = civ.units[EMPEROR_IN_A_LITTER]
    cloned_unit.standing_graphic = donor.standing_graphic
    if cloned_unit.dead_fish is not None and donor.dead_fish is not None:
        cloned_unit.dead_fish.walking_graphic = donor.dead_fish.walking_graphic
        cloned_unit.dead_fish.running_graphic = donor.dead_fish.running_graphic

    # act like a house that gives (and takes) 50 pop space
    cloned_unit.resource_storages[0].type = TYPE_POPULATION_HEADROOM
    cloned_unit.resource_storages[0].amount = 50
    cloned_unit.resource_storages[0].flag = TYPE_GIVE_AND_TAKE

    # grant 50 bonus pop cap while controlled
    cloned_unit.resource_storages[1].type = TYPE_BONUS_POPULATION_CAP
    cloned_unit.resource_storages[1].amount = 50
    cloned_unit.resource_storages[1].flag = TYPE_GIVE_AND_TAKE

    logging.info(f'Cloned unit {clone_unit_id} ({cloned_unit.name}) for civ {civ.name}')
    civ.units.append(cloned_unit)
    return clone_unit_id


def patch_kings(data: DatFile):
    for civ in data.civs:
        relic_cart_id = clone_and_patch_relic_cart(civ, data.version)
        king = civ.units[KING]
        king.blood_unit_id = relic_cart_id  # use blood unit so it does not conflict with exploding kings
        logging.info(f'Patched king blood unit for civ {civ.name}')


def mod(data: DatFile):
    patch_kings(data)
