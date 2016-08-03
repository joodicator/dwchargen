#===============================================================================
from itertools import *
import random
import string
import math
import re

import fantasynamegenerators as fantasy
import dungeon_world_base as base
import utility as util

#-------------------------------------------------------------------------------
class Char(base.Char):
    def set_random(self):
        super(Char, self).__init__()

        self.abilities = Abilities.new_random()

        self.class_ = Class.new_random(self)
        self.race = Race.new_random(self)

        self.class_.apply(self)
        self.race.apply(self)

        self.class_.apply_random(self)
        self.race.apply_random(self)

class Abilities(base.Abilities, util.Random):
    def set_random(self):
        scores = [16, 15, 13, 12, 9, 8]
        random.shuffle(scores)
        for ability, score in izip(self.ability_names, scores):
            self.set_ability_score(ability, score)

class Item(base.Item, util.Registry):
    pass

class Item_Uses(Item, util.AbstractSubRegistry):
    __slots__ = 'default_uses', 'uses_per_weight'
    def __init__(self, uses=None, *args, **kwds):
        if uses is None:
            uses = self.default_uses
        elif type(uses) is not tuple:
            uses = (uses, uses)
        if 'weight' not in kwds:
            kwds['weight'] = math.ceil(
                float(uses[0]) / float(self.uses_per_weight))
        super(Item_Uses, self).__init__(
            uses=uses, *args, **kwds)

class Item_Toolbox(Item_Uses):
    name = 'Toolbox'
    default_uses = (5, 5)
    uses_per_weight = 2.5

class Item_Rations(Item_Uses):
    name = 'Rations'
    default_uses = (5, 5)
    uses_per_weight = 5

class Item_HealingHerbs(Item_Uses):
    name = 'Healing herbs'
    default_uses = (2, 2)
    uses_per_weight = 2
    tags = { 'slow':True }

class Item_Medkit(Item_Uses):
    name = 'Medkit'
    default_uses = (3, 3)
    uses_per_weight = 3
    tags = { 'slow':True }

class Item_Antitoxin(Item):
    name = 'Antitoxin'
    tags = { 'weight':0 }

class Item_PersonalCommunicator(Item):
    name = 'Personal communicator'
    tags = { 'weight':0 }

class Item_Clothes(Item):
    name = 'Clothes'
    tags = { 'weight':0 }

class Item_TribalArmour(Item):
    name = 'Tribal armour'
    tags = { 'weight':1, 'armour':1 }

class Item_BodyArmour(Item):
    name = 'Body armour'
    tags = { 'weight':2, 'armour':2 }

class Item_BallisticVest(Item):
    name = 'Ballistic vest'
    tags = { 'weight':1, 'armour':1 }

class Item_CombatKnife(Item):
    name = 'Combat knife'
    tags = { 'weight':1, 'hand':True }

class Item_StunBaton(Item):
    name = 'Stun baton'
    tags = { 'weight':1, 'hand':True, 'stun':True, 'piercing':1 }

class Item_AssaultRifle(Item):
    name = 'Assault rifle'
    tags = { 'weight':2, 'near':True, 'far':True,
             'two-handed':True, 'automatic':True }

class Item_LaserRifle(Item):
    name = 'Laser rifle'
    tags = { 'weight':2, 'near':True, 'far':True,
             'piercing':2, 'two-handed':True }

class Item_LaserPistol(Item):
    name = 'Laser pistol'
    tags = { 'weight':1, 'near':True, 'piercing':2 }

class Item_StunPistol(Item):
    name = 'Stun pistol'
    tags = { 'weight':1, 'near':True, 'stun':True }

class Item_SilencedLaserPistol(Item):
    name = 'Silenced laser pistol'
    tags = { 'weight':1, 'near':True, 'silent':True }

class Item_StunGrenade(Item):
    name = 'Stun grenade'
    tags = { 'weight':0, 'near':True, 'thrown':True, 'stun':True }

class Item_FragGrenade(Item):
    name = 'Grenade'
    tags = { 'weight':0, 'near':True, 'thrown':True, 'area':True,
             'explosive':True, 'piercing':1, '+damage':2 }

class Item_Javelin(Item):
    name = 'Javelin'
    tags = { 'weight':1, 'close':True, 'thrown':True }

class Item_Machete(Item):
    name = 'Machete'
    tags = { 'weight':1, 'close':True }

class Item_RocketLauncher(Item):
    name = 'Rocket launcher'
    tags = { 'weight':3, 'near':True, 'far':True, 'reload':True }

class Item_Rocket(Item):
    name = 'Rocket'
    tags = { 'weight':1, '+damage':4, 'piercing':2,
              'area':True, 'explosive':True }

#===============================================================================
class Race(base.Race, util.Registry):
    pass

class Race_Human(Race):
    name = 'Human'
    frequency = 5
    def set_random(self, char):
        self.racial_move = Move_Human.new_random(char)
    def apply_random(self, char):
        char.name, char.gender = fantasy.random_name_gender(*(
            ['futuristic', 'human sw'] + getattr(self, 'human_name_types', [])))
        if char.gender is None:
            char.gender = random.choice(['male', 'female'])

class Move_Human(base.Move):
    __slots__ = 'extra_move'
    def __init__(self):
        super(Move_Human, self).__init__('Human', 'Take a starting move '
            'from a class nobody else is playing, or a level 2-5 advanced move '
            'from your own class.')
    def set_random(self, char):
        move_class = random.choice(
            [m for c in Class.classes if not isinstance(char.class_, c)
               for m in c.Move.classes if issubclass(m, base.Move_Starting)] +
            [m for m in char.class_.Move.classes
               if issubclass(m, base.Move_Advanced_2)])
        self.extra_move = move_class.new_random(char)
    def summarise_parenthetical(self):
        return 'gain %s' % self.extra_move.summarise_with_class()

class Race_Alien(Race, util.AbstractSubRegistry):
    def set_random(self, char):
        self.name = fantasy.random_name(*(
            ['alien'] + getattr(self, 'race_name_types', [])))
    def apply_random(self, char):
        while True:
            char.name, char.gender = fantasy.random_name_gender(*(
                ['alien', 'pet alien'] +
                getattr(self, 'char_name_types', [])))
            if self.name != char.name: break
        

class Race_Small(Race_Alien):
    racial_move = base.Move('Small', 'Your race is tiny. When you defy danger '
        'and use your small size to your advantage, take +1.')
    char_name_types = ['dwarf', 'hobbit', 'fairy', 'christmas elf']

class Race_Huge(Race_Alien):
    racial_move = base.Move('Huge', 'Your race is uncommonly large. You start '
        'with 3 more HP than normal.')
    char_name_types = ['giant', 'ogre', 'troll']
    def apply(self, char):
        super(Race_Huge, self).apply(char)
        char.max_hp += 3

class Race_Hardy(Race_Alien):
    race_name_types = ['mutant species']
    racial_move = base.Move('Hardy', 'Your race has adapted to a harmful '
        'environment. When you defy danger to resist poisons or '
        'disease, take +1.')

class Race_Flyer(Race_Alien):
    char_name_types = ['angel', 'griffin', 'harpy', 'pegasus', 'fairy']
    racial_move = base.Move('Flyer', 'Your race has wings (or some other '
        'natural method of flying) and can fly or float around freely '
        'in most atmospheres')

class Race_Climber(Race_Alien):
    racial_move = base.Move('Climber', 'Your race is naturally equipped to '
        'scale any solid surface easily.')
    char_name_types = ['star trek caitian']

class Race_Burrowing(Race_Alien):
    racial_move = base.Move('Burrowing', 'Your race is naturally equipped to '
        'dig through dirt and stone.')

class Race_Amphibian(Race_Alien):
    racial_move = base.Move('Amphibian', 'Your race is skilled at swimming and '
        'can breathe and move around effortlessly underwater.')
    char_name_types = ['mermaid']

class Race_Scaled(Race_Alien):
    racial_move = base.Move('Scaled', 'Your race is covered in tough scales. '
        'When you wear no armor, you have 2 armor anyways.')
    char_name_types = ['star trek saurian']

class Race_Chitinous(Race_Alien):
    racial_move = base.Move('Chitinous', 'Your race is protected by thick '
        'shells of bone. When you wear no armor, you have 2 armor '
        'anyways.')
    char_name_types = ['star trek jemhadar']

class Race_Clawed(Race_Alien):
    racial_move = base.Move('Clawed', 'Your race naturally has sharp claws. '
        'You may use them as a hand weapon, and they do +1 damage.')
    char_name_types = ['succubus', 'demon', 'star trek gorn']

class Race_Venomous(Race_Alien):
    racial_move = base.Move('Venomous', 'Your race has a set of venomous '
        'fangs. You may use them as a hand weapon, and in addition '
        'to damage they will poison the target.')
    char_name_types = ['star trek saurian', 'star trek gorn']

class Race_Acidic(Race_Alien):
    racial_move = base.Move('Acidic', "Your race's spit is a lethal, acidic "
        "weapon. You may use it as a near weapon with 1 piercing.")
    char_name_types = ['star trek saurian']

class Race_Vampiric(Race_Alien):
    racial_move = base.Move('Vampiric', 'Your race thrives on blood. When you '
        'consume fresh blood, take +1 forward and heal 1d4 damage.')
    char_name_types = ['vampire']

class Race_Hivemind(Race_Alien):
    racial_move = base.Move('Hivemind', 'You share a deep connection with those '
        'of your race. When nearby members of your race are in danger,'
        ' the GM will tell you this and where you feel it coming from.')

class Race_Phototroph(Race_Alien):
    racial_move = base.Move('Phototroph', 'Your race absorbs energy from light. '
        'When Making Camp in an area exposed to sunlight, you require '
        'no rations and take +1 forward.')
    char_name_types = ['ent']

class Race_Amorphous(Race_Alien):
    racial_move = base.Move('Amorphous', "Your race's strange alien bodies "
        "have no clearly-defined shape. You can squeeze into tight "
        "spaces and stretch out your form freely, but almost all worn "
        "equipment is useless to you.")

class Race_Tentacled(Race_Alien):
    racial_move = base.Move('Tentacled', 'Your race has many long prehensile '
        'limbs. Ignore the "two-handed" tag on weapons, and all your '
        'melee attacks have the "reach" range.')

class Race_Shifter(Race_Alien):
    char_name_types = ['shapeshifter']
    def set_random(self, char):
        super(Race_Shifter, self).set_random(char)
        self.racial_move = Move_Shifter.new_random(char)

class Move_Shifter(base.Move): 
    __slots__ = 'shift_condition', 'shift_race'
    def __init__(self):
        super(Move_Shifter, self).__init__('Shifter', 'Your race has '
            'evolved to shift uncontrollably into an almost completely '
            'different form under specific environmental conditions. Describe '
            'the conditions and choose a second racial move to represent the '
            'transformed state, and take +1 forward whenever you shift.')
    def set_random(self, char):
        self.shift_condition = random.choice((
            'in a vacuum', 'in low air pressure', 'in high air pressure',
            'immersed in liquid', 'wet', 'dry', 'in high temperatures',
            'in low temperatures', 'in bright light', 'in darkness',
            'inside a foreign organism', 'exposed to pathogenic microbes',
            'exposed to toxins', 'exposed to humans', 'exposed to loud noises',
            'exposed to air'))
        self.shift_race = Race.new_random(char)
    def summarise_parenthetical(self):
        return 'when %s: %s' % (
            self.shift_condition, self.shift_race.racial_move.summarise())

class Race_Parasitic(Race_Alien):
    racial_move = base.Move('Parasitic', "Your race is a parasite with the "
        "ability to control host bodies. When you inhabit a body, you'll gain "
        "an appropriate racial move as long as you control it. Your true form, "
        "however, is extremely vulnerable -- any serious attack against it is "
        "likely to kill you.")
    char_name_types = ['pet insect', 'pet crab']
    
#===============================================================================
class Class(base.Class, util.Registry):
    __slots__ = 'base_load', 'base_hp', 'base_damage'
    def apply(self, char):
        char.max_load += self.base_load + char.abilities.modifiers['strength']
        char.max_hp += self.base_hp + char.abilities.scores['constitution']
        char.base_damage += self.base_damage
        char.inventory += self.Inventory_Base()
    def apply_random(self, char):
        char.alignment = self.Alignment.new_random()
        for choice in self.Inventory_Choice.classes:
            char.inventory += choice.new_random()
    def random_human_name(self):
        raise NotImplementedError

class Move_Multiclass(base.Move_Class):
    __slots__ = 'multiclass_move'
    def set_random(self, char):
        wrapped_char = util.Wrapper(char, level=char.level-1)
        self.multiclass_move = random.choice([
            m.new_random(char)
            for c in Class.classes if not isinstance(char.class_, c)
            for m in c.Move.classes if m.eligible(wrapped_char)])
    def summarise_parenthetical(self):
        return self.multiclass_move.summarise_with_class()

#-------------------------------------------------------------------------------
class Agent(Class):
    name = 'Agent'
    base_load = 9
    base_hp = 6
    base_damage = base.Damage(8)
    human_name_types = ['detective', 'code']

    class Inventory_Base(base.Inventory):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Rations(),
            Item_PersonalCommunicator())

    class Inventory_Choice(base.Inventory, util.Registry):
        pass

    class Inventory_Choice1(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice1_Option1(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_SilencedLaserPistol())
    class Inventory_Choice1_Option2(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_AssaultRifle(),
            Item_StunGrenade(quantity=2))

    class Alignment(base.Move_Alignment, util.Registry):
        pass
    class Good(base.Move_Good, Alignment):
        description = 'Risk danger to avoid bloodshed.'
    class Lawful(base.Move_Lawful, Alignment):
        description = 'Take control of a dangerous situation.'
    class Chaotic(base.Move_Chaotic, Alignment):
        description = 'Reveal a secret of someone powerful.'
    class Evil(base.Move_Evil, Alignment):
        description = 'Exploit technology to cause needless violence.'

    class Move(base.Move_Class, util.Registry):
        pass
    for m in ('Hacker', 'Augmented', 'Takedown'):
        type(re.sub(r'\W','',m), (base.Move_Starting, Move), {'name': m})   
    for m in ('CQC', 'Double Down', 'Conspiracy Theorist', 'Blackmail',
        'Conspirator', 'Start Talking', 'Disguise', 'Remote Access',
        'I\'ve Never Seen Code Like This', 'Martial Artist', 'That Was Amazing',
        'Lethal Takedown', 'Augmented Attack'):
        type(re.sub(r'\W','',m), (base.Move_Advanced_2, Move), {'name': m})
    class MulticlassDabbler(base.Move_Advanced_2, Move, Move_Multiclass):
        name = 'Multiclass Dabbler'

Agent.Move.class_ = Agent

#-------------------------------------------------------------------------------
class BountyHunter(Class):
    name = 'Bounty Hunter'
    base_load = 11
    base_hp = 8
    base_damage = base.Damage(10)
    human_names = ['bounty hunter', 'ninja']

    class Inventory_Base(base.Inventory):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_BodyArmour(),
            Item_Rations(uses=5),
            Item_PersonalCommunicator())

    class Inventory_Choice(base.Inventory, util.Registry):
        pass

    class Inventory_Choice1(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice1_Option1(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_LaserRifle())
    class Inventory_Choice1_Option2(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_LaserPistol(),
            Item_CombatKnife())

    class Inventory_Choice2(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice2_Option1(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Rations(uses=5))
    class Inventory_Choice2_Option2(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_StunGrenade(quantity=2))

    class Alignment(base.Move_Alignment, util.Registry):
        pass
    class Good(base.Move_Good, Alignment):
        description = 'Give up reward for the greater good.'
    class Neutral(base.Move_Neutral, Alignment):
        description = 'Defeat worthy prey.'
    class Chaotic(base.Move_Chaotic, Alignment):
        description = 'Take out your target without regard for collateral damage.'
    class Evil(base.Move_Evil, Alignment):
        description = 'Kill a defenceless or surrendered enemy.'

    class Move(base.Move_Class, util.Registry):
        pass
    for m in ('Track Down', 'Locked and Loaded', 'Weapons Expert', 'Armored'):
        type(re.sub(r'\W','',m), (base.Move_Starting, Move), {'name': m})
    for m in ('For Any Occasion', 'Element of Surprise', 'But You Can\'t Hide',
        'Last Reserves', 'Locked On', 'Came Prepared', 'On the Job',
        'Cooling System', 'Old Fashioned', 'Energy Shields', 'Trophy Hunter',
        'Hunter\'s Instincts'):
        type(re.sub(r'\W','',m), (base.Move_Advanced_2, Move), {'name': m})
    class MulticlassDabbler(base.Move_Advanced_2, Move, Move_Multiclass):
        name = 'Multiclass Dabbler'

BountyHunter.Move.class_ = BountyHunter

#-------------------------------------------------------------------------------
class Commando(Class):
    name = 'Commando'
    base_hp = 10
    base_damage = base.Damage(10)
    base_load = 12
    human_names = ['warhammer 40k space marine', 'amazon']

    class Inventory_Base(base.Inventory):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Rations(uses=5),
            Item_BodyArmour(),
            Item_PersonalCommunicator())

    class Inventory_Choice(base.Inventory, util.Registry):
        pass

    class Inventory_Choice1(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice1_Option1(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_AssaultRifle())
    class Inventory_Choice1_Option2(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_LaserRifle(),
            Item_FragGrenade(quantity=2))
    class Inventory_Choice1_Option3(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_RocketLauncher(),
            Item_Rocket(quantity=2),
            Item_StunPistol())

    class Inventory_Choice2(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice2_Option1(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Rations(uses=5),
            Item_Medkit())
    class Inventory_Choice2_Option2(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_Toolbox())

    class Alignment(base.Move_Alignment, util.Registry):
        pass
    class Good(base.Move_Good, Alignment):
        description = 'Protect someone weaker than you.'
    class Lawful(base.Move_Lawful, Alignment):
        description = 'Deny mercy to an enemy of the alliance.'

    class Move(base.Move_Class, util.Registry):
        pass
    for m in ('Armored', 'Superior Soldier', 'War Hero', 'Call in the Cavalry'):
        type(re.sub(r'\W','',m), (base.Move_Starting, Move), {'name': m})
    for m in ('Superior Commander', 'Full Auto', 'Line in the Sand',
        'You\'re All Clear', 'Controlled Explosion', 'For the Alliance',
        'This is My Weapon', 'In the Name of', 'New Objectives'):
        type(re.sub(r'\W','',m), (base.Move_Advanced_2, Move), {'name': m})
    class MulticlassDabbler(base.Move_Advanced_2, Move, Move_Multiclass):
        name = 'Multiclass dabbler'

Commando.Move.class_ = Commando

#-------------------------------------------------------------------------------
class Outcast(Class):
    name = 'Outcast'
    base_hp = 8
    base_damage = base.Damage(6)
    base_load = 6
    human_names = ['apocalypse mutant', 'barbarian', 'dryad']

    class Inventory_Base(base.Inventory):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Rations(uses=5))

    class Inventory_Choice(base.Inventory, util.Registry):
        pass

    class Inventory_Choice1(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice1_Option1(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_TribalArmour())
    class Inventory_Choice1_Option2(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_Clothes(name='Hooded robes'))

    class Inventory_Choice2(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice2_Option1(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Machete(name='Makeshift machete'))
    class Inventory_Choice2_Option2(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_Javelin(quantity=3))

    class Inventory_Choice3(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice3_Option1(Inventory_Choice3):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_HealingHerbs())
    class Inventory_Choice3_Option2(Inventory_Choice3):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_Antitoxin(quantity=3))

    class Alignment(base.Move_Alignment, util.Registry):
        pass
    class Good(base.Move_Good, Alignment):
        description = 'Help someone who is strange to you.'
    class Chaotic(base.Move_Chaotic, Alignment):
        description = 'Free someone of their bonds.'
    class Evil(base.Move_Evil, Alignment):
        description = 'Spread fear in a civilised place.'

    class Move(base.Move_Class, util.Registry):
        pass
    for m in ('Aberration', 'Herbalist', 'Survivor'):
        type(re.sub(r'\W','',m), (base.Move_Starting, Move), {'name': m})
    for m in ('Mutant Warrior', 'Trapper', 'Guide', 'Frenzied', 'A Safe Place',
        'First Aid', 'Healer', 'The Secret Ingredient is Love', 'I\'m a Monster',
        'Simpler Times', 'Strong Arm', 'Blaze Brother', 'Strong Arm',
        'Blaze Brother', 'Adaptable', 'Eagle Eye', 'Terrain Advantage',
        'Trained Instincts'):
        type(re.sub(r'\W','',m), (base.Move_Advanced_2, Move), {'name': m})
    class MulticlassDabbler(base.Move_Advanced_2, Move, Move_Multiclass):
        name = 'Multiclass dabbler'

Outcast.Move.class_ = Outcast

#-------------------------------------------------------------------------------
class Scientist(Class):
    name = 'Scientist'
    base_hp = 4
    base_damage = base.Damage(4)
    base_load = 7

    class Inventory_Base(base.Inventory):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Rations(uses=5),
            Item_PersonalCommunicator(),
            Item(name='Scientific tools and materials', weight=1))

    class Inventory_Choice(base.Inventory, util.Registry):
        pass

    class Inventory_Choice1(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice1_Option1(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Clothes(name='Lab coat'),
            Item_BallisticVest())
    class Inventory_Choice1_Option2(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_Clothes(name='Hazard jumpsuit and gas mask', weight=1))

    class Inventory_Choice2(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice2_Option1(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_LaserRifle())
    class Inventory_Choice2_Option2(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_StunPistol(),
            Item_Medkit())

    class Alignment(base.Move_Alignment, util.Registry):
        pass
    class Good(base.Move_Good, Alignment):
        description = 'Use your expertise to help someone.'
    class Chaotic(base.Move_Chaotic, Alignment):
        description = 'Wreak havok with your experiments.'
    class Neutral(base.Move_Neutral, Alignment):
        description = 'Gain knowledge about your field.'
    class Evil(base.Move_Evil, Alignment):
        description = 'Harm innocents to further your research.'

    class Move(base.Move_Class, util.Registry):
        pass
    for m in ('Research', 'Development', 'Field Experiment',
        'Controlled Environment'):
        type(re.sub(r'\W','',m), (base.Move_Starting, Move), {'name': m})
    for m in ('Surgical Strike', 'Logical', 'Medical Doctor', 'Grease Monkey',
        'Conjecture', 'Ordered Chaos', 'Expanded Horizons', 'Vital Knowledge',
        'Logic Bomb', 'Flashy', 'Next Big Thing'):
        type(re.sub(r'\W','',m), (base.Move_Advanced_2, Move), {'name': m})
    class MulticlassDabbler(base.Move_Advanced_2, Move, Move_Multiclass):
        name = 'Multiclass dabbler'

Scientist.Move.class_ = Scientist

#-------------------------------------------------------------------------------
class Scoundrel(Class):
    name = 'Scoundrel'
    base_hp = 6
    base_damage = base.Damage(6)
    base_load = 9
    human_name_types = ['bandit', 'pirate']

    class Inventory_Base(base.Inventory):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Rations(uses=5),
            Item_PersonalCommunicator())

    class Inventory_Choice(base.Inventory, util.Registry):
        pass

    class Inventory_Choice1(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice1_Option1(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Clothes(name='Casual attire'),
            Item_Medkit())
    class Inventory_Choice1_Option2(Inventory_Choice1):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_BallisticVest())

    class Inventory_Choice2(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice2_Option1(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_LaserPistol(name='Trusty laser pistol'))
    class Inventory_Choice2_Option2(Inventory_Choice2):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_StunPistol(),
            Item_FragGrenade(quantity=2))

    class Inventory_Choice3(Inventory_Choice, util.Random, util.Registry):
        pass
    class Inventory_Choice3_Option1(Inventory_Choice3):
        __init__ = lambda self: base.Inventory.__init__(self,
            Item_Toolbox())
    class Inventory_Choice3_Option2(Inventory_Choice3):
        __init__ = lambda self: base.Inventory.__init__(self, 
            Item_Rations())

    class Alignment(base.Move_Alignment, util.Registry):
        pass
    class Good(base.Move_Good, Alignment):
        description = 'Give up riches to the less fortunate.'
    class Chaotic(base.Move_Chaotic, Alignment):
        description = 'Cheat someone powerful.'
    class Neutral(base.Move_Neutral, Alignment):
        description = 'Avoid conflict with cunning.'
    class Evil(base.Move_Evil, Alignment):
        description = 'Shift danger or blame from yourself to someone else.'

    class Move(base.Move_Class, util.Registry):
        pass
    for m in ('Cheap Shot', 'Charming and Open', 'Reputation'):
        type(re.sub(r'\W','',m), (base.Move_Starting, Move), {'name': m})
    for m in ('Experienced Troublemaker', 'Dirty Fighting', 'Renegade',
        'Holdout', 'I Am Altering the Deal', 'Ace in the Hole', 'Quick Shot',
        'Better Than One', 'I Know', 'Tonight\'s Entertainment'):
        type(re.sub(r'\W','',m), (base.Move_Advanced_2, Move), {'name': m})
    class MulticlassDabbler(base.Move_Advanced_2, Move, Move_Multiclass):
        name = 'Multiclass dabbler'

Scoundrel.Move.class_ = Scoundrel
