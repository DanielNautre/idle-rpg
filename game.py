#!/usr/bin/python3
# -*- coding: utf8 -*

from random import choice, randint, random
from collections import defaultdict

import operator

# Import other files from the project
from dice import d6, d20, d100
from hero import Hero
from item import Item

# Import logger
from logger import log, story

from widgets import HeroSelection, Adventure, HeroStats, EnnemyStats, NoEnnemyStats

# Import config & data
from data import dungeons, monsters, champions, fields, oskill_list, s, hpotion_type, mpotion_type, empty_dungeon, empty_ennemy


def selectRandomSkill(job, attribut):
    list_skill = []
    for skill in list(oskill_list):
        if job in oskill_list[skill]['job'] and oskill_list[skill]['base_att'] <= attribut:
            list_skill.append(skill)

    if len(list_skill) == 0:
        return False

    return choice(list_skill)


class Game(object):
    def __init__(self):
        super(Game, self).__init__()
        self.started = False
        self.game_reloaded = False

        # The game starts you at home
        self.location = 'home'

        # Initiate the current dungeon and ennemy with their empty versions
        self.dungeon = dict(empty_dungeon)
        self.ennemy = dict(empty_ennemy)
        self.hero = None

        self.wait = 0

        # general stats
        self.kills = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.hpotion_taken = 0
        self.mpotion_taken = 0
        self.spell_cast = 0
        self.dungeon_cleared = 0
        self.unique_kills = 0
        self.xp_earned = 0
        self.gold_earned = 0
        self.chest_opened = 0
        self.item_found = 0
        self.town_trips = 0
        self.killed_champ = []
        self.finished_dungeon = []
        self.skill_usage = {}

    def save(self):
        data = {}
        data['kills'] = self.kills
        data['damage_dealt'] = self.damage_dealt
        data['damage_taken'] = self.damage_taken
        data['hpotion_taken'] = self.hpotion_taken
        data['mpotion_taken'] = self.mpotion_taken
        data['spell_cast'] = self.spell_cast
        data['dungeon_cleared'] = self.dungeon_cleared
        data['unique_kills'] = self.unique_kills
        data['xp_earned'] = self.xp_earned
        data['gold_earned'] = self.gold_earned
        data['chest_opened'] = self.chest_opened
        data['item_found'] = self.item_found
        data['killed_champ'] = self.killed_champ
        data['finished_dungeon'] = self.finished_dungeon
        data['skill_usage'] = self.skill_usage

        # Game values
        data['location'] = self.location
        data['dungeon'] = self.dungeon
        data['ennemy'] = self.ennemy

        return data

    def load(self, data):
        self.kills = data['kills']
        self.damage_dealt = data['damage_dealt']
        self.damage_taken = data['damage_taken']
        self.hpotion_taken = data['hpotion_taken']
        self.mpotion_taken = data['mpotion_taken']
        self.spell_cast = data['spell_cast']
        self.dungeon_cleared = data['dungeon_cleared']
        self.unique_kills = data['unique_kills']
        self.xp_earned = data['xp_earned']
        self.gold_earned = data['gold_earned']
        self.chest_opened = data['chest_opened']
        self.item_found = data['item_found']
        self.killed_champ = data['killed_champ']
        self.finished_dungeon = data['finished_dungeon']
        self.skill_usage = data['skill_usage']

        # Game values
        self.location = data['location']
        self.dungeon = data['dungeon']
        self.ennemy = data['ennemy']

        self.game_reloaded = True

    def generateEnnemy(self, lvl, unique=False, boss=False, monster_list=False):
        # Reset ennemy and common var used
        self.ennemy = dict(empty_ennemy)

        # reset values
        hitpoints = 0
        message = ''

        # adjust lvl to avoid negatives
        lvl = max(lvl, 1)

        # modifier to increase values for unique or rare mobs
        modifier = 1

        # create list of matching monsters
        matches = []
        
        monster_pool = dict(monsters)

        if unique:
            monster_pool = dict(champions)
            monster_list = list(champions)
            log.info("Monster :: Generate Unique Monster")
        elif not monster_list:
            monster_list = list(monsters)
            log.info("Monster :: Generate Normal Monster")

        if boss:
            log.info("Monster :: Generate Boss")
            log.debug("Monster :: Boss info ::\n {}".format(boss))
            lvl = self.hero.lvl # boss['lvl']
            strength = boss['strength'] * (lvl ** 1.12)
            modifier += 2 * strength
            hitpoints = int(((lvl ** 1.35) * 5.5) + 15 + (random() * lvl))
            death_message = boss['death']
            name = boss['name']
            type = boss['type']
            id = boss['id']
            weakness = boss['weakness']
            resistance = boss['resistance']
            loot = boss['loot']
            taunt = boss['taunt'][self.hero.job]
            message = s['spawn_boss']

        else:
            for key in monster_list:
                if lvl >= monster_pool[key]['lvl'][0] and lvl <= monster_pool[key]['lvl'][1]:
                    if key in self.killed_champ:
                        continue
                    matches.append(key)

            if len(matches) > 0:                   
                id = choice(matches)
            else:
                return False

            log.debug("Monster :: List of matches :: {}".format(matches))
            log.info("Monster :: Chosen :: {}".format(id))

            if unique:
                message = s['spawn_champ']
                strength = champions[id]['strength'] * (lvl ** 1.12)
                hitpoints = int(((lvl ** 1.35) * 4) + 5 + (random() * lvl))
                name = champions[id]['name']
                type = champions[id]['type']
                weakness = champions[id]['weakness']
                resistance = champions[id]['resistance']
                # only if boss
                loot = champions[id]['loot']
                death_message = champions[id]['death']
                taunt = champions[id]['taunt'][self.hero.job]
                modifier += 2 * strength
                del(champions[id])
            else:        
                message = s['spawn']
                strength = monsters[id]['strength'] * (lvl ** 1.12)
                hitpoints = int(((lvl ** 1.35) * 2.5) + 2 + (random() * lvl))
                name = monsters[id]['name']
                type = monsters[id]['type']
                weakness = monsters[id]['weakness']
                resistance = monsters[id]['resistance']
                # only if boss
                loot = False
                death_message = None
                taunt = False

        self.ennemy['id'] = id
        self.ennemy['lvl'] = lvl
        self.ennemy['hitpoints'] = hitpoints
        self.ennemy['name'] = name
        self.ennemy['loot'] = loot
        self.ennemy['type'] = type
        self.ennemy['strength'] = strength
        self.ennemy['weakness'] = weakness
        self.ennemy['resistance'] = resistance
        self.ennemy['unique'] = modifier
        self.ennemy['death'] = death_message
        self.ennemy['taunt'] = taunt
        self.ennemy['effects'] = defaultdict(list)

        log.debug("Combat :: ennemy stats ::\n{}".format(self.ennemy))

        return message

    def generateDungeon(self, lvl):
        # Reset dungeon
        self.dungeon = dict(empty_dungeon)

        # create a list with dungeon who match the hero's lvl
        matches = []

        for key in list(dungeons):
            if lvl in dungeons[key]['lvl']:
                if key in self.finished_dungeon:
                    continue
                matches.append(key)

        if len(matches) < 1:
            return False

        log.debug("Dungeon Generation :: list of possible dungeons :: {}".format(matches))
        
        #select a random dungeon from the list of matching ones
        self.dungeon['id'] = choice(matches)
        self.dungeon['name'] = choice(dungeons[self.dungeon['id']]['name'])
        self.dungeon['monsters'] = dungeons[self.dungeon['id']]['monsters']
        self.dungeon['unique'] = dungeons[self.dungeon['id']]['unique']
        self.dungeon['unique_monster'] = dungeons[self.dungeon['id']]['unique_monster']
        min = dungeons[self.dungeon['id']]['rooms'][0]
        max = dungeons[self.dungeon['id']]['rooms'][1]
        self.dungeon['rooms'] = randint(min, max)

        if self.dungeon['unique']:
            # remove dungeon from the dict if it's unique (won't be generated anymore)
            self.dungeon['last_chamber'] = dungeons[self.dungeon['id']]['last_chamber']
            del(dungeons[self.dungeon['id']])

        return True

    def verboseLocation(self, lvl):
        if self.location == 'home':
            return "Home"
        elif self.location == 'town':
            return "Town"
        elif self.location == 'fields':
            for key, value in iter(fields.items()):
                if lvl in range(value[0], value[1]):
                    return key
            return "Void"
        elif self.location == 'dungeon':
            if self.dungeon['rooms'] == 0 and self.dungeon['last_chamber']:
                return "{0}: {1}".format(self.dungeon['name'], self.dungeon['last_chamber'])
            else:
                return self.dungeon['name']

    def handleLootDrop(self, channel, loot=False):
        #if loot is predetermined, drop it
        
        item = False
        message = s['no_loot']

        dice = d100()
        log.info("LootDrop :: Item dice :: {}".format(dice))

        if loot:
            # check for incompatible suptype before dropping loot
            if self.hero.job == 'Wizard' and loot['type'] == 'weapon' and not loot['subtype'] in ['sword', 'staff']:
                pass
            elif not self.hero.job == 'Paladin' and loot['subtype'] == 'shield':
                pass
            else:
                item = Item(job=self.hero.job, rare=loot)

        elif dice == 1:
            if self.hero.lvl < 25:
                message = s['bizzare_potion'].format(hero=self.hero.name)
            else:
                dice = d20()
                log.debug("LootDrop :: Attribut potion dice :: {}".format(dice))
                if dice == 1:
                    attribut_potion = choice(['Skill','Knowledge','Vigor','Might'])
                    potion_equivalence = {'Skill':'Dexterity','Knowledge':'Intelligence','Vigor':'Vitality','Might':'Strength'}
                    message = s['att_potion'].format(hero=self.hero.name, value=1, type= attribut_potion, attribut=potion_equivalence[attribut_potion])
                    if attribut_potion == 'Skill':
                        self.hero.base_dexterity += 1
                    elif attribut_potion == 'Knowledge':
                        self.hero.base_intelligence += 1
                    elif attribut_potion == 'Vigor':
                        self.hero.base_vitality += 1
                    elif attribut_potion == 'Might':
                        self.hero.base_strength += 1
                else:
                    message = s['bizzare_potion'].format(hero=self.hero.name)
        elif dice in range(2,5):
            # drop a skill tome                    
            skill = selectRandomSkill(self.hero.job, self.hero.baseAtt())
            log.info("LootDrop :: Found Skill Book :: {}".format(skill))
            if skill:
                success = self.hero.addSkill(skill)
                skillname = oskill_list[skill]['name']
            else:
                success = False

            if success == 'improved':
                message = s['improved_spell']
                message =  message.format(hero=self.hero.name, spell=skillname, his=self.hero.pronoun('his'))
                channel.updateSkills()

            elif success == 'added':
                message = s['new_spell']
                message =  message.format(hero=self.hero.name, spell=skillname)
                channel.updateSkills()

            else:
                message = s['gibberish']
                message =  message.format(hero=self.hero.name)
        elif dice in range(5,45):
            # drop weapon
            if self.hero.job == 'Paladin':
                subtype = choice(['sword', 'mace', 'axe', 'flail'])
                item = Item('weapon', subtype, self.hero.lvl, self.hero.job)
                #result = self.hero.equip(item)
            elif self.hero.job == 'Archer':
                subtype = choice(['bow', 'crossbow'])
                item = Item('weapon', subtype, self.hero.lvl, self.hero.job)
            elif self.hero.job == 'Wizard':
                subtype = choice(['sword', 'staff'])
                item = Item('weapon', subtype, self.hero.lvl, self.hero.job)
            log.info("LootDrop :: Found Weapon :: {}".format(item))
        elif dice in range(45,80):
            # drop armor
            subtype = choice(['chest', 'pants', 'gloves', 'boots', 'helm', 'shoulders', 'bracers', 'belt'])
            item = Item('armor', subtype, self.hero.lvl, self.hero.job)
            log.info("LootDrop :: Found Armor :: {}".format(item))
        elif dice in range(80,85):
            # drop shield for the Paladin
            if self.hero.job == 'Paladin':
                subtype = 'shield' 
                item = Item('armor', subtype, self.hero.lvl, self.hero.job)
                log.info("LootDrop :: Found Shield :: {}".format(item))
        elif dice in range(85,99):
            # drop armor
            subtype = choice(['amulet', 'ring'])
            item = Item('jewel', subtype, self.hero.lvl, self.hero.job)
            log.info("LootDrop :: Found Jewel :: {}".format(item))
        elif dice in range(99,101):
            # drop a potion
            if choice(['health','mana']) == 'health':
                #check space
                potion_type = self.hero.hpotion_type()
                if self.hero.belt_size - len(self.hero.hpotion_belt) > 0:
                    message = s['found_potion']
                    message = message.format(hero=self.hero.name, potion=potion_type)
                    self.hero.addHpotion(1, potion_type)
                else:
                    message = s['found_potion_no_space']
                    message = message.format(hero=self.hero.name, potion=potion_type)
            else:
                potion_type = self.hero.mpotion_type()
                #check space
                if self.hero.belt_size - len(self.hero.mpotion_belt) > 0:
                    message = s['found_potion']
                    message = message.format(hero=self.hero.name, potion=potion_type)
                    self.hero.addMpotion(1, potion_type)
                else:
                    message = s['found_potion_no_space']
                    message = message.format(hero=self.hero.name, potion=potion_type)

            log.info("LootDrop :: Found Potion :: {}".format(potion_type))
        
        if item: 
            # update stats
            self.item_found += 1

            if self.hero.equip(item) == True:
                message = s['new_item']
                message = message.format(hero=self.hero.name, item=item.fullname())
                channel.updateSkills()
            elif self.hero.equip(item) == False:
                message = s['crap_item']
                message = message.format(hero=self.hero.name, item=item.fullname())
            else:
                message = s['inventory_full']
                message.format(hero=self.hero.name)

        channel.addStory(message)

    def handleCombat(self, channel, docks):
        self.wait += 1

        # If the game was just reloaded, we may want to update some things
        if self.game_reloaded:
            self.game_reloaded = False
            # Update the dock
            docks['ennemy'].setWidget(EnnemyStats(self.ennemy))

        # Hero's turn
        if self.wait == 0:
            # Hero's turn
            skill_to_use = self.hero.bestSkill(self.ennemy['hitpoints'], self.ennemy['weakness'], self.ennemy['resistance'])
            damage = round(self.hero.useSkill(skill_to_use, self.ennemy['weakness'], self.ennemy['resistance']), 1)
            log.info("Combat :: Hero hits :: {0}: {1}".format(skill_to_use, damage))
            
            # update stats
            if skill_to_use in self.skill_usage:
                self.skill_usage[skill_to_use] += 1
            else:
                self.skill_usage[skill_to_use] = 1

            if skill_to_use == 'weapon':
                kill_string = choice(s['kill'])
                hit_string = choice(s['hit'])
            else:
                kill_string = oskill_list[skill_to_use]['kill_string']
                hit_string = oskill_list[skill_to_use]['hit_string']

                # update stats
                self.spell_cast += 1

            if damage > 0:
                self.ennemy['hitpoints'] -= damage

                # increment stats
                self.damage_dealt += damage

            # Creature is killed
            if self.ennemy['hitpoints'] <= 0:
                message = kill_string.format(creature=self.ennemy['name'], hero=self.hero.name, his=self.hero.pronoun('his'))
                channel.addStory(message)

                # increment stat
                self.kills += 1

                self.kill(channel, docks)

            else:
                message = hit_string.format(hero=self.hero.name, creature=self.ennemy['name'], damage=damage)
                channel.addStory(message)

                # If the creature survives, check if the skill created any effect
                effect_type = None
                if skill_to_use != 'weapon':
                    effect_type = oskill_list[skill_to_use]['type']
                    duration = oskill_list[skill_to_use]['duration']
                    chance = oskill_list[skill_to_use]['chance']
                elif self.hero.gear['weapon']:
                    if 'debuff' in self.hero.gear['weapon'].enchant:
                        effect_type = self.hero.gear['weapon'].enchant['debuff']
                        duration = 10000 if effect_type == 'Electric' else 1
                        chance = 10 

                if effect_type:
                    if effect_type == "Fire" and "Fire" not in self.ennemy['resistance']:
                        if d100() <= chance:
                            self.ennemy['effects']['Burning'] = duration
                            log.debug("Combat :: Burning effect was applied")
                    if effect_type == "Poison" and "Poison" not in self.ennemy['resistance']:
                        if d100() <= chance:
                            self.ennemy['effects']['Poison'] = duration
                            log.debug("Combat :: Poison effect was applied")
                    if effect_type == "Electric" and "Electric" not in self.ennemy['resistance']:
                        if d100() <= chance:
                            self.ennemy['effects']['Weakness'] = duration
                            log.debug("Combat :: Weakness effect was applied")
                            lost = round(self.ennemy['strength'] * 0.1, 1)
                            self.ennemy['strength'] -= lost
                            message = s['weakened'].format(creature=self.ennemy['name'], lost=lost)
                            channel.addStory(message)
                    if effect_type == "Ice" and "Ice" not in self.ennemy['resistance']:
                        if d100() <= chance:
                            self.ennemy['effects']['Stun'] = duration
                            log.debug("Combat :: Stun effect was applied")

                if self.ennemy['taunt']:
                    dice = d20()
                    if dice >= 19:
                        taunt = choice(self.ennemy['taunt'])
                        taunt = taunt.format(name=self.hero.name)
                        message = "<b>{0}</b> <i>{1}</i>".format(self.ennemy['name'], taunt)
                        channel.addStory(message) 
        # Creature's turn
        elif self.wait == 1:
            # Creature's turn

            nmy_damage = 0
            log.debug("Combat :: List of debuffs on the creature ::\n{}".format(self.ennemy['effects']))

            # the creature tries an attack and the hero tries to block it
            dice = d100()
            log.debug("Combat :: Block dice :: {}".format(dice))

            # If the Creature is stunned skip its turn
            if 'Stun' in self.ennemy['effects']:
                log.info("Combat :: Ennemy is Stunned and can't attack this turn")
                message = s['stunned'].format(hero=self.hero.name, creature=self.ennemy['name'])
                channel.addStory(message) 
            elif dice > self.hero.block_chance:
                dice = d20()
                log.debug("Combat :: Crit dice :: {}".format(dice))
                critic_msg = ''
                if dice < 5:
                    critic = 1
                    critic_msg = ' weakly'
                elif dice >= 5 and dice < 18:
                    critic = 2
                else:
                    critic = 3
                    critic_msg = ' critically'

                # calculate raw damage
                raw_damage = round(self.ennemy['strength'] * critic, 1)
                # caculate damage, based on armor and effectiveness
                # ensure armor absorbs maximum of 90% of raw damage. And player takes at least 0.1 damage 
                min_damage = round(max(raw_damage / 10, 0.1), 1)
                absorbtion = round(self.hero.armor * self.hero.armor_eff, 1)
                nmy_damage = round(max(raw_damage - absorbtion, min_damage), 1)
                
                self.hero.health -= nmy_damage
                self.hero.health = max(self.hero.health, 0)

                message = s['hero_hit']
                tt = "Raw Damage: {0}<br />".format(raw_damage)
                tt += "Max Absorption: {0}".format(absorbtion)
                message = message.format(creature=self.ennemy['name'], crit=critic_msg, hero=self.hero.name, dam=nmy_damage)
                channel.addStory(message, tt)

                log.debug("Combat :: Armor / Absorbtion :: {0:.1f}, {1}".format(self.hero.armor, absorbtion))
                log.debug("Combat :: Ennemy hits (raw, min, final) :: {0}, {1}, {2}".format(raw_damage, min_damage, nmy_damage))
            else:
                message = s['blocked'][self.hero.job]
                message = message.format(creature=self.ennemy['name'], hero=self.hero.name)
                channel.addStory(message)

                log.info("Combat :: Blocked attack")

            # Apply any damage effect to the creature
            if 'Burning' in self.ennemy['effects']:
                log.info("Combat :: Ennemy is burning and looses health")
                modifier = 2 if 'Fire' in self.ennemy['weakness'] else 1
                lost = round(self.ennemy['hitpoints'] * 0.1 * modifier, 1)
                self.ennemy['hitpoints'] -= lost
                if self.ennemy['hitpoints'] <= 0:
                    message = s['burning_kill'].format(creature=self.ennemy['name'], lost=lost)
                    channel.addStory(message)
                    self.kill(channel, docks)
                else:
                    message = s['burning'].format(creature=self.ennemy['name'], lost=lost)
                    channel.addStory(message)

            if 'Poison' in self.ennemy['effects']:
                log.info("Combat :: Ennemy is poisoned and looses health")
                modifier = 2 if 'Poison' in self.ennemy['weakness'] else 1
                lost = round(self.ennemy['lvl'] * 0.1 * modifier, 1)
                self.ennemy['hitpoints'] -= lost
                if self.ennemy['hitpoints'] <= 0:
                    message = s['poison_kill'].format(creature=self.ennemy['name'], lost=lost)
                    channel.addStory(message)
                    self.kill(channel, docks)
                else:
                    message = s['poison'].format(creature=self.ennemy['name'], lost=lost)
                    channel.addStory(message)

            # clear debuffs if counter reached 0
            marked = []

            for debuff in self.ennemy['effects']:
                self.ennemy['effects'][debuff] -= 1
                if self.ennemy['effects'][debuff] == 0:
                    marked.append(debuff)

            log.debug("Combat :: Debuff marked for deletion {}".format(marked))

            for debuff in marked:
                del(self.ennemy['effects'][debuff])

            # increment stats
            self.damage_taken += nmy_damage

            # reset turn counter
            self.wait = -1

    def handleMoving(self, channel, docks):
        # default message
        message = ""

        # If the game was just reloaded, we may want to update some things
        if self.game_reloaded:
            self.game_reloaded = False

        if self.location == 'home':
            self.wait += 1

            # act depending on time spent at home
            if self.wait == 1:
                message = s['wake']
                message = message.format(hero=self.hero.name, him=self.hero.pronoun('him'))
                channel.addStory(message)
            elif self.wait == 2:
                message = s['leave_home']
                message = message.format(hero=self.hero.name, his=self.hero.pronoun('his'))
                self.wait = 0
                self.location = 'fields'
                channel.addStory(message)
            
        elif self.location == 'town':
            self.wait += 1
            if self.wait == 1:
                log.info("Town :: Visit Healer")
                self.hero.heal('healer')
                message = s['healer']
                message = message.format(hero=self.hero.name, him=self.hero.pronoun('him'))
                channel.addStory(message)

            if self.wait == 2:
                if self.hero.job == "Wizard" or self.hero.lvl > 1:
                    log.info("Town :: Restore Mana")
                    self.hero.mana_restore('healer')
                    message = s['healer_mana'].format(hero=self.hero.name)
                    channel.addStory(message)

            elif self.wait == 3:
                log.debug("Town :: Gold from sales :: {0}".format(self.hero.sell_value))
                if self.hero.sell_value > 0:
                    message = s['sell_item']
                    message = message.format(hero=self.hero.name, his=self.hero.pronoun('his'), gold=self.hero.sell_value)
                    channel.addStory(message)
                    self.hero.gold += self.hero.sell_value
                    self.hero.sell_value = 0
                    self.used_slots = 0

            elif self.wait == 4:

                gold = self.hero.gold / 3
                # WIzard buy 2 3rd mana, others 1 3rd
                if self.hero.job == "Wizard":
                    gold_mana = 2 * gold
                    gold_health = gold
                else:
                    gold_mana = gold
                    gold_health = 2 * gold

                # calculate the rest money and use it for the main potion needed
                rest = self.hero.gold - (gold_mana + gold_health)
                if self.hero.job == "Wizard":
                    gold_mana += rest
                else:
                    gold_health += rest


                gold_mana = int(gold_mana)
                gold_health = int(gold_health)

                if gold_mana + gold_health > self.hero.gold :
                    log.warning("Town :: health and mana budget exceed total gold")

                log.debug("Town :: Money for life :: {0}".format(gold_health))
                log.debug("Town :: Money for mana :: {0}".format(gold_mana))
                log.debug("Town :: Total gold :: {0}".format(self.hero.gold))


                # First: Health
                potion_type = self.hero.hpotion_type()
                price = hpotion_type[potion_type]

                nb_potion = min(int(gold_health / price), self.hero.belt_size - len(self.hero.hpotion_belt))
                self.hero.addHpotion(nb_potion, potion_type)
                self.hero.gold -= nb_potion * price
                if nb_potion > 0:
                    message = s['hpotion_restocked']
                    message = message.format(hero=self.hero.name, nb=nb_potion, type=potion_type, him=self.hero.pronoun('him'), his=self.hero.pronoun('his'))
                    channel.addStory(message)
                    log.debug("Town :: bought {0} {1}".format(nb_potion, potion_type))

                # Second: Mana
                potion_type = self.hero.mpotion_type()
                price = mpotion_type[potion_type]

                nb_potion = min(int(gold_mana / price), self.hero.belt_size - len(self.hero.mpotion_belt))
                self.hero.addMpotion(nb_potion, potion_type)
                self.hero.gold -= nb_potion * price

                if nb_potion > 0:
                    message = s['mpotion_restocked']
                    message = message.format(hero=self.hero.name, nb=nb_potion, type=potion_type, him=self.hero.pronoun('him'))
                    channel.addStory(message)
                    log.debug("Town :: bought {0} {1}".format(nb_potion, potion_type))

                # update belt
                channel.updateBelt()

            elif self.wait == 5:
                self.wait = 0
                # update stats
                self.town_trips += 1

                # if a dungeon is currently loaded, return to it, else go to the fields
                if self.dungeon['name']:
                    self.location = 'dungeon'
                else:
                    self.location = 'fields'

                message = s['resume']
                message = message.format(hero=self.hero.name, his=self.hero.pronoun('his'))
                channel.addStory(message)

        elif self.location == 'fields':
            # throw dice and calculate chance of event
            dice = d100()
            log.debug("Fields :: dice :: {}".format(dice))

            if dice > 95:
                # Try to generate a monster
                unique = False
                if dice > 99:
                    unique = True
                    
                hlvl = self.hero.lvl
                #lvl = choice([hlvl-1, hlvl-1, hlvl-1, hlvl, hlvl, hlvl, hlvl, hlvl, hlvl, hlvl+1])
                message = self.generateEnnemy(hlvl, unique)
                if message:
                    message = message.format(hero=self.hero.name, creature=self.ennemy['name'])
                    channel.addStory(message)
                    # Update the dock
                    docks['ennemy'].setWidget(EnnemyStats(self.ennemy))
                    log.debug("Fields :: Generated Ennemy :: {}".format(self.ennemy['name']))

            elif dice <= 15:
                # Try to generate a dungeon matching the hero's lvl
                if self.generateDungeon(self.hero.lvl):
                    self.location = 'dungeon'
                    message = s['discover_dungeon'].format(hero=self.hero.name, dungeon=self.dungeon['name'])
                    channel.addStory(message)
                    log.debug("Fields :: Generated Dungeon :: {}".format(self.dungeon['name']))

        elif self.location == 'dungeon':
            if self.dungeon['rooms'] == 0:
                log.info("Dungeon :: Cleared")
                lvl = self.hero.lvl
                message = s['cleared_dungeon']
                self.location = 'fields'
                message = message.format(hero=self.hero.name, dungeon=self.dungeon['name'], fields=self.verboseLocation(lvl))
                channel.addStory(message)
                if self.dungeon['unique']:
                    self.finished_dungeon.append(self.dungeon['id'])

                self.dungeon = dict(empty_dungeon)

                # update stats
                self.dungeon_cleared += 1

            elif self.dungeon['rooms'] == 1 and self.dungeon['unique_monster']:
                log.info("Dungeon :: Boss room")

                message = s['last_room'].format(hero=self.hero.name, room= self.dungeon['last_chamber'])
                channel.addStory(message)

                message = self.generateEnnemy(1, True, self.dungeon['unique_monster']) 
                if message:
                    message = message.format(hero=self.hero.name, creature=self.ennemy['name'])
                    channel.addStory(message) 
                    # Update the dock
                    docks['ennemy'].setWidget(EnnemyStats(self.ennemy))

                    # Taunt the Hero upon spawn
                    taunt = choice(self.ennemy['taunt'])
                    taunt = taunt.format(name=self.hero.name)
                    message = "<b>{0}</b> <i>{1}</i>".format(self.ennemy['name'], taunt)
                    channel.addStory(message) 

            else:
                dice = d100()
                log.debug("Dungeon :: dice :: {}".format(dice))
                if dice > 30:
                    unique = False
                    if dice > 99:
                        unique = True
                    hlvl = self.hero.lvl
                    #lvl = choice([hlvl-1, hlvl-1, hlvl, hlvl, hlvl, hlvl, hlvl+1, hlvl+1])
                    #log.debug("Dungeon :: Monster level chosen :: {}".format(lvl))
                    message = self.generateEnnemy(hlvl, unique, monster_list=self.dungeon['monsters'])
                    if message:
                        message = message.format(hero=self.hero.name, creature=self.ennemy['name'])
                        channel.addStory(message)
                        # Update the dock
                        docks['ennemy'].setWidget(EnnemyStats(self.ennemy))

                elif dice < 2:
                    message = s['found_chest'].format(hero=self.hero.name)
                    channel.addStory(message)
                    log.info("Dungeon :: Found a chest")

                    self.handleLootDrop(channel)

                    # update stats
                    self.chest_opened += 1
            
            # we explored one room, let's tick it off
            if self.dungeon['rooms']:
                self.dungeon['rooms'] = max(0, self.dungeon['rooms'] - 1)

    def kill(self, channel, docks):
        # calculate loot and XP
        unique = self.ennemy['unique']

        # increment stats and output death message for boss/champions
        if self.ennemy['unique'] > 1:
            self.unique_kills += 1
            self.killed_champ.append(self.ennemy['id'])
            death_message = self.ennemy['death'][self.hero.job]
            if len(death_message) > 0:
                channel.addStory("<b>{0}</b>  <i>{1}</i>".format(self.hero.name, death_message))

        earned_xp = int(self.ennemy['lvl'] * 100 * self.ennemy['strength'] * unique)
        earned_gold = int(self.ennemy['lvl'] + choice([1, 2, 3]) * unique * self.hero.gold_bonus * self.ennemy['strength'])

        self.hero.xp += earned_xp
        self.hero.gold += earned_gold

        # increment stat
        self.kills += 1
        self.xp_earned += earned_xp
        self.gold_earned += earned_gold            

        message = s['xp_earned']
        message = message.format(hero=self.hero.name, gold=earned_gold, xp=earned_xp)
        channel.addStory(message)
        log.info("Combat :: {0} killed for {1} xp and {2} gold".format(self.ennemy['name'], earned_xp, earned_gold))

        dice = d6()
        log.debug("Combat :: Loot dice :: {}".format(dice))

        if dice == 6:
            self.handleLootDrop(channel)

        if self.ennemy['loot']:
            self.handleLootDrop(channel)


        self.ennemy = dict(empty_ennemy)
        # Update the dock
        docks['ennemy'].setWidget(NoEnnemyStats())

    def inCombat(self):
        if not self.ennemy['name']:
            return False
        else:
            return True

    def returnToTown(self):
        self.location = 'town'

# Some tests
if __name__ == '__main__':

    debug = 'monstergeneration1'
    game = Game()

    if debug == 'fieldname':
        game.location = 'fields'
        for i in range(1, 80):
            print("{0}: {1}".format(i, game.verboseLocation(i)))
    elif debug == 'skill':
        print('skill: ', selectRandomSkill('Archer', 15))        
    elif debug == 'dungeongeneration1':
        for _ in range(20):
            lvl = choice([1,2,3,4,5])
            game.generateDungeon(lvl)
            print('Level {0}: {1}'.format(lvl, game.dungeon))
    elif debug == 'dungeonname':
        lvl = 4
        game.generateDungeon(lvl)
        game.location = 'dungeon'
        print('Room {0}: {1}'.format(game.dungeon['rooms'], game.verboseLocation(lvl)))
    elif debug == 'monstergeneration1':
        for _ in range(20):
            lvl = choice([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
            game.generateEnnemy(lvl)
            print('Level {0}: {1}'.format(lvl, game.ennemy))
    elif debug == 'monstergeneration2':
        for _ in range(5):
            lvl = 4
            game.generateEnnemy(lvl)
    elif debug == 'potion':
        life = 150
        potions = sorted(hpotion_type.items(), key=operator.itemgetter(1))
        for key, value in potions:
            if value < life / 2:
                continue
            else:
                potion_type = key
                price = value
                break
        print(potion_type, price)
