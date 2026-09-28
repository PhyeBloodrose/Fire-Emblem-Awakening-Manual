from typing import Optional, Any
from BaseClasses import MultiWorld


# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the category, False to disable it, or None to use the default behavior
def before_is_category_enabled(multiworld: MultiWorld, player: int, category_name: str) -> Optional[bool]:
    from ..Helpers import get_option_value

    sanity = get_option_value(multiworld, player, "EnemySanity")
    
    if category_name == "EnemySanity":
        return 1 <= sanity <= 3

    if category_name == "EnemySanityHard":
        return 2 <= sanity <= 3

    if category_name == "EnemySanityLuna":
        return sanity == 3

    if category_name == "EnemySanityType":
        return sanity == 4

    enabled_dlc = get_option_value(multiworld, player, "Enabled_DLC")
    
    from ..Items import item_name_groups
    if category_name in item_name_groups["Xenologue Chapters"]:
        return category_name in enabled_dlc

    if category_name == "MadKingGoal":
        return get_option_value(multiworld, player, "Main_Goal") == 0

    if category_name == "GrimaGoal":
        return get_option_value(multiworld, player, "Main_Goal") == 1

    if category_name == "MadKingDisabled":
        return get_option_value(multiworld, player, "Main_Goal") >= 1

    if category_name == "Character Pairs":
        return get_option_value(multiworld, player, "Main_Goal") >= 1

    if category_name == "Seals":
        return get_option_value(multiworld, player, "Add_Seals") == 1

    if category_name == "CharaSeals":
        return get_option_value(multiworld, player, "Add_Seals") == 2

    classes = get_option_value(multiworld, player, "Randomized_Classes")

    from ..Helpers import is_option_enabled
    child = is_option_enabled(multiworld, player, "Enable_Children")
    
    if category_name == "ClassGenericBase":
        return classes == 1 or classes == 3

    if category_name == "ClassGenericPromo":
        return classes == 2 or classes == 3

    if category_name == "ClassChara":
        return classes >= 4

    if category_name == "ClassCharaChild":
        return classes >= 4 and child

    if category_name == "StartClass":
        return classes >= 5

    levelup = get_option_value(multiworld, player, "LevelUpSanity")
    
    if category_name == "LevelUpSanity":
        return 1 <= levelup <= 2

    if category_name == "LevelUpSanityPromo":
        return levelup == 2

    if category_name == "LevelUpTwenty":
        return levelup >= 3

    if category_name == "LevelUpMax":
        return levelup == 4

    return None

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the item, False to disable it, or None to use the default behavior
def before_is_item_enabled(multiworld: MultiWorld, player: int, item:  dict[str, Any]) -> Optional[bool]:
    # Remove unwanted dlc from the item pool
    return None

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the location, False to disable it, or None to use the default behavior
def before_is_location_enabled(multiworld: MultiWorld, player: int, location:  dict[str, Any]) -> Optional[bool]:
    return None

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the event, False to disable it, or None to use the default behavior
def before_is_event_enabled(multiworld: MultiWorld, player: int, event:  dict[str, Any]) -> Optional[bool]:
    return None
