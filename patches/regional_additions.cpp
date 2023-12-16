#include "regional_additions.h"
#include <set>
#include "genie/dat/DatFile.h"
#include "ids.h"

//The idea to this mod is not to affect anything gameplay/balance wise 
//but only to give civs access to technology / units they would have had
//access to historically, and provide more of a regional identity to more of the civs. 
//The premise behind the mod is the following

// 1. Give civs access to new elements they likely would have had if released today 
// 2. Stay historically accurate to the extent possible 
// 3. Focus on giving factions/regions more of an identity/uniqueness
// 4. Try to be additive (devs give trebs to civs without them for a reason)
// 5. If balance occurs, generally err on buffing instead of nerfing
//


int16_t getVectorAtIndex(std::vector<int16_t> vec, int16_t index, int16_t defaultValue = -1){
    if(vec.size() <= index){
        return defaultValue;
    }
    return vec.at(index);
}

void updateUnitSkins(genie::DatFile *df, std::vector<int> civIds, int16_t unitId, int16_t replacementGraphicUnitId, bool copyIcon=false, bool copyName=false ) {
    for (int16_t civId : civIds) {
        //get the civ and skins we want
        genie::Civ &chosenCiv = df->Civs.at(civId);
        genie::Unit &unitToUpdate = chosenCiv.Units.at(unitId);
        genie::Unit unitWhosSkinWeWant = chosenCiv.Units.at(replacementGraphicUnitId);
        //update it from old to new
        if(copyIcon == true){
            unitToUpdate.IconID = unitWhosSkinWeWant.IconID;
        }
        if(copyName == true){
            unitToUpdate.LanguageDLLName = unitWhosSkinWeWant.LanguageDLLName;
        }
        unitToUpdate.StandingGraphic = unitWhosSkinWeWant.StandingGraphic;
        unitToUpdate.DyingGraphic = unitWhosSkinWeWant.DyingGraphic;
        unitToUpdate.UndeadGraphic = unitWhosSkinWeWant.UndeadGraphic;
        unitToUpdate.DamageGraphics = unitWhosSkinWeWant.DamageGraphics;
        unitToUpdate.DeadFish.WalkingGraphic = unitWhosSkinWeWant.DeadFish.WalkingGraphic;
        unitToUpdate.DeadFish.RunningGraphic = unitWhosSkinWeWant.DeadFish.RunningGraphic;
        unitToUpdate.Type50.AttackGraphic = unitWhosSkinWeWant.Type50.AttackGraphic;


        std::cout << "Gave Skin '" << unitWhosSkinWeWant.Name << "' to unit '" << unitToUpdate.Name << "' for Civ '" << chosenCiv.Name << "'" << std::endl; 
    }
}

std::vector<int16_t> duplicateTechToNewCiv(genie::DatFile *df, int techId, int civId, std::vector<int16_t> feedForwardTechIds = {-1,-1}, int buttonOverride = -1) {
        //instantiate log and some id information
        std::string lastPositionString = "";
        int16_t newTechPosition = getVectorAtIndex(feedForwardTechIds, 0);
        int16_t originalTechId = getVectorAtIndex(feedForwardTechIds, 1);
        //turn off full tech mode as that will break with this anyway
        genie::Tech tech = df->Techs.at(techId);
        std::cout << "Added Tech '" << tech.Name << "' to civ id '" << df->Civs.at(civId).Name << "'" << lastPositionString; 
        tech.Civ = civId;
        tech.FullTechMode = 0;         
        if (buttonOverride >= 0) {
            tech.ButtonID = buttonOverride;         
            std::cout << ": Button overriden to " << buttonOverride;
        }

        //if tech references the last duplicated tech directly, move the new requirement
        auto requiredTechs = tech.RequiredTechs;
        auto it = find(requiredTechs.begin(), requiredTechs.end(), originalTechId);
        if(originalTechId > 0 && it != requiredTechs.end() ){
            int16_t foundIndex = it-requiredTechs.begin();
            tech.RequiredTechs.at(foundIndex) = newTechPosition;
            //reset added tech if the current tech needs to point at old tech
            std::cout << ": moved research requirement position from " << originalTechId << " to " << newTechPosition;
        }
        else { 
            //if no original tech found, set to new value 
            originalTechId = techId;
        };

        std::cout << std::endl;
        //push here, but logging looks better above so it is all consitent
        df->Techs.push_back(tech);
        newTechPosition = (df->Techs.size() -1);
        std::vector<int16_t> res{newTechPosition, originalTechId};
        return res;
};

void addExtraUniqueUnitToCiv(genie::DatFile *df, int civId, int16_t unitId, int enablementTechid){
    genie::Civ &chosenCiv = df->Civs.at(civId);
    genie::Unit &duplicateUnit = chosenCiv.Units.at(unitId);
    duplicateUnit.Creatable.ButtonID = 4; //after petard so it doesnt block things
    duplicateTechToNewCiv(df, enablementTechid, civId);
    std::cout << "Added Unique Unit '" << duplicateUnit.Name << "' to civ '" << chosenCiv.Name << std::endl; 
}

void SwapSamuraiUnitToRanged(genie::DatFile *df, int16_t SAMURAI_UNIT_ID, int16_t UNIT_TO_SWAP_TO, int16_t LANGFILE) {
    for (genie::Civ &civ : df->Civs) {

        //use archer fo the eye for samuraiUnit swap
        genie::Unit &samuraiUnit = civ.Units.at(SAMURAI_UNIT_ID);
        samuraiUnit.Nothing = UNIT_TO_SWAP_TO;
        samuraiUnit.Trait = samuraiUnit.Trait | 8;

        //make archer of the eye bad except against unique units
        genie::Unit &samuraiUnitArcher = civ.Units.at(UNIT_TO_SWAP_TO);
        samuraiUnitArcher.Nothing = SAMURAI;
        samuraiUnitArcher.IconID = samuraiUnit.IconID;
        samuraiUnitArcher.Trait = samuraiUnitArcher.Trait | 8;

        samuraiUnitArcher.Name = "Samurai (ranged)";
        samuraiUnitArcher.LanguageDLLName = LANGFILE;
        //df->Langfile.setString(LANGFILE_ENGLISH_ARCHER_OF_THE_EYES, "Samurai (Ranged)").
        samuraiUnitArcher.Creatable.HeroGlowGraphic = -1;
        samuraiUnitArcher.Creatable.HeroMode = 0;
        //make sure its weaker in archer form but make it the same otherwise
        samuraiUnitArcher.HitPoints = samuraiUnit.HitPoints; //keep it's HP in line
        samuraiUnitArcher.Type50.Armours = samuraiUnit.Type50.Armours; //make it same as samurai
        samuraiUnitArcher.Type50.BaseArmor = samuraiUnit.Type50.BaseArmor; //dont give armor bonuses
        samuraiUnitArcher.Type50.DisplayedMeleeArmour = samuraiUnit.Type50.DisplayedMeleeArmour; //dont give armor bonuses
        samuraiUnitArcher.Creatable.DisplayedPierceArmour = samuraiUnit.Creatable.DisplayedPierceArmour; //dont give armor bonuses
        //make sure it's ranged mode is only good against unique units
        samuraiUnitArcher.Type50.DisplayedAttack = 1;

        //
        samuraiUnitArcher.Type50.DisplayedRange = 5; //same as arbalest 
        samuraiUnitArcher.Type50.MaxRange = 4; //same as arbalest
        //super slow but heavy hitting to encourage shoot once than swap
        samuraiUnitArcher.Type50.ReloadTime = 5;
        samuraiUnitArcher.Type50.DisplayedReloadTime = 5;
        //archer of the eye and lhunhan chu have 2 attacks, unlikely to change so can just edit them
        samuraiUnitArcher.Type50.Attacks.at(0).Amount = 1;
        samuraiUnitArcher.Type50.Attacks.at(1).Amount = 30;
        samuraiUnitArcher.Type50.Attacks.at(1).Class = ATTACK_TYPE_HERO_BONUS_DAMAGE;
        //slow them down for good measure to decrease odds of staying in this form
        samuraiUnitArcher.Speed = .8;
    }
    std::cout << "Added Ability 'Samurai can swap to Ranged Mode'" << std::endl;
}

void allowSamuraiToSwapToArcherMode(genie::DatFile *df) {
    SwapSamuraiUnitToRanged(df, SAMURAI, ARCHER_OF_THE_EYES, LANGFILE_ENGLISH_SAMURAI);
    SwapSamuraiUnitToRanged(df, ELITE_SAMURAI, LUU_NHAN_CHU, LANGFILE_ENGLISH_SAMURAI_ELITE);
}

int16_t addTechnologiesToCivs(genie::DatFile *df, std::vector<int16_t> civIds, std::vector<std::vector<int16_t>> techSetters){
    std::vector<int16_t> feedForwardTechIds{-1,-1};
    for (int16_t civId : civIds) {
        for (std::vector<int16_t> techSetter : techSetters) {
            //this should probably be done better, but works for now and we
            //names nicelyish? idk, probably make it map<string,int> it
            //and check if tech.String (exists) then set to int but i'm lazy
            int16_t techId = getVectorAtIndex(techSetter, 0);
            int16_t buttonOverride = getVectorAtIndex(techSetter, 1);
            feedForwardTechIds = duplicateTechToNewCiv(df, techId, civId, feedForwardTechIds, buttonOverride);
        }
    };
    int16_t finalNewTechnologyId =  getVectorAtIndex(feedForwardTechIds, 0);
    return finalNewTechnologyId;
};

void addGenitourToCivs(genie::DatFile *df, std::vector<int16_t> civIds){
    int16_t addedGenitourtechId = -1;
    for (int16_t civId : civIds) {
        addedGenitourtechId = addTechnologiesToCivs(df, {civId}, {{TECH_GENITOUR_MAKE_AVAILABLE}});
        genie::Tech &newlyAddedGenitourTech = df->Techs.at(addedGenitourtechId);
        newlyAddedGenitourTech.ResourceCosts.at(0).Amount = 0;
        newlyAddedGenitourTech.ResearchTime = 0;
        std::cout << "  Genitour at tech id " << addedGenitourtechId << " updated cost";
    }
}

void makeLongboatsTransports(genie::DatFile *df) {
    //allow viking longboats to transport 5 units
    //https://www.google.com/search?q=longboats+should+transport+aoe2&rlz=1C5CHFA_enUS906US906&oq=longboats+should+transport+aoe2&gs_lcrp=EgZjaHJvbWUyCQgAEEUYORigATIHCAEQIRigAdIBCDQyOTBqMGo5qAIAsAIA&sourceid=chrome&ie=UTF-8
    for (genie::Civ &civ : df->Civs) {
        genie::Unit &longboat = civ.Units.at(LONGBOAT);
        genie::Unit &eliteLongboat = civ.Units.at(ELITE_LONGBOAT);
        longboat.GarrisonCapacity = 5;
        eliteLongboat.GarrisonCapacity = 5;
        longboat.Class = CLASS_TRANSPORT_BOAT;
        eliteLongboat.Class = CLASS_TRANSPORT_BOAT;
        longboat.Trait = 3;
        eliteLongboat.Trait = 3;
        auto unloadTask = new genie::Task();
        unloadTask->ActionType = ACTION_TYPE_UNLOAD;
        longboat.Bird.TaskList.push_back(*unloadTask);
        eliteLongboat.Bird.TaskList.push_back(*unloadTask);
    }
    std::cout << "Added Ability 'Longboats act as Transports'" << std::endl;
}

void giveHistoricRegionalVarietyToCivs(genie::DatFile *df) {
    //Add Mulecarts to the nomadic civs for that flavor
    //https://www.reddit.com/r/aoe2/comments/17stxfy/should_all_nomad_civs_be_given_mule_carts/
    addTechnologiesToCivs(df, {
                CIV_MONGOLS,
                CIV_HUNS,
                CIV_TATARS,
                CIV_CUMANS,
                CIV_MAGYARS
            }, {
                {TECH_MULECART_MAKE_AVAILABLE, -1}
            } 
    );
    //add bombard and hand cannon to the civ that created it 
    //https://forums.ageofempires.com/t/chinese-civilization/73726
    addTechnologiesToCivs(df, {
                CIV_CHINESE,
            }, {
               {TECH_HAND_CANNON, -1}
            } 
    );
    //add caravanseri to silk road civs 
    //https://www.reddit.com/r/aoe2/comments/10a3jg9/historically_persian_should_also_have_access_to/
    addTechnologiesToCivs(df, {
                CIV_SARACENS,
                CIV_CHINESE,
                CIV_MONGOLS,
                CIV_TURKS,
                CIV_TATARS
            }, {
               {TECH_CARAVANSERI_MAKE_AVAILABLE, -1}
            } 
    );
    //add elephaunt archers to civs that had them historically
    //https://www.reddit.com/r/aoe2/comments/10mqm64/sotl_should_more_civs_get_elephant_archers/
    addTechnologiesToCivs(df, {
                CIV_PERSIANS,
                CIV_BURMESE,
                CIV_MALAY,
                CIV_KHMER,
                CIV_VIETNAMESE
            }, {
                {TECH_ELEPHANT_ARCHER_MAKE_AVAILABLE, -1},
                {TECH_MOVE_ELEPHANT_ARCHER, -1}
            } 
    );
    //give armoured elephaunts to elephant civs 
    //https://www.reddit.com/r/aoe2/comments/ubkjoa/armored_elephants_for_khmer_burmese_and_malay
    addTechnologiesToCivs(df, {
                CIV_KHMER,
                CIV_BURMESE,
                CIV_BURMESE,
                CIV_MALAY,
                CIV_ETHIOPIANS
            }, {
            {TECH_ARMORED_ELEPHANT_MAKE_AVAILABLE, -1},
            {TECH_MOVE_ARMORED_ELEPHANT, -1},
            {TECH_SIEGE_ELEPHANT, 12}
    });
    //add steppe lancers to civs that should probably have them
    //https://www.reddit.com/r/aoe2/comments/10mqm64/sotl_should_more_civs_get_elephant_archers/
    //https://www.reddit.com/r/aoe2/comments/y6b17r/disproportionate_spread_of_regional_units/
    addTechnologiesToCivs(df, {
                CIV_CHINESE,
                CIV_BULGARIANS,
                CIV_LITHUANIANS, 
                CIV_HINDUSTANIS, 
                CIV_MAGYARS,
                CIV_SLAVS,
                CIV_PERSIANS
            }, {
                {TECH_STEPPE_LANCER_MAKE_AVAILABLE, -1}
    });
    addTechnologiesToCivs(df, {
                CIV_HUNS,
                CIV_TURKS
            }, {
                {TECH_STEPPE_LANCER_MAKE_AVAILABLE, -1},
                {TECH_ELITE_STEPPE_LANCER_MAKE_AVAILABLE, -1}
    });
    //disable paladin for pure cumans and give heavy camel
    //https://forums.ageofempires.com/t/give-cumans-heavy-camel-riders-and-remove-paladins-and-maybe-chevaliers/196455
    //https://www.reddit.com/r/aoe2/comments/y6b17r/disproportionate_spread_of_regional_units/
    addTechnologiesToCivs(df, {
                CIV_CUMANS,
                CIV_HUNS
            }, {
            {TECH_HEAVY_CAMEL_RIDER, -1}
    });

    //Give more civs access to the camel scout
    //https://www.reddit.com/r/aoe2/comments/ukg4ko/should_other_civs_get_the_camel_scout_as_well
    addTechnologiesToCivs(df, {
                CIV_HINDUSTANIS,
                CIV_ETHIOPIANS,
                CIV_MALIANS,
                CIV_BERBERS,
                CIV_SARACENS,
            }, {
            {TECH_CAMEL_SCOUT_MAKE_AVAILABLE, -1},
            {TECH_CAMEL_MAKE_AVAILABLE, -1}
    });
    //Give out some legionaires 
    //https://www.reddit.com/r/aoe2/comments/13tw143/so_i_read_some_comments_about_how_byzantine_civ/
    addTechnologiesToCivs(df, {
                CIV_BYZANTINES,
            }, {
            {TECH_LEGIONARY, -1},
            {TECH_DISABLE_MILITIA_UPGRADES, -1}
    });
    //give celts some infantry love and remove paladin
    //https://www.reddit.com/r/aoe2/comments/164jd1v/give_celts_squires/
    addTechnologiesToCivs(df, {
                CIV_CELTS,
            }, {
            {SQUIRES, -1},
            {BLOODLINES, -1},
            {TECH_DISABLE_PALADIN, -1}
    });
    //give magyars winged hussars
    //https://www.reddit.com/r/aoe2/comments/qu6b4a/should_magyars_get_winged_hussars_too/
    addTechnologiesToCivs(df, {
                CIV_MAGYARS,
                CIV_CUMANS
            }, {
                //must disable first so the id maps for adding winged hussars
            {TECH_DISABLE_HUSSARS, -1},
            {TECH_WINGED_HUSSARS, 6}
    });

    //give ethiopians war elephants, no elite
    //https://forums.ageofempires.com/t/should-ethiopians-get-war-elephants/202217/12
    addExtraUniqueUnitToCiv(df,
                CIV_ETHIOPIANS, WAR_ELEPHANT, TECH_WAR_ELEPHANT_MAKE_AVAILABLE
    );
    //give imperial skirm to civs that had great skirms 
    //https://www.reddit.com/r/aoe2/comments/17h70lv/imperial_skirmisher_would_be_nice_if_it_wasnt/
    addTechnologiesToCivs(df, {
                CIV_MALIANS,
                CIV_ROMANS
            }, {
            {TECH_IMPERIAL_SKIRMISHER, 7}
    });
    //give some boys imp camels
    //https://forums.ageofempires.com/t/imperial-camels-for-saracens-turks-and-berbers/245239
    addTechnologiesToCivs(df, {
                CIV_BERBERS,
                CIV_SARACENS,
                CIV_TURKS
            }, {
            {TECH_IMPERIAL_CAMEL_RIDER, 8}
    });


    //give portugeset conquistadors, no elite
    //https://www.reddit.com/r/aoe2/comments/snpt20/how_unbalanced_would_making_the_conq_a_regional/
    addExtraUniqueUnitToCiv(df,
                CIV_PORTUGUESE, CONQUISTADOR, TECH_CONQUISTADOR_MAKE_AVAILABLE
    );

    //give missionaries to some more civs
    //https://www.reddit.com/r/aoe2/comments/ka4jvi/why_dont_portuguese_have_access_to_missionaries/
    //https://www.reddit.com/r/aoe2/comments/152bspg/should_missionaries_be_just_exclusive_to_spanish/
    addTechnologiesToCivs(df, {
               CIV_ITALIANS,
               CIV_PORTUGUESE,
               CIV_BYZANTINES
            }, {
            {TECH_MISSIONARY_MAKE_AVAILABLE, -1}
    });

    //give warrior priest to some more civs
    //https://www.reddit.com/r/aoe2/comments/17egkrm/for_fun_what_if_the_new_warrior_priest_from/
    addTechnologiesToCivs(df, {
            CIV_VIKINGS,
            CIV_CELTS,
            CIV_AZTECS,
            CIV_DRAVIDIANS,
            CIV_MALIANS,
            CIV_TEUTONS,
            CIV_JAPANESE,
            CIV_CHINESE
            }, {
            {TECH_WARRIOR_PRIEST_MAKE_AVAILABLE, -1}
    });

    /*NOTE EVERYTHING BELOW HERE IS EITHER IN DEBUG OR HAS NOT BEEN TESTED*/

    //Add genitour to more civs that would have had them
    //https://www.reddit.com/r/aoe2/comments/106i52l/genitours_for_middle_eastern_civs/
    //https://www.reddit.com/r/aoe2/comments/rheysc/malians_civ_rework/
    addGenitourToCivs(df, {
            CIV_SPANISH,
            CIV_PORTUGUESE,
            CIV_PERSIANS,
            CIV_SARACENS,
            CIV_MALIANS,
            CIV_TURKS
    });
}

void giveUnitsRegionalSkins(genie::DatFile *df){
    //give elite janissarys hats
    updateUnitSkins(df, {CIV_TURKS }, ELITE_JANISSARY, ROYAL_JANISSARY, true);
    //https://forums.ageofempires.com/t/regional-skins-are-already-in-the-game-its-just-a-matter-of-allowing-through-non-data-mod-for-asian-african-civs/85404
    //give middle east civs imam for monks
    updateUnitSkins(df, {CIV_PERSIANS, CIV_SARACENS, CIV_HINDUSTANIS, CIV_ETHIOPIANS, CIV_MALIANS, CIV_BERBERS }, MONK, IMAM, true);
    //give SE asian and chinese bui bi sking for monks
    updateUnitSkins(df, {CIV_CHINESE, CIV_KHMER, CIV_MALAY, CIV_BURMESE, CIV_VIETNAMESE, CIV_DRAVIDIANS, CIV_BENGALIS, CIV_GURJARAS}, MONK, BUI_BI, true);
    //give some civs priest  for monks
    updateUnitSkins(df, {CIV_ROMANS}, MONK, PRIEST, true);




    //atillia knight line upgrades
    const std::vector<int> atillaKnightLine = {CIV_JAPANESE, CIV_CHINESE, CIV_BYZANTINES, CIV_TURKS, CIV_MONGOLS, CIV_HUNS, CIV_KOREANS, CIV_KHMER, CIV_TATARS, CIV_CUMANS, CIV_VIETNAMESE};
    //give atilla as knight for SR asia, east asia, hun etc...
    updateUnitSkins(df, atillaKnightLine, KNIGHT, ATILLA_THE_HUN);
    updateUnitSkins(df, atillaKnightLine, CAVALIER, WANG_TONG);
    updateUnitSkins(df, {CIV_CUMANS, CIV_HUNS, CIV_MAGYARS, CIV_MONGOLS}, CAVALIER, CUMAN_CHIEF, true);

    //sumanguru knight line upgrades
    const std::vector<int> sumanguruKinghtLine = {CIV_PERSIANS, CIV_SARACENS, CIV_HINDUSTANIS, CIV_ETHIOPIANS, CIV_MALIANS, CIV_BERBERS, CIV_MALAY, CIV_BURMESE, CIV_DRAVIDIANS, CIV_BENGALIS, CIV_GURJARAS};
    updateUnitSkins(df, sumanguruKinghtLine, KNIGHT, SUMANGURU);
    updateUnitSkins(df, sumanguruKinghtLine, CAVALIER, SUNDJATA );
    updateUnitSkins(df, sumanguruKinghtLine, HUSSAR, ARAIYAN_RAJARAJAN);

    //give eastern europe paldins vayatas skin
    const std::vector<int> bohemondKnightLine = {CIV_MAGYARS, CIV_SLAVS, CIV_BULGARIANS, CIV_LITHUANIANS, CIV_CUMANS, CIV_BURGUNDIANS, CIV_BOHEMIANS, CIV_ARMENIANS};
    updateUnitSkins(df, bohemondKnightLine, KNIGHT, BOHEMOND);
    updateUnitSkins(df, bohemondKnightLine, CAVALIER, KESTUTIS);
    updateUnitSkins(df, bohemondKnightLine, PALADIN, VYAUTAS_THE_GREAT);




    //west europe style knight changes
    const std::vector<int> westernEuropKnightLines = {CIV_BRITONS, CIV_GOTHS, CIV_TEUTONS, CIV_LITHUANIANS, CIV_SICILIANS, CIV_POLES, CIV_BOHEMIANS, CIV_GEORGIANS};
    updateUnitSkins(df, westernEuropKnightLines, KNIGHT, GILBERT_DE_CLARE);
    updateUnitSkins(df, westernEuropKnightLines, CAVALIER, ALGRIDAS);

    //give crusader paldins to crusader civs
    updateUnitSkins(df, {CIV_ITALIANS, CIV_SICILIANS}, PALADIN, CRUSADER_KNIGHT, true, true);
    updateUnitSkins(df, {CIV_TEUTONS}, PALADIN, ULRICH_VON_JUNGINGEN, true);
    //give frank paldins to britains civs because franks get gold ones
    updateUnitSkins(df, {CIV_BRITONS}, PALADIN, FRANKISH_PALADIN);


    //update franks to be more fun
    updateUnitSkins(df, {CIV_FRANKS}, KNIGHT, PALADIN);
    updateUnitSkins(df, {CIV_FRANKS}, CAVALIER, ALGRIDAS);
    updateUnitSkins(df, {CIV_FRANKS}, PALADIN, BERNARD);


    //give romans some better knight lines
    updateUnitSkins(df, {CIV_ROMANS}, KNIGHT, ALARIC_THE_GOTH);
    updateUnitSkins(df, {CIV_ROMANS}, CAVALIER, LE_LAI);

    //indian knight line skins
    const std::vector<int> indianMiddleEachKnightLineCivs = {CIV_PERSIANS, CIV_SARACENS, CIV_TURKS, CIV_MONGOLS, CIV_HUNS, CIV_ETHIOPIANS, CIV_MALIANS, CIV_BERBERS, CIV_KHMER, CIV_MALAY, CIV_HINDUSTANIS, CIV_MALAY, CIV_BURMESE, CIV_DRAVIDIANS, CIV_BENGALIS, CIV_GURJARAS};
    updateUnitSkins(df, indianMiddleEachKnightLineCivs, KNIGHT, RAJENDRA_CHOLA);
    updateUnitSkins(df, indianMiddleEachKnightLineCivs, CAVALIER, SHAH_ISMAIL);



    //give civs east asian civs subotair heavy cav archers 
    updateUnitSkins(df, {CIV_CHINESE, CIV_VIETNAMESE, CIV_KOREANS, CIV_JAPANESE}, HEAVY_CAV_ARCHER, SUBOTAI );
    updateUnitSkins(df, {CIV_MALAY, CIV_BURMESE, CIV_DRAVIDIANS, CIV_KHMER, CIV_HINDUSTANIS, CIV_DRAVIDIANS, CIV_BENGALIS, CIV_GURJARAS}, HEAVY_CAV_ARCHER, PRITHVIRAJ );
    //give cav archers into heavy cav archers for other civs
    const std::vector<int> girgenCavArcherLine = {CIV_BYZANTINES, CIV_PERSIANS, CIV_TURKS, CIV_MAGYARS, CIV_SLAVS, CIV_BULGARIANS, CIV_TATARS, CIV_LITHUANIANS, CIV_BURGUNDIANS, CIV_POLES, CIV_GEORGIANS, CIV_ARMENIANS};
    updateUnitSkins(df, girgenCavArcherLine, CAVALRY_ARCHER, GIRGEN_KHAN );
    updateUnitSkins(df, girgenCavArcherLine, HEAVY_CAV_ARCHER, KOTYAN_KHAN );
    //steppe archers
    const std::vector<int> steppeCavArcherLine = {CIV_MONGOLS, CIV_HUNS, CIV_TATARS, CIV_CUMANS};
    updateUnitSkins(df, steppeCavArcherLine, CAVALRY_ARCHER, QUTLUGH );
    updateUnitSkins(df, steppeCavArcherLine, HEAVY_CAV_ARCHER, SHAYBANI_KHAN );




    //eastern civs leloi champ
    updateUnitSkins(df, {CIV_CHINESE, CIV_KOREANS, CIV_VIETNAMESE, CIV_JAPANESE}, CHAMPION, LE_LOI );

    //lots of civs eastern swordmen champ
    updateUnitSkins(df, {CIV_PERSIANS, CIV_SARACENS, CIV_TURKS, CIV_MONGOLS, CIV_HUNS, CIV_ETHIOPIANS, CIV_MALIANS, CIV_BERBERS, CIV_KHMER, CIV_MALAY, CIV_HINDUSTANIS, CIV_MALAY, CIV_BURMESE, CIV_DRAVIDIANS, CIV_BENGALIS, CIV_GURJARAS}, CHAMPION, EASTERN_SWORDSMEN);

    //lots of civs gidajan champ
    updateUnitSkins(df, {CIV_PERSIANS, CIV_SARACENS, CIV_TURKS, CIV_MONGOLS, CIV_HUNS, CIV_ETHIOPIANS, CIV_MALIANS, CIV_BERBERS, CIV_KHMER, CIV_MALAY, CIV_HINDUSTANIS, CIV_MALAY, CIV_BURMESE, CIV_DRAVIDIANS, CIV_BENGALIS, CIV_GURJARAS}, CHAMPION, GIDAJAN );

    //american civs pachacuti
    updateUnitSkins(df, {CIV_AZTECS, CIV_MAYANS, CIV_INCAS}, CHAMPION, PACHACUTI );

    //romans heavy swordsmen
    updateUnitSkins(df, {CIV_ROMANS}, LONG_SWORDSMAN, HEAVY_SWORDSMEN);

    //"barbarian" civ unique units
    const std::vector<int> barbarianLine = {CIV_CELTS, CIV_GOTHS, CIV_VIKINGS};
    updateUnitSkins(df, barbarianLine, MAN_AT_ARMS, NORSE_WARRIOR );
    updateUnitSkins(df, barbarianLine, LONG_SWORDSMAN, IVALYO_INFANTRY );
    updateUnitSkins(df, barbarianLine, TWO_HANDED_SWORDSMAN, ATAULF );
    updateUnitSkins(df, barbarianLine, CHAMPION, WILLIAM_WALLACE );
    //knights
    updateUnitSkins(df, barbarianLine, KNIGHT, JANZIZKA );


    //"euopean" civ unique units
    const std::vector<int> europeanInfantryLine = {CIV_FRANKS, CIV_BRITONS, CIV_GOTHS, CIV_TEUTONS, CIV_BULGARIANS, CIV_LITHUANIANS, CIV_SICILIANS, CIV_POLES, CIV_BOHEMIANS, CIV_GEORGIANS};
    updateUnitSkins(df, europeanInfantryLine, MAN_AT_ARMS, DAFYD_AP_GRUFFYD );
    updateUnitSkins(df, europeanInfantryLine, LONG_SWORDSMAN, LLYWELYN_AP_GRUFFYD );

    //give a pike upgrade here
    updateUnitSkins(df, {CIV_BERBERS, CIV_SARACENS, CIV_MALIANS, CIV_ETHIOPIANS}, HALBERDIER, SOSSO_GUARD);

}

void configureRegionalAdditions(genie::DatFile *df) {
    giveUnitsRegionalSkins(df);
    allowSamuraiToSwapToArcherMode(df);
    makeLongboatsTransports(df);
    giveHistoricRegionalVarietyToCivs(df);
}
