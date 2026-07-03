# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
class TotalCharactersToWinWith(Range):
    """Instead of having to beat the game with all characters, you can limit locations to a subset of character victory locations."""
    display_name = "Number of characters to beat the game with before victory"
    range_start = 10
    range_end = 50
    default = 50

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
from Options import OptionSet
from ..Items import item_name_groups

class ManualPairing(OptionSet):
  """Name the Pairs you wish to have in the game. Make sure to remove the Robin Pair for the gender you do not wish to play as. The items need to be named 'MOTHER x FATHER'. Make this blank if you intend to use randomized pairings."""           # Description of the yaml option in the template
  display_name = "Manual Pairing"                              # Name of the option in the spoiler
  valid_keys = item_name_groups["Character Pairings"]          # This is the bit that matters.  Our yaml option wants you to pick names of items in the Character Pairings category
  default = ["Sumia x Chrom", "Robin x Gregor", "Lucina x Robin", "Lissa x Frederick", "Olivia x Virion", "Maribelle x Stahl", "Sully x Henry", "Cordelia x Vaike", "Cherche x Kellam", "Panne x Lon'qu", "Miriel x Ricken", "Tharja x Gaius", "Nowi x Donnel"]
  group = "Child Options"

def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["Manual_Pairing"] = ManualPairing  # This registers the yaml option as `Manual_Pairing`
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options

    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
