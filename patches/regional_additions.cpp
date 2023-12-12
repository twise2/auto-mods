#include "regional_additions.h"
#include <set>
#include "genie/dat/DatFile.h"
#include "ids.h"

//The idea to this mod is not to affect anything gameplay/balance wise 
//but only to give civs access to technology / units they would have had
//access to historically, take away things they would not have, and provide
//more of a regional identity to more of the civs. The premise behind the mod
//is to do things like the following
//
//Give new features to civs that should have them. For example, nomadic civs having
//trade cart access.
//
//Differentiate steppe and non-steppe civs to give a regional feel to those units
//
//Grant gunpowder to Chinese as they were on of the first to utilize it
//
//Grant Caravanseri to civs that had it.
//
//etc....

void configureRegionalAdditions(genie::DatFile *df) {
    std::set<int> villagers = {
        ID_FISHING_SHIP,        ID_TRADE_COG,           ID_TRADE_CART_EMPTY,   ID_TRADE_CART_FULL,
        ID_VILLAGER_BASE_M,     ID_VILLAGER_BASE_F,     ID_VILLAGER_FARMER_M,  ID_VILLAGER_FARMER_F,
        ID_VILLAGER_SHEPHERD_M, ID_VILLAGER_SHEPHERD_F, ID_VILLAGER_FORAGER_M, ID_VILLAGER_FORAGER_F,
        ID_VILLAGER_HUNTER_M,   ID_VILLAGER_HUNTER_F,   ID_VILLAGER_FISHER_M,  ID_VILLAGER_FISHER_F,
        ID_VILLAGER_WOOD_M,     ID_VILLAGER_WOOD_F,     ID_VILLAGER_GOLD_M,    ID_VILLAGER_GOLD_F,
        ID_VILLAGER_STONE_M,    ID_VILLAGER_STONE_F,    ID_VILLAGER_BUILDER_M, ID_VILLAGER_BUILDER_F,
        ID_VILLAGER_REPAIRER_M, ID_VILLAGER_REPAIRER_F,
    };

    for (genie::Civ &civ : df->Civs) {
        for (int villager_id : villagers) {
            civ.Units.at(villager_id).DeadUnitID = ID_SABOTEUR;
            std::cout << "Patched Villager unit " << villager_id << " for civ " << civ.Name << "\n";
        }
        std::cout << "Patched Saboteur unit for civ " << civ.Name << "\n";
    }
}
