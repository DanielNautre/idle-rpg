#!/usr/bin/python3
# -*- coding: utf8 -*

from json import load

# Fix for file paths errors
import os
PATH = os.path.dirname(os.path.realpath(__file__))

with open('{}/data/dungeons.json'.format(PATH)) as file:    
    dungeons = load(file)

with open('{}/data/monsters.json'.format(PATH)) as file:    
    monsters = load(file)

with open('{}/data/champions.json'.format(PATH)) as file:    
    champions = load(file)

with open('{}/data/fields.json'.format(PATH)) as file:    
    fields = load(file)

with open('{}/data/offensive_skills.json'.format(PATH)) as file:    
    oskill_list = load(file)

with open('{}/data/strings.json'.format(PATH)) as file:    
    s = load(file)

with open('{}/data/health_potion.json'.format(PATH)) as file:    
    hpotion_type = load(file)

with open('{}/data/mana_potion.json'.format(PATH)) as file:    
    mpotion_type = load(file)

with open('{}/data/items.json'.format(PATH)) as file:    
    items = load(file)

with open('{}/data/suffix.json'.format(PATH)) as file:    
    suffix = load(file)

with open('{}/data/prefix.json'.format(PATH)) as file:    
    prefix = load(file)


empty_dungeon = {'id':None, 'name':None, 'unique':None, 'monsters':None, 'unique_monster':None, 'rooms':None, 'last_chamber':None}
empty_ennemy = {'lvl':None,'hitpoints':None,'name':None,'loot':None,'type':None,'strength':None,'weakness':None,'unique':None,'death':None,'taunt':None,'effects':None}

pronouns = {'male': {'he':'he', 'him':'him', 'his':'his'}, 'female': {'he':'she','him':'her','his':'her'}}
type_list = {'weapon','armor','jewel'}
weapon_list = {'sword','mace','flail','axe','staff','bow','crossbow'}
armor_list = {'shield','pants','boots','helm','belt','chest','shoulders','bracers','gloves'}
jewel_list = {'ring','amulet'}

verbose_enchants = {'int':'Intelligence', 'str':'Strength', 'dex':'Dexterity', 'vit':'Vitality', 'all':'All Attributes', 'mana':'Mana', 'life':'Life', 'life_regen':'Life regen per tick', 'mana_regen':'Mana regen per tick', 'damage':'Bonus Damage', 'armor':'Bonus Armor', 'gold':'Bonus Gold'}

verbose_subtype = {'sword':'Sword','mace':'Mace','flail':'Flail','axe':'Axe','staff':'Staff','bow':'Bow','crossbow':'Crossbow','shield':'Shield','pants':'Pants','boots':'Boots','helm':'Helmet','belt':'Belt','chest':'Chest','shoulders':'Shoulders','bracers':'Bracers','gloves':'Gloves','ring':'Ring','amulet':'Amulet'}