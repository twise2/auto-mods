import logging

from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost
from genieutils.unit import ResourceCost, ResourceStorage

from mods.ids import WATCH_TOWER, GUARD_TOWER, KEEP, BOMBARD_TOWER, TYPE_POPULATION_HEADROOM, \
    TYPE_CURRENT_POPULATION, TYPE_TOTAL_UNITS_OWNED, TECH_CARAVAN, TYPE_FOOD, TYPE_GOLD

NAME = 'community-games-custom'


def add_population_cost_to_all_towers(data: DatFile):
    logging.info('Adding 1 population cost to all towers (Watch/Guard/Keep/Bombard) of all civs')
    for civ in data.civs:
        for tower_id in (WATCH_TOWER, GUARD_TOWER, KEEP, BOMBARD_TOWER):
            tower = civ.units[tower_id]
            tower.creatable.resource_costs = (
                tower.creatable.resource_costs[0],
                tower.creatable.resource_costs[1],
                ResourceCost(type=TYPE_POPULATION_HEADROOM, amount=1, flag=0),
            )
            tower.resource_storages = (
                ResourceStorage(type=TYPE_POPULATION_HEADROOM, amount=-1, flag=2),
                ResourceStorage(type=TYPE_CURRENT_POPULATION, amount=1, flag=2),
                ResourceStorage(type=TYPE_TOTAL_UNITS_OWNED, amount=1, flag=1),
            )


def modify_caravan_cost(data: DatFile, food: int, gold: int):
    caravan = data.techs[TECH_CARAVAN]
    caravan.resource_costs = (
        ResearchResourceCost(type=TYPE_FOOD, amount=food, flag=1),
        ResearchResourceCost(type=TYPE_GOLD, amount=gold, flag=1),
        caravan.resource_costs[2],
    )


def mod(data: DatFile):
    add_population_cost_to_all_towers(data)
    modify_caravan_cost(data, 800, 200)
