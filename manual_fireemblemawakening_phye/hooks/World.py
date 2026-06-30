# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, remove_specific_item

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """
    pass

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    from ..Helpers import get_option_value
    male_avatar = is_option_enabled(multiworld, player, "Male_Avatar")
    possible_pairings = {
        "Sumia": ["Frederick", "Gaius", "Henry"],
        "Olivia": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Maribelle": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Sully": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Lissa": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Cordelia": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Cherche": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Panne": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Miriel": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Tharja": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        "Nowi": ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"],
        }
    chrom_wives = ["Sully", "Sumia", "Maribelle", "Olivia"]
    robin_wives = ["Sully", "Sumia", "Maribelle", "Olivia", "Lissa", "Cordelia", "Cherche", "Panne", "Miriel", "Tharja", "Nowi" ]
    robin_extra_wives = ["Lucina", "Kjelle", "Cynthia", "Severa", "Noire", "Nah"]
    robin_extra_1 = get_option_value(multiworld, player, "Robin_PairPlus") >= 1
    robin_extra_2 = get_option_value(multiworld, player, "Robin_PairPlus") >= 2
    robin_extra_3 = get_option_value(multiworld, player, "Robin_PairPlus") >= 3
    robin_2nd = is_option_enabled(multiworld, player, "Robin_2ndGen")

        
    if not male_avatar:
       chrom_wives.append("Robin")
       if not robin_2nd:
          possible_pairings["Robin"] = ["Frederick", "Virion", "Stahl", "Vaike", "Kellam", "Lon'qu", "Ricken", "Gaius", "Donnel", "Gregor", "Libra", "Henry"]
          if robin_extra_1:
             possible_pairings["Robin"] += ["Brady", "Gerome", "Owain", "Inigo", "Yarne", "Laurent"]
             if robin_extra_2:
                possible_pairings["Robin"] += ["Basilio"]
                if robin_extra_3:
                   possible_pairings["Robin"] += ["Gangrel", "Walhart", "Yen'fay", "Priam"]
       if robin_2nd:
          possible_pairings["Robin"] = ["Brady", "Gerome", "Owain", "Inigo", "Yarne", "Laurent"]
                
    # Generates Parents for children and making sure everyone can be paired 
    def generate_pairings(possible_pairings, rng):
        available_fathers = set()
        #Chrom Gets his Wife first!
        chrom_wife = rng.choice(chrom_wives)
        world.chrom_wife = chrom_wife
        possible_pairings[chrom_wife] = ["Chrom"]
        #Then Robin gets his if he is male
        if male_avatar:
            if not robin_2nd:
                robin_wives.remove(chrom_wife)
                if robin_extra_1:
                    robin_wives_1 = ["Lucina", "Kjelle", "Cynthia", "Severa", "Noire", "Nah"]
                    robin_wives.extend(robin_wives_1)
                    if robin_extra_2:
                        robin_wives_2 = ["Anna", "Say'ri", "Flavia", "Tiki"]
                        robin_wives.extend(robin_wives_2)
                        if robin_extra_3:
                            robin_wives_3 = ["Aversa", "Emmeryn"]
                            robin_wives.extend(robin_wives_3)
                robin_wife = rng.choice(robin_wives)
            if robin_2nd:
                robin_wife = rng.choice(robin_extra_wives)
            possible_pairings[robin_wife] = ["Robin"]
            world.robin_wife = robin_wife
        if not male_avatar:
            world.robin_wife = "None"
        for fathers in possible_pairings.values():
            available_fathers.update(fathers)
        
        result = {}

        mothers = list(possible_pairings.keys())
        rng.shuffle(mothers)

        #Makes sure the mothers with the least amount of pairings get their partner first.
        mothers = sorted(
        possible_pairings.keys(),
        key=lambda m: len(possible_pairings[m])
)
        for mother in mothers:
            valid = [
               father
               for father in possible_pairings[mother]
               if father in available_fathers
            ]

            if not valid:
               raise Exception(f"No valid father remaining for {mother}")

            chosen = rng.choice(valid)

            result[mother] = chosen
            available_fathers.remove(chosen)

        return result

    Children = is_option_enabled(multiworld, player, "Enable_Children")
    ChildPair = is_option_enabled(multiworld, player, "Restrict_ChildPairs")
    E_Rank = is_option_enabled(multiworld, player, "Include_Rank_E")
    Prog_Weapon = is_option_enabled(multiworld, player, "Progressive_Weapons")
    MadKing = is_option_enabled(multiworld, player, "Mad_King_Goal")
    ProgPro = is_option_enabled(multiworld, player, "Progressive_Paralogues")
    SpotPassPro = is_option_enabled(multiworld, player, "Enable_SpotPass_Paralogues")
    CharaSpecific = is_option_enabled(multiworld, player, "Character_Specific_Classes")
    
    if E_Rank:
       if Prog_Weapon:
            item_config["Progressive Sword Rank"] = {"useful": 5}
            item_config["Progressive Lance Rank"] = {"useful": 5}
            item_config["Progressive Axe Rank"] = {"useful": 5}
            item_config["Progressive Bow Rank"] = {"useful": 5}
            item_config["Progressive Fire Tome Rank"] = {"useful": 5}
            item_config["Progressive Wind Tome Rank"] = {"useful": 5}
            item_config["Progressive Thunder Tome Rank"] = {"useful": 5}
            item_config["Progressive Dark Tome Rank"] = {"useful": 5}
            item_config["Progressive Staff Rank"] = {"useful": 5}
    if MadKing:
        item_config["Main Chapter Progression"] = {"progression": 11}
    if not MadKing:
        if ProgPro:
           if SpotPassPro:
              item_config["Progressive Paralogue Chapter"] = {"progression": 23}  
        if Children:
           if ChildPair:
              generated_pairings = generate_pairings(possible_pairings,world.random)
              world.generated_pairings = generated_pairings

              generated_pairing_names = set()

              for mother, father in generated_pairings.items():
                pairing_name = f"{mother} x {father}"
                generated_pairing_names.add(pairing_name)
                item_config[pairing_name] = {"progression": 1}

              if CharaSpecific:
                    lucina_mother = world.chrom_wife
                    owain_father = generated_pairings.get("Lissa")
                    inigo_father = generated_pairings.get("Olivia")
                    brady_father = generated_pairings.get("Maribelle")
                    kjelle_father = generated_pairings.get("Sully")
                    cynthia_father = generated_pairings.get("Sumia")
                    severa_father = generated_pairings.get("Cordelia")
                    gerome_father = generated_pairings.get("Cherche")
                    morgan_mother = world.robin_wife
                    morgan_father = generated_pairings.get("Robin")
                    yarne_father = generated_pairings.get("Panne")
                    laurent_father = generated_pairings.get("Miriel")
                    noire_father = generated_pairings.get("Tharja")
                    nah_father = generated_pairings.get("Nowi")    
                    taguel_parent = (
                    world.robin_wife == "Panne" or
                    generated_pairings.get("Robin") == "Yarne"
                    )
                    
                    if lucina_mother != "Robin":
                        item_config["Lucina's Tactician"] = {"progression": 0}
                        item_config["Lucina's Grandmaster"] = {"progression": 0}
                        item_config["Lucina's Thief"] = {"progression": 0}
                        item_config["Lucina's Trickster"] = {"progression": 0}
                        item_config["Lucina's Hero"] = {"progression": 0}
                        item_config["Lucina's Mercenary"] = {"progression": 0}
                        item_config["Lucina's Sorcerer"] = {"progression": 0}
                        item_config["Lucina's Dark Mage"] = {"progression": 0}                 
                       
                    if lucina_mother not in {"Robin", "Sumia"}:
                        item_config["Lucina's Knight"] = {"progression": 0}
                        item_config["Lucina's General"] = {"progression": 0}

                    if lucina_mother not in {"Robin", "Sully", "Olivia"}:
                        item_config["Lucina's Swordmaster"] = {"progression": 0}
                        item_config["Lucina's Myrmidon"] = {"progression": 0}
                        item_config["Lucina's Assassin"] = {"progression": 0}
                 
                    if lucina_mother not in {"Robin", "Sumia", "Maribelle", "Olivia"}:
                        item_config["Lucina's Pegasus Knight"] = {"progression": 0}
                        item_config["Lucina's Falcon Knight"] = {"progression": 0}
                        item_config["Lucina's Dark Flier"] = {"progression": 0}

                    if lucina_mother not in {"Robin", "Sully"}:
                        item_config["Lucina's Wyvern Rider"] = {"progression": 0}
                        item_config["Lucina's Wyvern Lord"] = {"progression": 0}
                        item_config["Lucina's Griffon Rider"] = {"progression": 0}

                    if lucina_mother not in {"Robin", "Maribelle"}:
                        item_config["Lucina's Dark Knight"] = {"progression": 0}
                        item_config["Lucina's Mage"] = {"progression": 0}
                        item_config["Lucina's Troubadour"] = {"progression": 0}
                        item_config["Lucina's Valkyrie"] = {"progression": 0}

                    if lucina_mother not in {"Robin", "Sumia", "Maribelle"}:
                        item_config["Lucina's Sage"] = {"progression": 0}
                        item_config["Lucina's Cleric"] = {"progression": 0}
                        item_config["Lucina's War Cleric"] = {"progression": 0}

                    if owain_father != "Robin":
                        item_config["Owain's Tactician"] = {"progression": 0}
                        item_config["Owain's Grandmaster"] = {"progression": 0}

                    if owain_father not in {"Robin", "Frederick", "Stahl", "Ricken"}:
                        item_config["Owain's Paladin"] = {"progression": 0}
                        item_config["Owain's Cavalier"] = {"progression": 0}

                    if owain_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Owain's Knight"] = {"progression": 0}
                        item_config["Owain's General"] = {"progression": 0}

                    if owain_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Kellam"}:
                        item_config["Owain's Great Knight"] = {"progression": 0}

                    if owain_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Owain's Thief"] = {"progression": 0}
                        item_config["Owain's Trickster"] = {"progression": 0}

                    if owain_father not in {"Robin", "Vaike", "Donnel"}:
                        item_config["Owain's Fighter"] = {"progression": 0}

                    if owain_father not in {"Robin", "Vaike", "Donnel", "Gregor"}:
                        item_config["Owain's Hero"] = {"progression": 0}

                    if owain_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Owain's Mercenary"] = {"progression": 0}

                    if owain_father not in {"Robin", "Donnel", "Gregor", "Virion", "Stahl", "Ricken"}:
                        item_config["Owain's Bow Knight"] = {"progression": 0}

                    if owain_father not in {"Robin", "Virion", "Stahl", "Ricken"}:
                        item_config["Owain's Archer"] = {"progression": 0}
                        item_config["Owain's Sniper"] = {"progression": 0}

                    if owain_father not in {"Robin", "Frederick", "Virion", "Lon'qu"}:
                        item_config["Owain's Wyvern Rider"] = {"progression": 0}
                        item_config["Owain's Wyvern Lord"] = {"progression": 0}
                        item_config["Owain's Griffon Rider"] = {"progression": 0}

                    if owain_father not in {"Robin", "Libra", "Henry"}:
                        item_config["Owain's Sorcerer"] = {"progression": 0}
                        item_config["Owain's Dark Mage"] = {"progression": 0}

                    if owain_father not in {"Robin", "Virion", "Ricken", "Libra", "Henry"}:
                        item_config["Owain's Dark Knight"] = {"progression": 0}

                    if owain_father not in {"Robin", "Virion", "Ricken", "Libra"}:
                        item_config["Owain's Mage"] = {"progression": 0}

                    if owain_father != "Donnel":
                        item_config["Owain's Villager"] = {"progression": 0}

                    if inigo_father != "Robin":
                        item_config["Inigo's Tactician"] = {"progression": 0}
                        item_config["Inigo's Grandmaster"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Chrom"}:
                        item_config["Inigo's Paladin"] = {"progression": 0}
                        item_config["Inigo's Cavalier"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Inigo's Knight"] = {"progression": 0}
                        item_config["Inigo's General"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Kellam", "Chrom"}:
                        item_config["Inigo's Great Knight"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Inigo's Thief"] = {"progression": 0}
                        item_config["Inigo's Trickster"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Vaike", "Donnel"}:
                        item_config["Inigo's Fighter"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Virion", "Stahl", "Ricken", "Chrom"}:
                        item_config["Inigo's Archer"] = {"progression": 0}
                        item_config["Inigo's Sniper"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Frederick", "Virion", "Lon'qu"}:
                        item_config["Inigo's Wyvern Rider"] = {"progression": 0}
                        item_config["Inigo's Wyvern Lord"] = {"progression": 0}
                        item_config["Inigo's Griffon Rider"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Libra", "Henry"}:
                        item_config["Inigo's Sorcerer"] = {"progression": 0}
                        item_config["Inigo's Dark Mage"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Virion", "Ricken", "Libra", "Henry"}:
                        item_config["Inigo's Dark Knight"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Virion", "Ricken", "Libra"}:
                        item_config["Inigo's Mage"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Virion", "Ricken", "Libra", "Kellam"}:
                        item_config["Inigo's Sage"] = {"progression": 0}

                    if inigo_father not in {"Robin", "Kellam", "Libra"}:
                        item_config["Inigo's Priest"] = {"progression": 0}
                        item_config["Inigo's War Monk"] = {"progression": 0}

                    if inigo_father != "Donnel":
                        item_config["Inigo's Villager"] = {"progression": 0} 

                    if brady_father != "Robin":
                        item_config["Brady's Tactician"] = {"progression": 0}
                        item_config["Brady's Grandmaster"] = {"progression": 0}

                    if brady_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Brady's Knight"] = {"progression": 0}
                        item_config["Brady's General"] = {"progression": 0}

                    if brady_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor"}:
                        item_config["Brady's Swordmaster"] = {"progression": 0}
                        item_config["Brady's Myrmidon"] = {"progression": 0}

                    if brady_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor", "Vaike", "Kellam", "Gaius", "Henry"}:
                        item_config["Brady's Assassin"] = {"progression": 0}

                    if brady_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Brady's Thief"] = {"progression": 0}
                        item_config["Brady's Trickster"] = {"progression": 0}

                    if brady_father not in {"Robin", "Vaike", "Gaius", "Gregor", "Henry"}:
                        item_config["Brady's Berserker"] = {"progression": 0}
                        item_config["Brady's Barbarian"] = {"progression": 0}

                    if brady_father not in {"Robin", "Vaike", "Gaius", "Gregor", "Henry", "Donnel"}:
                        item_config["Brady's Warrior"] = {"progression": 0}

                    if brady_father not in {"Robin", "Vaike", "Donnel"}:
                        item_config["Brady's Fighter"] = {"progression": 0}

                    if brady_father not in {"Robin", "Vaike", "Donnel", "Gregor"}:
                        item_config["Brady's Hero"] = {"progression": 0}

                    if brady_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Brady's Mercenary"] = {"progression": 0}

                    if brady_father not in {"Robin", "Donnel", "Gregor", "Virion", "Stahl", "Ricken", "Chrom"}:
                        item_config["Brady's Bow Knight"] = {"progression": 0}

                    if brady_father not in {"Robin", "Virion", "Stahl", "Ricken", "Chrom"}:
                        item_config["Brady's Archer"] = {"progression": 0}
                        item_config["Brady's Sniper"] = {"progression": 0}

                    if brady_father not in {"Robin", "Frederick", "Virion", "Lon'qu"}:
                        item_config["Brady's Wyvern Rider"] = {"progression": 0}
                        item_config["Brady's Wyvern Lord"] = {"progression": 0}
                        item_config["Brady's Griffon Rider"] = {"progression": 0}

                    if brady_father not in {"Robin", "Libra", "Henry"}:
                        item_config["Brady's Sorcerer"] = {"progression": 0}
                        item_config["Brady's Dark Mage"] = {"progression": 0}

                    if brady_father != "Donnel":
                        item_config["Brady's Villager"] = {"progression": 0}  

                    if kjelle_father != "Robin":
                        item_config["Kjelle's Tactician"] = {"progression": 0}
                        item_config["Kjelle's Grandmaster"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Kjelle's Thief"] = {"progression": 0}
                        item_config["Kjelle's Trickster"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Vaike", "Donnel", "Gregor"}:
                        item_config["Kjelle's Hero"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Kjelle's Mercenary"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Donnel", "Gregor", "Virion", "Stahl", "Ricken", "Chrom"}:
                        item_config["Kjelle's Bow Knight"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Virion", "Stahl", "Ricken", "Chrom"}:
                        item_config["Kjelle's Archer"] = {"progression": 0}
                        item_config["Kjelle's Sniper"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Donnel", "Gaius"}:
                        item_config["Kjelle's Pegasus Knight"] = {"progression": 0}
                        item_config["Kjelle's Falcon Knight"] = {"progression": 0}
                        item_config["Kjelle's Dark Flier"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Libra", "Henry"}:
                        item_config["Kjelle's Sorcerer"] = {"progression": 0}
                        item_config["Kjelle's Dark Mage"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Virion", "Ricken", "Libra", "Henry"}:
                        item_config["Kjelle's Dark Knight"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Virion", "Ricken", "Libra"}:
                        item_config["Kjelle's Mage"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Virion", "Ricken", "Libra", "Kellam"}:
                        item_config["Kjelle's Sage"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Kellam", "Libra"}:
                        item_config["Kjelle's Cleric"] = {"progression": 0}
                        item_config["Kjelle's War Cleric"] = {"progression": 0}

                    if kjelle_father not in {"Robin", "Donnel", "Gregor", "Henry"}:
                        item_config["Kjelle's Troubadour"] = {"progression": 0}
                        item_config["Kjelle's Valkyrie"] = {"progression": 0} 

                    if cynthia_father != "Robin":
                        item_config["Cynthia's Tactician"] = {"progression": 0}
                        item_config["Cynthia's Grandmaster"] = {"progression": 0}
                        item_config["Cynthia's Mercenary"] = {"progression": 0}
                        item_config["Cynthia's Hero"] = {"progression": 0}
                        item_config["Cynthia's Mage"] = {"progression": 0}

                    if cynthia_father not in {"Robin", "Chrom", "Frederick"}:
                        item_config["Cynthia's Cavalier"] = {"progression": 0}
                        item_config["Cynthia's Paladin"] = {"progression": 0}

                    if cynthia_father not in {"Robin", "Gaius"}:
                        item_config["Cynthia's Myrmidon"] = {"progression": 0}
                        item_config["Cynthia's Swordmaster"] = {"progression": 0}

                    if cynthia_father not in {"Robin", "Gaius", "Henry"}:
                        item_config["Cynthia's Assassin"] = {"progression": 0}
                        item_config["Cynthia's Thief"] = {"progression": 0}
                        item_config["Cynthia's Trickster"] = {"progression": 0}

                    if cynthia_father not in {"Robin", "Chrom"}:
                        item_config["Cynthia's Bow Knight"] = {"progression": 0}
                        item_config["Cynthia's Archer"] = {"progression": 0}
                        item_config["Cynthia's Sniper"] = {"progression": 0}

                    if cynthia_father not in {"Robin", "Frederick"}:
                        item_config["Cynthia's Wyvern Rider"] = {"progression": 0}
                        item_config["Cynthia's Wyvern Lord"] = {"progression": 0}
                        item_config["Cynthia's Griffon Rider"] = {"progression": 0}

                    if cynthia_father not in {"Robin", "Henry"}:
                        item_config["Cynthia's Dark Mage"] = {"progression": 0}
                        item_config["Cynthia's Sorcerer"] = {"progression": 0}
                        item_config["Cynthia's Dark Knight"] = {"progression": 0}
                        item_config["Cynthia's Troubadour"] = {"progression": 0}
                        item_config["Cynthia's Valkyrie"] = {"progression": 0}

                    if severa_father != "Robin":
                        item_config["Severa's Tactician"] = {"progression": 0}
                        item_config["Severa's Grandmaster"] = {"progression": 0}

                    if severa_father not in {"Robin", "Frederick", "Stahl", "Ricken"}:
                        item_config["Severa's Paladin"] = {"progression": 0}
                        item_config["Severa's Cavalier"] = {"progression": 0}

                    if severa_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Kellam"}:
                        item_config["Severa's Great Knight"] = {"progression": 0}

                    if severa_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Severa's Knight"] = {"progression": 0}
                        item_config["Severa's General"] = {"progression": 0}

                    if severa_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor"}:
                        item_config["Severa's Swordmaster"] = {"progression": 0}
                        item_config["Severa's Myrmidon"] = {"progression": 0}

                    if severa_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor", "Vaike", "Kellam", "Gaius", "Henry"}:
                        item_config["Severa's Assassin"] = {"progression": 0}

                    if severa_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Severa's Thief"] = {"progression": 0}
                        item_config["Severa's Trickster"] = {"progression": 0}

                    if severa_father not in {"Robin", "Virion", "Stahl", "Ricken"}:
                        item_config["Severa's Archer"] = {"progression": 0}
                        item_config["Severa's Sniper"] = {"progression": 0}

                    if severa_father not in {"Robin", "Frederick", "Virion", "Lon'qu"}:
                        item_config["Severa's Wyvern Rider"] = {"progression": 0}
                        item_config["Severa's Wyvern Lord"] = {"progression": 0}
                        item_config["Severa's Griffon Rider"] = {"progression": 0}

                    if severa_father not in {"Robin", "Virion", "Ricken", "Libra"}:
                        item_config["Severa's Mage"] = {"progression": 0}

                    if severa_father not in {"Robin", "Virion", "Ricken", "Libra", "Kellam"}:
                        item_config["Severa's Sage"] = {"progression": 0}

                    if severa_father not in {"Robin", "Kellam", "Libra"}:
                        item_config["Severa's Cleric"] = {"progression": 0}
                        item_config["Severa's War Cleric"] = {"progression": 0}

                    if severa_father not in {"Robin", "Donnel", "Gregor", "Henry"}:
                        item_config["Severa's Troubadour"] = {"progression": 0}
                        item_config["Severa's Valkyrie"] = {"progression": 0}

                    if gerome_father != "Robin":
                        item_config["Gerome's Tactician"] = {"progression": 0}
                        item_config["Gerome's Grandmaster"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Frederick", "Stahl", "Ricken"}:
                        item_config["Gerome's Paladin"] = {"progression": 0}
                        item_config["Gerome's Cavalier"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Kellam"}:
                        item_config["Gerome's Great Knight"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Gerome's Knight"] = {"progression": 0}
                        item_config["Gerome's General"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor"}:
                        item_config["Gerome's Swordmaster"] = {"progression": 0}
                        item_config["Gerome's Myrmidon"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor", "Vaike", "Kellam", "Gaius", "Henry"}:
                        item_config["Gerome's Assassin"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Gerome's Thief"] = {"progression": 0}
                        item_config["Gerome's Trickster"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Vaike", "Gaius", "Gregor", "Henry"}:
                        item_config["Gerome's Berserker"] = {"progression": 0}
                        item_config["Gerome's Barbarian"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Gerome's Mercenary"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Donnel", "Gregor", "Virion", "Stahl", "Ricken"}:
                        item_config["Gerome's Bow Knight"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Virion", "Stahl", "Ricken"}:
                        item_config["Gerome's Archer"] = {"progression": 0}
                        item_config["Gerome's Sniper"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Libra", "Henry"}:
                        item_config["Gerome's Sorcerer"] = {"progression": 0}
                        item_config["Gerome's Dark Mage"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Virion", "Ricken", "Libra", "Henry"}:
                        item_config["Gerome's Dark Knight"] = {"progression": 0}

                    if gerome_father not in {"Robin", "Virion", "Ricken", "Libra"}:
                        item_config["Gerome's Mage"] = {"progression": 0}

                    if gerome_father != "Donnel":
                        item_config["Gerome's Villager"] = {"progression": 0} 

                    if morgan_mother not in {"Nowi", "Nah", "Tiki"}:
                        item_config["Morgan's Manakete"] = {"progression": 0}  

                    if morgan_father != "Donnel":
                        item_config["Morgan's Villager"] = {"progression": 0}  

                    if not taguel_parent:
                        item_config["Morgan's Taguel"] = {"progression": 0}

                    if yarne_father != "Robin":
                        item_config["Yarne's Tactician"] = {"progression": 0}
                        item_config["Yarne's Grandmaster"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Frederick", "Stahl", "Ricken"}:
                        item_config["Yarne's Paladin"] = {"progression": 0}
                        item_config["Yarne's Cavalier"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Kellam"}:
                        item_config["Yarne's Great Knight"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Yarne's Knight"] = {"progression": 0}
                        item_config["Yarne's General"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor"}:
                        item_config["Yarne's Swordmaster"] = {"progression": 0}
                        item_config["Yarne's Myrmidon"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Vaike", "Donnel"}:
                        item_config["Yarne's Fighter"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Vaike", "Donnel", "Gregor"}:
                        item_config["Yarne's Hero"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Yarne's Mercenary"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Donnel", "Gregor", "Virion", "Stahl", "Ricken"}:
                        item_config["Yarne's Bow Knight"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Virion", "Stahl", "Ricken"}:
                        item_config["Yarne's Archer"] = {"progression": 0}
                        item_config["Yarne's Sniper"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Frederick", "Virion", "Lon'qu"}:
                        item_config["Yarne's Wyvern Rider"] = {"progression": 0}
                        item_config["Yarne's Wyvern Lord"] = {"progression": 0}
                        item_config["Yarne's Griffon Rider"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Libra", "Henry"}:
                        item_config["Yarne's Sorcerer"] = {"progression": 0}
                        item_config["Yarne's Dark Mage"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Virion", "Ricken", "Libra", "Henry"}:
                        item_config["Yarne's Dark Knight"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Virion", "Ricken", "Libra"}:
                        item_config["Yarne's Mage"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Virion", "Ricken", "Libra", "Kellam"}:
                        item_config["Yarne's Sage"] = {"progression": 0}

                    if yarne_father not in {"Robin", "Kellam", "Libra"}:
                        item_config["Yarne's Priest"] = {"progression": 0}
                        item_config["Yarne's War Monk"] = {"progression": 0}

                    if yarne_father != "Donnel":
                        item_config["Yarne's Villager"] = {"progression": 0}  

                    if laurent_father != "Robin":
                        item_config["Laurent's Tactician"] = {"progression": 0}
                        item_config["Laurent's Grandmaster"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Frederick", "Stahl", "Ricken"}:
                        item_config["Laurent's Paladin"] = {"progression": 0}
                        item_config["Laurent's Cavalier"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Kellam"}:
                        item_config["Laurent's Great Knight"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Laurent's Knight"] = {"progression": 0}
                        item_config["Laurent's General"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor"}:
                        item_config["Laurent's Swordmaster"] = {"progression": 0}
                        item_config["Laurent's Myrmidon"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor", "Vaike", "Kellam", "Gaius", "Henry"}:
                        item_config["Laurent's Assassin"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Laurent's Thief"] = {"progression": 0}
                        item_config["Laurent's Trickster"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Vaike", "Donnel"}:
                        item_config["Laurent's Fighter"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Vaike", "Donnel", "Gregor"}:
                        item_config["Laurent's Hero"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Laurent's Mercenary"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Donnel", "Gregor", "Virion", "Stahl", "Ricken"}:
                        item_config["Laurent's Bow Knight"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Virion", "Stahl", "Ricken"}:
                        item_config["Laurent's Archer"] = {"progression": 0}
                        item_config["Laurent's Sniper"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Frederick", "Virion", "Lon'qu"}:
                        item_config["Laurent's Wyvern Rider"] = {"progression": 0}
                        item_config["Laurent's Wyvern Lord"] = {"progression": 0}
                        item_config["Laurent's Griffon Rider"] = {"progression": 0}

                    if laurent_father not in {"Robin", "Kellam", "Libra"}:
                        item_config["Laurent's Priest"] = {"progression": 0}
                        item_config["Laurent's War Monk"] = {"progression": 0}

                    if laurent_father != "Donnel":
                        item_config["Laurent's Villager"] = {"progression": 0}  

                    if noire_father != "Robin":
                        item_config["Noire's Tactician"] = {"progression": 0}
                        item_config["Noire's Grandmaster"] = {"progression": 0}

                    if noire_father not in {"Robin", "Frederick", "Stahl", "Ricken"}:
                        item_config["Noire's Paladin"] = {"progression": 0}
                        item_config["Noire's Cavalier"] = {"progression": 0}

                    if noire_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor"}:
                        item_config["Noire's Swordmaster"] = {"progression": 0}
                        item_config["Noire's Myrmidon"] = {"progression": 0}

                    if noire_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor", "Vaike", "Kellam", "Gaius", "Henry"}:
                        item_config["Noire's Assassin"] = {"progression": 0}

                    if noire_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Noire's Thief"] = {"progression": 0}
                        item_config["Noire's Trickster"] = {"progression": 0}

                    if noire_father not in {"Robin", "Vaike", "Donnel", "Gregor"}:
                        item_config["Noire's Hero"] = {"progression": 0}

                    if noire_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Noire's Mercenary"] = {"progression": 0}

                    if noire_father not in {"Robin", "Donnel", "Gaius"}:
                        item_config["Noire's Pegasus Knight"] = {"progression": 0}
                        item_config["Noire's Falcon Knight"] = {"progression": 0}
                        item_config["Noire's Dark Flier"] = {"progression": 0}

                    if noire_father not in {"Robin", "Frederick", "Virion", "Lon'qu"}:
                        item_config["Noire's Wyvern Rider"] = {"progression": 0}
                        item_config["Noire's Wyvern Lord"] = {"progression": 0}
                        item_config["Noire's Griffon Rider"] = {"progression": 0}

                    if noire_father not in {"Robin", "Virion", "Ricken", "Libra"}:
                        item_config["Noire's Mage"] = {"progression": 0}

                    if noire_father not in {"Robin", "Virion", "Ricken", "Libra", "Kellam"}:
                        item_config["Noire's Sage"] = {"progression": 0}

                    if noire_father not in {"Robin", "Kellam", "Libra"}:
                        item_config["Noire's Cleric"] = {"progression": 0}
                        item_config["Noire's War Cleric"] = {"progression": 0}

                    if noire_father not in {"Robin", "Donnel", "Gregor", "Henry"}:
                        item_config["Noire's Troubadour"] = {"progression": 0}
                        item_config["Noire's Valkyrie"] = {"progression": 0}  

                    if nah_father != "Robin":
                        item_config["Nah's Tactician"] = {"progression": 0}
                        item_config["Nah's Grandmaster"] = {"progression": 0}

                    if nah_father not in {"Robin", "Frederick", "Stahl", "Ricken"}:
                        item_config["Nah's Paladin"] = {"progression": 0}
                        item_config["Nah's Cavalier"] = {"progression": 0}

                    if nah_father not in {"Robin", "Frederick", "Stahl", "Ricken", "Kellam"}:
                        item_config["Nah's Great Knight"] = {"progression": 0}

                    if nah_father not in {"Robin", "Frederick", "Kellam"}:
                        item_config["Nah's Knight"] = {"progression": 0}
                        item_config["Nah's General"] = {"progression": 0}

                    if nah_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor"}:
                        item_config["Nah's Swordmaster"] = {"progression": 0}
                        item_config["Nah's Myrmidon"] = {"progression": 0}

                    if nah_father not in {"Robin", "Stahl", "Lon'qu", "Gaius", "Gregor", "Vaike", "Kellam", "Gaius", "Henry"}:
                        item_config["Nah's Assassin"] = {"progression": 0}

                    if nah_father not in {"Robin", "Vaike", "Kellam", "Lon'qu", "Gaius", "Henry"}:
                        item_config["Nah's Thief"] = {"progression": 0}
                        item_config["Nah's Trickster"] = {"progression": 0}

                    if nah_father not in {"Robin", "Vaike", "Donnel", "Gregor"}:
                        item_config["Nah's Hero"] = {"progression": 0}

                    if nah_father not in {"Robin", "Donnel", "Gregor"}:
                        item_config["Nah's Mercenary"] = {"progression": 0}

                    if nah_father not in {"Robin", "Donnel", "Gregor", "Virion", "Stahl", "Ricken"}:
                        item_config["Nah's Bow Knight"] = {"progression": 0}

                    if nah_father not in {"Robin", "Virion", "Stahl", "Ricken"}:
                        item_config["Nah's Archer"] = {"progression": 0}
                        item_config["Nah's Sniper"] = {"progression": 0}

                    if nah_father not in {"Robin", "Donnel", "Gaius"}:
                        item_config["Nah's Pegasus Knight"] = {"progression": 0}
                        item_config["Nah's Falcon Knight"] = {"progression": 0}
                        item_config["Nah's Dark Flier"] = {"progression": 0}

                    if nah_father not in {"Robin", "Libra", "Henry"}:
                        item_config["Nah's Sorcerer"] = {"progression": 0}
                        item_config["Nah's Dark Mage"] = {"progression": 0}

                    if nah_father not in {"Robin", "Kellam", "Libra"}:
                        item_config["Nah's Cleric"] = {"progression": 0}
                        item_config["Nah's War Cleric"] = {"progression": 0}

                    if nah_father not in {"Robin", "Donnel", "Gregor", "Henry"}:
                        item_config["Nah's Troubadour"] = {"progression": 0}
                        item_config["Nah's Valkyrie"] = {"progression": 0}  

                    StartClass = is_option_enabled(multiworld, player, "Character_Specific_Classes_Include_Start_Class")

                    if not StartClass:
                        if morgan_mother in {"Olivia", "Lucina"}:
                            item_config["Morgan's Tactician"] = {"progression": 0}

                        if morgan_father in {"Chrom", "Walhart"}:
                            item_config["Morgan's Tactician"] = {"progression": 0}

                        if morgan_mother in {"Lissa", "Emmeryn"}:
                            item_config["Morgan's Cleric"] = {"progression": 0}

                        if morgan_father in {"Frederick", "Stahl"}:
                            item_config["Morgan's Cavalier"] = {"progression": 0}

                        if morgan_mother == "Sully":
                            item_config["Morgan's Cavalier"] = {"progression": 0}

                        if morgan_father == "Virion":
                            item_config["Morgan's Archer"] = {"progression": 0}

                        if morgan_mother == "Noire":
                            item_config["Morgan's Archer"] = {"progression": 0}

                        if morgan_father in {"Vaike", "Basilio"}:
                            item_config["Morgan's Fighter"] = {"progression": 0}

                        if morgan_father in {"Ricken", "Laurent"}:
                            item_config["Morgan's Mage"] = {"progression": 0}

                        if morgan_mother == "Miriel":
                            item_config["Morgan's Mage"] = {"progression": 0}

                        if morgan_mother in {"Sumia", "Cordelia", "Aversa", "Cynthia"}:
                            item_config["Morgan's Pegasus Knight"] = {"progression": 0}

                        if morgan_mother == "Kjelle":
                            item_config["Morgan's Knight"] = {"progression": 0}

                        if morgan_father == "Kellam":
                            item_config["Morgan's Knight"] = {"progression": 0}

                        if morgan_father == "Donnel":
                            item_config["Morgan's Villager"] = {"progression": 0}

                        if morgan_father in {"Lon'qu", "Yen'fay", "Owain"}:
                            item_config["Morgan's Myrmidon"] = {"progression": 0}

                        if morgan_mother == "Say'ri":
                            item_config["Morgan's Myrmidon"] = {"progression": 0}

                        if morgan_mother == "Maribelle":
                            item_config["Morgan's Troubadour"] = {"progression": 0}

                        if taguel_parent:
                            item_config["Morgan's Taguel"] = {"progression": 0}

                        if morgan_father in {"Gaius", "Gangrel"}:
                            item_config["Morgan's Thief"] = {"progression": 0}

                        if morgan_mother == "Anna":
                            item_config["Morgan's Thief"] = {"progression": 0}

                        if morgan_father in {"Gregor", "Priam", "Inigo"}:
                            item_config["Morgan's Mercenary"] = {"progression": 0}

                        if morgan_mother in {"Flavia", "Severa"}:
                            item_config["Morgan's Mercenary"] = {"progression": 0}

                        if morgan_mother in {"Nowi", "Tiki", "Nah"}:
                            item_config["Morgan's Manakete"] = {"progression": 0}

                        if morgan_father in {"Libra", "Brady"}:
                            item_config["Morgan's Priest"] = {"progression": 0}

                        if morgan_mother == "Tharja":
                            item_config["Morgan's Dark Mage"] = {"progression": 0}

                        if morgan_father == "Henry":
                            item_config["Morgan's Dark Mage"] = {"progression": 0}

                        if morgan_mother == "Cherche":
                            item_config["Morgan's Wyvern Rider"] = {"progression": 0}

                        if morgan_father == "Gerome":
                            item_config["Morgan's Wyvern Rider"] = {"progression": 0}

    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names
     
    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        remove_specific_item(item_pool, item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # remove_specific_item(item_pool, item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass

def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, Any]) -> dict[str, Any]:
    """
        Called when Universal Tracker wants to perform a fake generation
        Use this if you want to use or modify the slot_data for passed into re_gen_passthrough
    """
    return slot_data
