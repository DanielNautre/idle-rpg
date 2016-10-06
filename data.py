#!/usr/bin/python3
# -*- coding: utf8 -*

from json import load

# Fix for file paths errors
import os
PATH = os.path.dirname(os.path.realpath(__file__))

with open('{}/data/dungeons.json'.format(PATH)) as file:    
    dungeons = json.load(file)

with open('{}/data/monsters.json'.format(PATH)) as file:    
    monsters = json.load(file)

with open('{}/data/champions.json'.format(PATH)) as file:    
    champions = json.load(file)

with open('{}/data/fields.json'.format(PATH)) as file:    
    fields = json.load(file)

with open('{}/data/offensive_skills.json'.format(PATH)) as file:    
    oskill_list = json.load(file)

with open('{}/data/strings.json'.format(PATH)) as file:    
    s = json.load(file)

with open('{}/data/health_potion.json'.format(PATH)) as file:    
    hpotion_type = json.load(file)

with open('{}/data/mana_potion.json'.format(PATH)) as file:    
    mpotion_type = json.load(file)

with open('{}/data/items.json'.format(PATH)) as file:    
    items = json.load(file)

with open('{}/data/suffix.json'.format(PATH)) as file:    
    suffix = json.load(file)

with open('{}/data/prefix.json'.format(PATH)) as file:    
    prefix = json.load(file)


empty_dungeon = {}
empty_ennemy = {}

pronouns = {}
type_list = {'weapon','armor','jewel'}
weapon_list = {'sword','mace','flail'}
armor_list = {}
jewel_list = {'ring','amulet'}
verbose_enchants = {}
verbose_subtype = {}