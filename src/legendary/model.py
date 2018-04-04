'''
The model module holds the class definitions for the various components of a
Legendary set. Each component holds the meta data about the card or card group
that would assist a decision engine in makeing a choice.
'''

# core libraries
from enum import Enum
import json
from abc import ABC

class CardClass(Enum):
    '''
    An enum to establish the card classes (colors) as denoted as the second icon
    down in the top right of the card.
    '''
    GREY = 1
    RED = 2
    YELLOW = 3
    GREEN = 4
    BLUE = 5
    BLACK = 6

class CardGroup(ABC):
    '''
    Base class for all card and card group classes defined in the model. This
    handles the Legendary "set," unique ID (within the card group), and name.
    '''
    def __init__(self, legendary_set, identity, name):
        '''
        Constructor called by subclasses.

        :param legendary_set:   the Legendary set this card or card group is
                                from
        :param identity:        the ID of this card or card group
        :param name:            the name of the card or card group as seen in
                                the title on the card
        '''
        self._legendary_set = legendary_set
        self._identity = identity
        self._name = name

    @property
    def legendary_set(self):
        '''
        Return the set of Legendary this card or card group is from.
        '''
        return self._legendary_set

    @property
    def identity(self):
        '''
        Return the ID of this card or card group.
        '''
        return self._identity

    @property
    def name(self):
        '''
        Return the name of this card or card group.
        '''
        return self._name

    def to_dict(self):
        '''
        Produce the dictionary data for saving.
        '''
        return {"legendary_set": self._legendary_set,
                "identity": self._identity,
                "name": self._name}

    @classmethod
    def from_json(cls, data):
        '''
        Construct a Scheme object from a JSON representation.
        '''
        return cls(**json.loads(data))

class Scheme(CardGroup):
    '''
    The Scheme class is a value object that encapsulates the common information
    for schemes.
    '''
    def __init__(self, twist_count=8, retributions=None, **kwargs):
        '''
        Construct the Mastermind object with the mastermind-specific attributes,
        then dish the rest up to the base class.

        :param twist_count:     the number of scheme twists to include in the
                                villain deck as dictated by this scheme
        :param retributions:    a list of retributions (enums from the legendary
                                set) the scheme takes
        '''
        super().__init__(**kwargs)
        self._twist_count = twist_count
        self._retributions = retributions or []

    @property
    def twist_count(self):
        '''
        Return the number of twists this scheme dictates should be in the
        villain deck.
        '''
        return self._twist_count

    @property
    def retributions(self):
        '''
        Return list of retributions (enums from the legendary set) the scheme
        takes.
        '''
        return self._retributions

    def to_dict(self):
        '''
        Produce the dictionary data for saving.
        '''
        retributions = [retribution.value for retribution in self._retributions]
        return dict(super().to_dict(), **{"twist_count": self._twist_count,
                                          "retributions": retributions})

forge_crime_syndicate = Scheme(legendary_set="big_trouble", identity=1, name="Forge Crime Syndicate", retributions=["discard", "villain_deck_draw"])
rampage_for_sacrifices = Scheme(legendary_set="big_trouble", identity=2, name="Rampage for Sacrifices", twist_count=10, retributions=["lose_vp", "stronger_villains", "capture_bystanders", "villain_deck_draw"])
flood_chinatown_in_mediocrity = Scheme(legendary_set="big_trouble", identity=3, name="Flood Chinatown in Mediocrity", twist_count=10, retributions=["gain_grey_heroes", "villain_deck_draw"])
kill_uncle_shu = Scheme(legendary_set="big_trouble", identity=4, name="Kill Uncle Chu", retributions=["stronger_villains", "villain_deck_draw"])
corrupt_true_heroes = Scheme(legendary_set="big_trouble", identity=5, name="Corrupt True Heroes", twist_count=10, retributions=["stronger_villains", "destroy_library", "villain_deck_draw"])
assassination = Scheme(legendary_set="big_trouble", identity=6, name="Assassination", retributions=["destroy_library", "villain_deck_draw"])
destroy_chinatowns_dreams = Scheme(legendary_set="big_trouble", identity=7, name="Destroy Chinatown's Dreams", retributions=["villain_deck_draw", "capture_bystanders", "ko_bystander"])
fill_the_hell = Scheme(legendary_set="big_trouble", identity=8, name="Fill the Hell of Upside Down Sinners", retributions=["destroy_library", "villain_deck_draw"])
enforce_villainous_hierarchy = Scheme(legendary_set="big_trouble", identity=9, name="Enforce Villainous Hierarchy", retributions=["villain_deck_draw"])
ruin_san_fran = Scheme(legendary_set="big_trouble", identity=10, name="Ruin San Fran", twist_count=7, retributions=["stronger_villains"])
open_the_hell_gates = Scheme(legendary_set="big_trouble", identity=11, name="Open the Hell Gates")
one_and_the_same = Scheme(legendary_set="big_trouble", identity=12, name="One and the Same Person, Jack", twist_count=10, retributions=["villain_deck_draw"])

# hellmouth_opening = Scheme(legendary_set="buffy", identity=1, name="Hellmouth Opening")
# dict_repr = hellmouth_opening.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))
# convert_to_evil = Scheme(legendary_set="buffy", identity=2, name="Convert to Evil")
# dict_repr = convert_to_evil.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))
# summon_the_uber_vamps = Scheme(legendary_set="buffy", identity=3, name="Summon the Uber Vamps")
# dict_repr = summon_the_uber_vamps.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))
# twilight_terror = Scheme(legendary_set="buffy", identity=4, name="Twilight Terror")
# dict_repr = twilight_terror.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))
# vile_agenda = Scheme(legendary_set="buffy", identity=5, name="Vile Agenda")
# dict_repr = vile_agenda.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))
# road_to_damnation = Scheme(legendary_set="buffy", identity=6, name="Road to Damnation")
# dict_repr = road_to_damnation.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))
# epic_struggle = Scheme(legendary_set="buffy", identity=7, name="Epic Struggle")
# dict_repr = epic_struggle.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))
# darkness_falls = Scheme(legendary_set="buffy", identity=8, name="Darkness Falls")
# dict_repr = darkness_falls.to_dict()
# new = Scheme.from_json(json.dumps(dict_repr))

class EvilCardGroup(CardGroup):
    '''
    The EvilCardGroup class is the parent class of masterminds, villains, and
    henchmen. This encapsulates the common information across all three, such as
    attack power, the retributions that can be averted by the presence of teams
    and/or colors, etc.
    '''
    def __init__(self, attack_power, team_requirements=None, class_requirements=None, retributions=None, **kwargs):
        '''
        Construct an EvilCardGroup object with the attributes set here, then
        dish the rest up to the base class.

        :param attack_power:        the attack power as printed on the
                                    mastermind (main) card
        :param team_requirements:   a dictionary pairing a team (an enum value
                                    from the legendary set) with a retribution
                                    (also enum from the legendary set) that can
                                    be averted by its presence
        :param class_requirements:  a dictionary pairing a class (color) with a
                                    retribution (an enum from the legendary set)
                                    that can be averted by its presence
        :param retributions:        a list of retributions (enums from the
                                    legendary set) the evil card group takes
        '''
        super().__init__(**kwargs)
        self._attack_power = attack_power
        self._team_requirements = team_requirements or {}
        self._class_requirements = class_requirements or {}
        self._retributions = retributions or []

    @property
    def attack_power(self):
        '''
        Return the attack power of the card (or the total attack power across
        the card group).
        '''
        return self._attack_power

    @property
    def team_requirements(self):
        '''
        Return the dictionary pairing teams with the retribution that can be
        averted by their presence.
        '''
        return self._team_requirements

    @property
    def class_requirements(self):
        '''
        Return the dictionary pairing classes (colors) with the retribution that
        can be averted by their presence.
        '''
        return self._class_requirements

    @property
    def retributions(self):
        '''
        Return list of retributions (enums from the legendary set) the card or
        card group takes.
        '''
        return self._retributions

    def to_dict(self):
        '''
        Produce the dictionary data for saving.
        '''
        team_reqs = {key.value: value for key, value in self._team_requirements.items()}
        class_reqs = {key.value: value for key, value in self._class_requirements.items()}
        retributions = [retribution.value for retribution in self._retributions]
        return dict(super().to_dict(), **{"attack_power": self._attack_power,
                                          "team_requirements": team_reqs,
                                          "class_requirements": class_reqs,
                                          "retributions": retributions})

class Mastermind(EvilCardGroup):
    '''
    The Mastermind class is a value object that encapsulates the common
    information for masterminds.
    '''
    pass

six_shooter = Mastermind(legendary_set="big_trouble", identity=1, name="Six Shooter", attack_power=7, class_requirements={"6": "wound", "5": "wound"}, retributions=["lose_vp", "capture_bystanders"])
ching_dai = Mastermind(legendary_set="big_trouble", identity=2, name="Ching Dai", attack_power=8, retributions=["ko_grey_heroes", "wound", "villain_deck_draw", "gain_grey_heroes", "ko_non_grey_heroes"])
david_lo_pan = Mastermind(legendary_set="big_trouble", identity=3, name="David Lo Pan", attack_power=9, retributions=["discard", "wound"])
sorcerous_lo_pan = Mastermind(legendary_set="big_trouble", identity=4, name="Sorcerous Lo Pan", attack_power=10, retributions=["villain_deck_draw", "add_tactic", "ko_non_grey_heroes"])

# the_master = Mastermind(legendary_set="buffy", identity=1, name="The Master", attack_power=7, retributions=["villain_deck_draw", "light/dark", "discard"])
# dict_repr = the_master.to_dict()
# new = Mastermind.from_json(json.dumps(dict_repr))
# glorificus = Mastermind(legendary_set="buffy", identity=2, name="Glorificus", attack_power=8, retributions=["capture_bystanders", "wound"])
# dict_repr = glorificus.to_dict()
# new = Mastermind.from_json(json.dumps(dict_repr))
# the_mayor = Mastermind(legendary_set="buffy", identity=3, name="The Mayor", attack_power=8, retributions=["ko_grey_heroes", "wound", "courage_token", "lose_vp", "discard", "light/dark"])
# dict_repr = the_mayor.to_dict()
# new = Mastermind.from_json(json.dumps(dict_repr))
# angelus = Mastermind(legendary_set="buffy", identity=4, name="Angelus", attack_power=9, team_requirements={"slayers": "wound"}, retributions=["wound", "light/dark", "courage_token"])
# dict_repr = angelus.to_dict()
# new = Mastermind.from_json(json.dumps(dict_repr))
# the_first = Mastermind(legendary_set="buffy", identity=5, name="The First", attack_power=8, retributions=["villain_deck_draw", "destroy_library"])
# dict_repr = the_first.to_dict()
# new = Mastermind.from_json(json.dumps(dict_repr))

class VillainGroup(EvilCardGroup):
    '''
    The VillainGroup class is a value object that encapsulates the common
    information for a villain group - the eight villain cards with the same
    group name.
    '''
    def __init__(self, ambush_count=0, fight_count=0, escape_count=0, **kwargs):
        '''
        Construct the VillainGroup object with the villain-specific attributes,
        then dish the rest up to the base class.

        :param ambush_count:    the number of cards in the villain group with an
                                ambush effect
        :param fight_count:     the number of cards in the villain group with a
                                fight effect
        :param escape_count:    the number of cards in the villain group with an
                                escape effect
        '''
        super().__init__(**kwargs)
        self._ambush_count = ambush_count
        self._fight_count = fight_count
        self._escape_count = escape_count

    @property
    def ambush_count(self):
        '''
        Return the number of cards in this villain group with ambush effects.
        '''
        return self._ambush_count

    @property
    def fight_count(self):
        '''
        Return the number of cards in this villain group with fight effects.
        '''
        return self._fight_count

    @property
    def escape_count(self):
        '''
        Return the number of cards in this villain group with escape effects.
        '''
        return self._escape_count

    def to_dict(self):
        '''
        Produce the dictionary data for saving.
        '''
        return dict(super().to_dict(), **{"ambush_count": self._ambush_count,
                                          "fight_count": self._fight_count,
                                          "escape_count": self._escape_count})

wing_kong_gang = VillainGroup(legendary_set="big_trouble", identity=1, name="Wing Kong Gang", attack_power=38, ambush_count=4, fight_count=4, escape_count=0, retributions=["wound", "ko_attack", "destroy_library", "capture_bystanders"])
monsters = VillainGroup(legendary_set="big_trouble", identity=2, name="Monsters", attack_power=40, ambush_count=4, fight_count=0, escape_count=6, retributions=["add_tactic", "ko_cards", "lose_vp", "ko_attack", "villain_deck_draw"])
wing_kong_exchange = VillainGroup(legendary_set="big_trouble", identity=3, name="Wing Kong Exchange", attack_power=38, ambush_count=0, fight_count=6, escape_count=0, retributions=["discard", "ko_heroes"])
warriors_of_lo_pan = VillainGroup(legendary_set="big_trouble", identity=4, name="Warriors of Lo Pan", attack_power=46, ambush_count=8, fight_count=2, escape_count=6, class_requirements={"5": "wound"}, retributions=["discard"])

# order_of_aurelius = VillainGroup(legendary_set="buffy", identity=1, name="Order of Aurelius", attack_power=35, ambush_count=3, fight_count=3, escape_count=1, retributions=["light/dark", "discard"])
# dict_repr = order_of_aurelius.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# glorys_minions = VillainGroup(legendary_set="buffy", identity=2, name="Glory's Minions", attack_power=32, ambush_count=6, fight_count=3, escape_count=4, retributions=["light/dark", "capture_bystanders", "villain_deck_draw"])
# dict_repr = glorys_minions.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# mayors_minions = VillainGroup(legendary_set="buffy", identity=3, name="Mayor's Minions", attack_power=40, ambush_count=8, fight_count=8, escape_count=2, retributions=["wound", "light/dark"])
# dict_repr = mayors_minions.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# scourge_of_europe = VillainGroup(legendary_set="buffy", identity=4, name="Scourge of Europe", attack_power=37, ambush_count=8, fight_count=6, escape_count=1, team_requirements={"slayers": "light/dark"}, retributions=["discard", "light/dark", "capture_hero", "ko_bystander"])
# dict_repr = scourge_of_europe.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# the_firsts_minions = VillainGroup(legendary_set="buffy", identity=5, name="The First's Minions", attack_power=40, ambush_count=6, fight_count=0, escape_count=4, retributions=["wound", "light/dark", "villain_deck_draw", "ko_grey_heroes"])
# dict_repr = the_firsts_minions.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# demons = VillainGroup(legendary_set="buffy", identity=6, name="Demons", attack_power=40, ambush_count=6, fight_count=6, escape_count=0, retributions=["light/dark", "card_exchange", "wound", "ko"])
# dict_repr = demons.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# harmonys_gang = VillainGroup(legendary_set="buffy", identity=7, name="Harmony's Gang", attack_power=38, ambush_count=8, fight_count=4, escape_count=4, class_requirements={CardClass.RED: "wound", CardClass.GREEN: "wound", CardClass.BLACK: "courage_token", CardClass.YELLOW: "courage_token"})
# dict_repr = harmonys_gang.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))

class HenchmenGroup(EvilCardGroup):
    '''
    The HenchmenGroup class is a value object that encapsulates the common
    information for a henchmen villain group - the ten henchman villain cards
    with the same group name.
    '''
    pass

lords_of_death = HenchmenGroup(legendary_set="big_trouble", identity=1, name="Lords of Death", attack_power=30, retributions=["wound"])
ceremonial_warriors = HenchmenGroup(legendary_set="big_trouble", identity=2, name="Ceremonial Warriors", attack_power=30)
wing_kong_thugs = HenchmenGroup(legendary_set="big_trouble", identity=3, name="Wing Kong Thugs", attack_power=30, retributions=["ko_purchase"])

# henchmen = []
# turok_han_vampires = HenchmenGroup(legendary_set="buffy", identity=1, name="Turok-Han Vampires", attack_power=50, retributions=["courage_token"])
# henchmen.append(turok_han_vampires)
# dict_repr = turok_han_vampires.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# vampire_initiate = HenchmenGroup(legendary_set="buffy", identity=2, name="Vampire Initiate", attack_power=30, retributions=["capture_bystanders"])
# henchmen.append(vampire_initiate)
# dict_repr = vampire_initiate.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# shark_gangsters = HenchmenGroup(legendary_set="buffy", identity=3, name="Shark Gangsters", attack_power=40, retributions=["courage_token"])
# henchmen.append(shark_gangsters)
# dict_repr = shark_gangsters.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# harbingers_of_death = HenchmenGroup(legendary_set="buffy", identity=4, name="Harbingers of Death", attack_power=40, retributions=["light/dark"])
# henchmen.append(harbingers_of_death)
# dict_repr = harbingers_of_death.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))
# hellhounds = HenchmenGroup(legendary_set="buffy", identity=5, name="Hellhounds", attack_power=30, retributions=["light/dark"])
# henchmen.append(hellhounds)
# dict_repr = hellhounds.to_dict()
# new = VillainGroup.from_json(json.dumps(dict_repr))

# henchmen_data = [henchman.to_dict() for henchman in henchmen]
# print(henchmen_data)
