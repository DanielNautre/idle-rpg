#!/usr/bin/python3
# -*- coding: utf8 -*

from random import choice
from collections import deque


# Import other files from the project
from dice import d6, d20, d100

# Import logger
from logger import log, story

# Import config & data
from data import items, suffix, prefix, type_list, weapon_list, armor_list, jewel_list, verbose_enchants, verbose_subtype


def verboseEnchants(enchant):
    return verbose_enchants[enchant]

class Item(object):
    def __init__(self, type=None, subtype=None, lvl=1, job=None, rare=False):
        super(Item, self).__init__()

        self.baseValue()

        if not rare:
            self.type = type
            self.subtype = subtype
            self.lvl = lvl
            self.rollStats()

            # choose if enchanted item
            dice = d100()
            if lvl >= 3 and lvl < 10:
                if dice > 85:
                    nb = choice([0,1])
                    self.rollEnchant(nb, job)
                pass
            elif lvl >=10:
                if dice > 5:
                    nb = choice([1,2])
                    self.rollEnchant(nb, job)
            self.rollName()

        else:
            self.type = rare['type']
            self.subtype = rare['subtype']
            self.lvl = rare['lvl']
            self.enchanted = rare['enchanted']

            if self.type == 'weapon':
                damage = choice(range(int(self.lvl ** 1.1), int(self.lvl ** 1.3)))
                self.damage_min = damage + rare['damage_min']
                self.damage_max = damage + rare['damage_max']
                if self.subtype in ['bow', 'crossbow']:
                    self.evasion = rare['evasion']
            elif self.type == 'armor':
                self.armor = rare['armor']
                if self.subtype  == 'shield':
                    self.block = rare['block']

            if self.enchanted:
                self.rollEnchant(2, job)

            # set the name, and remove affixes
            self.name = rare['name']
            self.suffix = ''
            self.prefix = ''
            self.desc = rare['desc']

    def baseValue(self):
        # items have names
        self.name = ''
        self.suffix = ''
        self.prefix = ''
        self.desc = ''

        # weapons have damage values
        self.damage_min = 0
        self.damage_max = 0
        # bow has a evasion value, to simulate ranged combat
        self.evasion = 0
        # armor have armor value
        self.armor = 0
        # shields have block value
        self.block = 0

        # enchanted items have special attributes
        self.enchanted = False
        self.enchant = {}
        
    def rollStats(self):
        # roll dices to determine the stats based on the lvl of the item
        
        if self.type == 'weapon':

            self.damage_min = choice(range(self.lvl, int(self.lvl ** 1.2) + 1))

            # archer don't block, they "evade" since there not meleeing. woking but should be fine
            if self.subtype in ['bow', 'crossbow']:                
                self.evasion = max(int((8 * d6() * self.lvl) / (3 * self.lvl + 7) - 5), 1)

            self.damage_min = int(self.damage_min)
            self.damage_max = int(self.damage_min + max(int(self.lvl/4), 2))

        elif self.type == 'armor':
            self.armor = self.lvl / 5
            if self.subtype  == 'shield':
                # for non archer, would provide between 35-85 block for given level
                self.block = max(int(((14 + d20()) * self.lvl)), 1)# - 5), 1)

    def rollEnchant(self, nb, job):
        log.debug("Item ::  max enchants: {}".format(nb))
        self.enchanted = True
        possible_enchants = deque(['mana', 'life', 'life_regen', 'mana_regen', 'damage', 'armor', 'gold'])

        # roll dice to determine enchants (1% for all, 20% for vit, the rest for main attribut)
        dice = d100()

        if dice > 99:
            value = self.addEnchant('all')
            self.setAffix('all', value)
        elif dice <= 20:
            value = self.addEnchant('vit')
            self.setAffix('vit', value)
        elif job == 'Wizard':
            value = self.addEnchant('int')
            self.setAffix('int', value)
        elif job == 'Paladin':
            value = self.addEnchant('str')
            self.setAffix('str', value)
        elif job == 'Archer':
            value = self.addEnchant('dex')
            self.setAffix('dex', value)

        # some item can't have specific enchants
        if self.type == 'weapon':
            possible_enchants.remove('armor')
            possible_enchants.remove('gold')
        elif self.type == 'armor':
            possible_enchants.remove('damage')
            possible_enchants.remove('gold')
        elif self.type == 'jewelry':
            possible_enchants.remove('armor')
            possible_enchants.remove('damage')

        log.debug("Item :: Possible enchants: {}".format(possible_enchants))

        for _ in range(nb):
            type = choice(list(possible_enchants))
            value = self.addEnchant(type)
            possible_enchants.remove(type)
            self.setAffix(type, value)

    def setAffix(self, type, value):
        if type == "damage" and self.subtype == "staff":
            type = "mag_damage"

        if type in list(suffix):
            for key in list(suffix[type]):
                min = suffix[type][key][0]
                max = suffix[type][key][1]
                if value in range(min, max):
                    self.suffix = key
                    log.debug("Item :: set suffix :: {0}".format(key))
                    break
        else:
            for key in list(prefix[type]):
                min = prefix[type][key][0]
                max = prefix[type][key][1]
                if value in range(min, max):
                    self.prefix = key
                    log.debug("Item :: set preffix :: {0}".format(key))
                    break

    def addEnchant(self, type):
        value = False
        if type == 'int':
            value = int(self.lvl * (d6()/6) / 4)
            self.enchant[type] = round(max(value, 1), 1)
        elif type == 'dex':
            value = int(self.lvl * (d6()/6) / 4)
            self.enchant[type] = round(max(value, 1), 1)
        elif type == 'str':
            value = int(self.lvl * (d6()/6) / 4)
            self.enchant[type] = round(max(value, 1), 1)
        elif type == 'vit':
            value = int(self.lvl * (d6()/6) / 4)
            self.enchant[type] = round(max(value, 1), 1)           
        elif type == 'all':
            value = int(self.lvl * (d6()/6) / 4)
            self.enchant[type] = round(max(value, 1), 1)
        elif type == 'mana':
            value = int(self.lvl * (d6()/6))
            self.enchant[type] = round(max(value, 1), 1)
        elif type == 'life':
            value = int(self.lvl * (d6()/6))
            self.enchant[type] = round(max(value, 1), 1)
        elif type == 'mana_regen':
            value = int(self.lvl * (d6()/6) / 10)
            self.enchant[type] = round(max(value, 0.1), 1)
        elif type == 'life_regen':
            value = int(self.lvl * (d6()/6) / 10)
            self.enchant[type] = round(max(value, 0.1), 1)
        elif type == 'damage':
            value = int(self.lvl * (d6()/6))
            self.enchant[type] = round(max(value, 1), 1)
        elif type == 'armor':
            value = int(self.lvl * (d6()/6) / 10)
            self.enchant[type] = round(max(value, 0.1), 1)
        elif type == 'gold':
            value = int(self.lvl * (d6()/6))
            self.enchant[type] = round(max(value, 1), 1)
        return self.enchant[type]

    def value(self):
        modifier = 4 if self.enchanted else 2
        return int(self.lvl * (modifier + d6() / 2))

    def compare(self, item, att=None):
        # return true if item is better
        pips = 0

        if self.enchanted and not item.enchanted:
            # if the new item is not enchanted, don't bother trying to equip it
            log.info("Item :: New item is not enchanted, old one is")
            return False

        if not self.enchanted and item.enchanted:
            # on the contrary, equip any item that is enchanted on a slot that has not an enchanted item
            log.info("Item :: New item is enchanted, old one is not")
            return True

        #compare raw damage
        if self.type == 'weapon':
            average = (self.damage_min + self.damage_max) / 2
            item_average = (item.damage_min + item.damage_max) / 2
            val = ((item_average - average) * 4) / 10
            log.debug("Item :: Compare Damage :: New: {0} Old: {1}".format(item_average, average))
            log.debug("Item :: Compare Damage :: {} pips for damage".format(val))
            pips += val

        # compare raw armor
        elif self.type == 'armor':
            val = ((item.armor - self.armor) * 4) / 10
            log.debug("Item :: Compare Armor :: New: {0} Old: {1}".format(item.armor, self.armor))
            log.debug("Item :: Compare Armor:: {} pips ".format(val))
            pips += val 


        if item.enchanted:

            for key in ['int', 'str', 'dex', 'vit', 'all']:
                if key in item.enchant: 
                    value = item.enchant[key]

            for key2 in ['int', 'str', 'dex', 'vit', 'all']: 
                if key2 in self.enchant: 
                    value2 = item.enchant[key]

            val = ((value - value2) * 7) / 10
            log.debug("Item :: Compare Enchants :: New : {0} {1} Old: {2} {3}".format(key, value, key2, value2))
            log.debug("Item :: Compare Enchants:: {} pips ".format(val))
            pips += val

            val = ((item.lvl - self.lvl) * 3) / 10
            log.debug("Item :: Compare Lvl :: New: {0} Old: {1}".format(item.lvl, self.lvl))
            log.debug("Item :: Compare Lvl:: {} pips ".format(val))
            pips += val

            if len(item.enchant) > len(self.enchant):
                val = (len(item.enchant) - len(self.enchant) * 2) / 10
                log.debug("Item :: Compare Nb of Enchants :: New: {0} Old: {1}".format(len(item.enchant), len(self.enchant)))
                log.debug("Item :: Compare Nb of Enchants:: {} pips ".format(val))
                pips += val


        log.debug("Item :: Comparaison value :: {}".format(pips))

        if pips > 0:
            return True

        return False

    def fullname(self):
        return "{prefix}{name}{suffix}".format(prefix=self.prefix, name=self.name, suffix=self.suffix)

    def rollName(self):
        for key in list(items[self.type][self.subtype]):
            min = items[self.type][self.subtype][key][0]
            max = items[self.type][self.subtype][key][1]
            if self.lvl in range(min, max):
                self.name = key
                break

    def verboseSubtype(self):
        return verbose_subtype[self.subtype]

    def __str__(self):
        string = "\nType: {}".format(self.verboseSubtype())
        string += "\nName: {}".format(self.fullname())
        if self.type == "weapon":
            string += "\nDamage: {0} - {1}".format(self.damage_min, self.damage_max)
        elif self.type == "armor":
            string += "\nArmor: {0}".format(self.armor)
        if self.subtype in ['crossbow', 'bow']:
            string += "\nEvasion: {}".format(self.evasion)
        elif self.subtype is 'shield':
            string += "\nBlock: {}".format(self.block)
        string += "\nLevel: {}".format(self.lvl, self.enchanted)
        string += "\nEnchantments: {}".format(self.enchant)
        return string

if __name__ == '__main__':
    
    item = Item('weapon', 'sword', 10, 'Paladin')

    print(item.fullname())