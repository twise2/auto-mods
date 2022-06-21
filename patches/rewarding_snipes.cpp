#include "rewarding_snipes.h"
#include "genie/dat/DatFile.h"
#include "ids.h"

void configureRewardingSnipes(genie::DatFile *df) {
    for (genie::Civ &civ : df->Civs) {
        genie::Unit &king = civ.Units.at(ID_KING);
        king.BloodUnitID = ID_RELIC_CART; // use blood unit so it does not conflict with exploding kings
        std::cout << "Patched King blood unit for civ " << civ.Name << "\n";

        genie::Unit &relicCart = civ.Units.at(ID_RELIC_CART);
        relicCart.FogVisibility = 1; //always visible
        relicCart.HitPoints = 30000; //don't die from exploding kings
        relicCart.ResourceStorages.at(0).Type = TYPE_POPULATION_HEADROOM;
        relicCart.ResourceStorages.at(0).Amount = 50;
        relicCart.ResourceStorages.at(0).Flag = TYPE_GIVE_AND_TAKE;
        std::cout << "Patched Relic Cart for civ " << civ.Name << "\n";
    }
}
