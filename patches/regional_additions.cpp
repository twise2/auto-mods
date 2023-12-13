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

void duplicateTechToNewCiv(genie::DatFile *df, int techId, int civId ) {
        genie::Tech tech = df->Techs.at(techId);
        tech.Civ = civId;
        //turn off full tech mode as that will break with this anyway
        //and this will be so much easier if i can reuse FTT stuff in base
        //rather than having to figure out tech tree modifications
        tech.FullTechMode = 0;         
        df->Techs.push_back(tech);
    std::cout << "Added Tech '" << tech.Name << "' to civ id '" << df->Civs.at(civId).Name << "'" << std::endl;
};

void allowSamuraiToSwapToArcherMode(genie::DatFile *df) {
    for (genie::Civ &civ : df->Civs) {
        //use archer fo the eye for samuraiUnit swap
        genie::Unit &samuraiUnit = civ.Units.at(SAMURAI);
        samuraiUnit.Nothing = ARCHER_OF_THE_EYES;
        samuraiUnit.Trait = samuraiUnit.Trait | 8;

        //make archer of the eye bad except against unique units
        genie::Unit &samuraiUnitArcher = civ.Units.at(ARCHER_OF_THE_EYES);
        samuraiUnitArcher.Nothing = SAMURAI;
        samuraiUnitArcher.Trait = samuraiUnitArcher.Trait | 8;

        samuraiUnitArcher.Name = "Samurai (ranged)";
        samuraiUnitArcher.LanguageDLLName = LANGFILE_ENGLISH_SAMURAI;
        //df->Langfile.setString(LANGFILE_ENGLISH_ARCHER_OF_THE_EYES, "Samurai (Ranged)").
        samuraiUnitArcher.Creatable.HeroGlowGraphic = -1;
        samuraiUnitArcher.Creatable.HeroMode = 0;
        samuraiUnitArcher.Type50.BaseArmor = 0; //dont give armor bonuses
        //make sure it's ranged mode is only good against unique units
        samuraiUnitArcher.Type50.DisplayedAttack = 1;
        //super slow but heavy hitting to encourage shoot once than swap
        samuraiUnitArcher.Type50.ReloadTime = 4;
        samuraiUnitArcher.Type50.DisplayedReloadTime = 4;
        //has 2 attacks, unlikely to change
        samuraiUnitArcher.Type50.Attacks.at(0).Amount = 1;
        samuraiUnitArcher.Type50.Attacks.at(1).Amount = 25;
        samuraiUnitArcher.Type50.Attacks.at(1).Class = ATTACK_TYPE_HERO_BONUS_DAMAGE;
        //slow them down for good measure to decrease odds of staying in this form
        samuraiUnitArcher.Speed = .81;
    }
    std::cout << "Added Ability 'Samurai can swap to Ranged Mode'" << std::endl;
}

void addTechnologiesToCivs(genie::DatFile *df, std::vector<int16_t> civIds, std::vector<int16_t>  techIds){
    for (int16_t civId : civIds) {
        for (int16_t techId : techIds) {
            duplicateTechToNewCiv(df, techId, civId);
        }
    };
};

void makeLongboatsTransports(genie::DatFile *df) {
    //allow viking longboats to transport 5 units
    //https://www.google.com/search?q=longboats+should+transport+aoe2&rlz=1C5CHFA_enUS906US906&oq=longboats+should+transport+aoe2&gs_lcrp=EgZjaHJvbWUyCQgAEEUYORigATIHCAEQIRigAdIBCDQyOTBqMGo5qAIAsAIA&sourceid=chrome&ie=UTF-8
    for (genie::Civ &civ : df->Civs) {
        genie::Unit &longboat = civ.Units.at(LONGBOAT);
        genie::Unit &eliteLongboat = civ.Units.at(ELITE_LONGBOAT);
        longboat.GarrisonCapacity = 5;
        eliteLongboat.GarrisonCapacity = 5;
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
                TECH_MULECART_MAKE_AVAILABLE
            } 
    );
    //add chemistry to the civ that created it 
    //https://forums.ageofempires.com/t/chinese-civilization/73726
    addTechnologiesToCivs(df, {
                CIV_CHINESE,
            }, {
               TECH_HAND_CANNON,
               TECH_BOMBARD_TOWER
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
               TECH_CARAVANSERI_MAKE_AVAILABLE 
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
                TECH_ELEPHAUNT_ARCHER_MAKE_AVAILABLE,
                //have to move because these civs have cav archers as well
                TECH_MOVE_ELEPHANT_ARCHER
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
            TECH_ARMORED_ELEPHANT_MAKE_AVAILABLE,
            TECH_SIEGE_ELEPHANT,
            TECH_MOVE_ARMORED_ELEPHANT
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
                CIV_HUNS,
                CIV_TURKS,
                CIV_PERSIANS
            }, {
                TECH_STEPPE_LANCER_MAKE_AVAILABLE
    });
    addTechnologiesToCivs(df, {
                CIV_HUNS,
                CIV_TURKS
            }, {
                TECH_ELITE_STEPPE_LANCER_MAKE_AVAILABLE
    });
    //disable paladin for pure cumans and give heavy camel
    //https://forums.ageofempires.com/t/give-cumans-heavy-camel-riders-and-remove-paladins-and-maybe-chevaliers/196455
    //https://www.reddit.com/r/aoe2/comments/y6b17r/disproportionate_spread_of_regional_units/
    addTechnologiesToCivs(df, {
                CIV_CUMANS,
                CIV_HUNS
            }, {
                TECH_DISABLE_PALADIN,
                TECH_HEAVY_CAMEL_RIDER
    });
    //Add genitour to more civs that would have had them
    //https://forums.ageofempires.com/t/give-cumans-heavy-camel-riders-and-remove-paladins-and-maybe-chevaliers/196455
    addTechnologiesToCivs(df, {
                CIV_SPANISH,
                CIV_PORTUGUESE,
                CIV_PERSIANS,
                CIV_SARACENS,
                CIV_TURKS
            }, {
                TECH_GENITOUR_MAKE_AVAILABLE
    });

    //Give more civs access to the camel scout
    //https://www.reddit.com/r/aoe2/comments/ukg4ko/should_other_civs_get_the_camel_scout_as_well
    addTechnologiesToCivs(df, {
                CIV_HINDUSTANIS,
                CIV_BERBERS,
                CIV_SARACENS,
            }, {
                TECH_CAMEL_SCOUT_MAKE_AVAILABLE
    });
    //Give out some legionaires 
    //https://www.reddit.com/r/aoe2/comments/13tw143/so_i_read_some_comments_about_how_byzantine_civ/
    addTechnologiesToCivs(df, {
                CIV_BYZANTINES,
            }, {
                TECH_LEGIONARY,
                TECH_DISABLE_MILITIA_UPGRADES
    });
    //give celts some infantry love and remove paladin
    //https://www.reddit.com/r/aoe2/comments/164jd1v/give_celts_squires/
    addTechnologiesToCivs(df, {
                CIV_CELTS,
            }, {
                SQUIRES,
                BLOODLINES,
                TECH_DISABLE_PALADIN
    });
    //give magyars winged hussars
    //https://www.reddit.com/r/aoe2/comments/qu6b4a/should_magyars_get_winged_hussars_too/
    addTechnologiesToCivs(df, {
                CIV_MAGYARS,
                CIV_CUMANS
            }, {
            TECH_WINGED_HUSSARS,
            TECH_DISABLE_HUSSARS
    });

    //TODO need to make this work as war elephant is in the way
    /*
    //give ethiopians war elephants, no elite
    //https://forums.ageofempires.com/t/should-ethiopians-get-war-elephants/202217/12
    addTechnologiesToCivs(df, {
                CIV_ETHIOPIANS
            }, {
            TECH_WAR_ELEPHANT_MAKE_AVAILABLE
    });
    */
    //give imperial skirm to civs that had great skirms 
    //https://www.reddit.com/r/aoe2/comments/17h70lv/imperial_skirmisher_would_be_nice_if_it_wasnt/
    addTechnologiesToCivs(df, {
                CIV_MALIANS,
                CIV_ROMANS
            }, {
            TECH_IMPERIAL_SKIRMISHER
    });
}

void configureRegionalAdditions(genie::DatFile *df) {
    allowSamuraiToSwapToArcherMode(df);
    makeLongboatsTransports(df);
    giveHistoricRegionalVarietyToCivs(df);
}
