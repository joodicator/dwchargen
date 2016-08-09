from itertools import *
from UserList import UserList

import utility as util

#===============================================================================
class Char(util.Random):
#    __slots__ = (
#        'name', 'class_', 'alignment_move', 'race', 'gender', 'abilities',
#        'max_hp', 'max_load', 'base_damage', 'level', 'inventory', 'armour')

    def __init__(self):
        self.max_hp = 0
        self.max_load = 0
        self.base_damage = Damage()
        self.level = 1
        self.inventory = Inventory()

    def show_lines(self):
        return [
            'Name: %s, Class: %s' % (self.name, self.class_.name),
            'Race: %s' % self.race.summarise(self),
            'Alignment:  %s' % self.alignment.summarise(),
            'Abilities:  %s' % self.abilities.summarise(),
            'Statistics: %d HP, %s Damage, %d Armour, %d/%d Load' % (
                self.max_hp,
                self.base_damage.summarise(),
                self.armour,
                self.inventory.load_used, self.max_load),
            'Inventory:  %s' % self.inventory.summarise()]

    def print_lines(self):
        for line in self.show_lines():
            print line

    @property
    def armour(self):
        return sum(item.tags.get('armour', 0) for item in self.inventory)

class Damage(object):
#    __slots__ = 'sides', 'add'
    def __init__(self, sides=0, add=0):
        self.sides = sides
        self.add = add
    def __add__(self, other):
        if not isinstance(other, Damage): raise NotImplemented
        return Damage(self.sides+other.sides, self.add+other.add)
    def __sub__(self, other):
        if not instanceof(other, Damage): raise NotImplemented
        return Damage(self.sides-other.sides, self.add-other.add)
    def summarise(self):
        return 'd%d%s' % (
            self.sides,
            '%+d' % self.add != 0 if self.add else '')

class Item(object):
#    __slots__ = 'name', 'quantity', 'tags'
    name = None
    def __init__(self, *atags, **ktags):
        if 'name' in ktags:
            self.name = ktags.pop('name')
        if 'quantity' in ktags:
            self.quantity = ktags.pop('quantity')
        elif not hasattr(self, 'quantity'):
            self.quantity = 1
        self.tags = getattr(self, 'tags', dict())
        self.tags.update((tag, True) for tag in atags)
        self.tags.update(ktags)

    def summarise(self):
        return '%s%s%s' % (
            '%d * ' % self.quantity if self.quantity != 1 else '',
            '%d/%d ' % self.tags['uses'] if 'uses' in self.tags else '',
            self.name)

    def merge(self, other):
        if (isinstance(other, Item)
        and other.name == self.name and other.tags == self.tags):
            quantity = self.quantity + other.quantity
            return Item(name=self.name, quantity=quantity, **self.tags)
        else:
            return None

    def __mul__(self, other):
        if isinstance(other, numbers.Integral):
            return self(name=self.name, quantity=self.quantity*other, **self.tags)
        else:
            return NotImplemented

    def __repr__(self):
        return '%s%s(%s)' % (
            '' if self.quantity == 1 else '%d * ' % self.quantity,
            self.__class__.__name__,
            ', '.join('%s=%r' % i for i in chain(
                [('name', self.name)] if self.name else [],
                self.tags.iteritems())))

class Inventory(UserList):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            self.data = args[0]
        else:
            self.data = list(args)
        self.compact()

    @property
    def load_used(self):
        return sum(item.tags.get('weight')*item.quantity for item in self)

    def summarise(self):
        return ', '.join(item.summarise() for item in self)

    def __setitem__(self, i, value):
        result = super(Inventory, self).__setitem__(i, value)
        self.compact(i, i+1)
        return result

    def __setslice__(self, i, j, values):
        result = super(Inventory, self).__setslice__(i, j, values)
        self.compact(i, i + len(values))
        return result

    def __iadd__(self, other):
        result = super(Inventory, self).__iadd__(other)
        self.compact(-len(other))
        return result

    def __imul__(self, n):
        for i in range(len(self)):
            self[i] *= n
        return result

    def append(self, value):
        result = super(Inventory, self).append(value)
        self.compact(-1)
        return result

    def extend(self, values):
        result = super(Inventory, self).extend(values)
        self.compact(-len(values))
        return result

    def insert(self, i, value):
        result = super(Inventory, self).insert(i, value)
        self.compact(i, i+1)
        return result

    def compact(self, start=None, end=None):
        length = len(self)
        start = 0 if start is None else length+start if start<0 else start
        end = length if end is None else length+end if end<0 else end

        for i in reversed(range(start, end)):
            for j in chain(range(i), range(i+1, length)):
                merged = self[i].merge(self[j])
                if merged is not None:
                    super(Inventory, self).__setitem__(min(i,j), merged)
                    del self[max(i,j)]
                    length -= 1
                    break

    def __repr__(self):
        return 'Inventory(%s)' % ', '.join(repr(i) for i in self)

class Abilities(object):
#    __slots__ = 'scores', 'modifiers'
    ability_names = (
        'strength', 'dexterity', 'constitution',
        'intelligence', 'wisdom', 'charisma')
    def __init__(self):
        self.scores    = {a:None for a in self.ability_names}
        self.modifiers = {a:None for a in self.ability_names}
    def set_ability_score(self, ability, score):
        self.scores[ability] = score
        self.modifiers[ability] = self.score_modifier(score)
    def summarise(self):
        return ', '.join(
            '%s %d (%+d)' % (
                ability[:3].upper(),
                self.scores[ability],
                self.modifiers[ability])
            for ability in sorted(
                self.ability_names, reverse=True, key=self.scores.get))
    @classmethod
    def score_modifier(cls, score):
        return -3 if score < 4 \
          else -2 if score < 6 \
          else -1 if score < 9 \
          else +0 if score < 13 \
          else +1 if score < 16 \
          else +2 if score < 18 \
          else +3

class Char_Attr(util.Random):
    def apply(self, char):
        pass

class Class(Char_Attr):
#    __slots__ = 'name',
    pass

class Race(Char_Attr):
#    __slots__ = 'name', 'racial_move'
    def summarise(self, char):
        if self.name == self.racial_move.name:
            suffix = self.racial_move.summarise_parenthetical()
        else:
            suffix = self.racial_move.summarise()
        return '%s%s%s' % (
            self.name,
            ' (%s)' % char.gender if char.gender is not None else '',
            ' -- %s' % suffix if suffix is not None else '')

class Move(util.Random):
#    __slots__ = 'name', 'description'
    def __init__(self, name=None, description=None):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
    def summarise(self):
        summary = self.name
        if hasattr(self, 'summarise_parenthetical'):
            summary = '%s (%s)' % (summary, self.summarise_parenthetical())
        return summary

class Move_Class(Move):
#    __slots__ = 'class_'
    @classmethod
    def eligible(self, char):
        return True
    def summarise_with_class(self):
        summary = '%s\'s "%s"' % (self.class_.name, self.name)
        if hasattr(self, 'summarise_parenthetical'):
            summary = '%s (%s)' % (summary, self.summarise_parenthetical())
        return summary
class Move_Starting(Move_Class):
    pass
class Move_Advanced(Move_Class):
    pass
class Move_Advanced_2(Move_Advanced):
    @classmethod
    def eligible(self, char):
        return char.level >= 2 \
           and super(Move_Advanced_2, self).eligible(char)
class Move_Advanced_6(Move_Advanced):
    @classmethod
    def eligible(self, char):
        return char.level >= 6 \
           and super(Move_Advanced_6, self).eligible(char)

class Move_Alignment(Move):
    def summarise(self):
        return '%s -- %s' % (self.name, self.description)
class Move_Good(Move_Alignment):
    name = 'Good'
class Move_Lawful(Move_Alignment):
    name = 'Lawful'
class Move_Neutral(Move_Alignment):
    name = 'Neutral'
class Move_Chaotic(Move_Alignment):
    name = 'Chaotic'
class Move_Evil(Move_Alignment):
    name = 'Evil'
