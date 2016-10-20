#!/usr/bin/python3
# -*- coding: utf8 -*

from collections import deque, defaultdict
from item import Item
from random import choice

import operator

# Import other files from the project
from dice import d6, d20, d100

# Import logger
from logger import log, story

# Import config & data
from data import oskill_list, hpotion_type, mpotion_type, s, pronouns
from config import job_stats

class Hero(object):

    def __init__(self, job='Wizard', gender='male', name='Gandalf'):
        super(Hero, self).__init__()

        # initiate base value of the player
        self.lvl = 1
        self.xp = 0
        self.next_lvl = self.nextLvl()
        self.job = job
        self.gender = gender
        self.name = name
        self.gold = 0
        self.sell_value = 0
        self.hpotion_belt = deque(['Minor Health Potion', 'Minor Health Potion'])
        self.mpotion_belt = deque()
        self.offensive_skills = {}
        self.buffs = defaultdict(list)

        # base attribut value, only increased by lvl up
        # used as a base to calculate the real value used by other stats

        # Mana max, mana potion, magic damage
        self.base_intelligence = job_stats[self.job]['intelligence']
        # Melee damage, armor type
        self.base_strength = job_stats[self.job]['strength']
        # Archer damage, martial art damage, chance of block, attack speed
        self.base_dexterity = job_stats[self.job]['dexterity']
        # health max
        self.base_vitality = job_stats[self.job]['vitality']
        # main attribut
        self.main = job_stats[self.job]['main']
        # How effective the armor is depends on the class
        self.armor_eff = job_stats[self.job]['armor']

        # Base gear: None
        self.gear = {'weapon': None, 'armor': {'shield': None, 'chest': None, 'pants': None, 'gloves': None, 'boots': None, 'helm': None, 'shoulders': None, 'bracers': None, 'belt': None}, 'jewel': {'ring': None, 'amulet': None}}
        
        # Calculate modifier based on class
        self.healing_modifier = 1.5 if self.job == 'Paladin' else 1
        self.mana_modifier = 1.5 if self.job == 'Wizard' else 1
        self.base_blocking = 10 if self.job == 'Archer' else 5

        # calculate all stats based on the above
        self.deriveSecondaryStats()

        # Wizard as no block, no armor or increased strength, so it gets a spell and mana 
        if self.job == 'Wizard':                    
            self.addSkill('firebolt')
            self.mpotion_belt.append('Minor Mana Potion')
            self.mpotion_belt.append('Minor Mana Potion')

        # Set health to max and mana to default value
        self.health = self.health_max
        self.mana = self.mana_max if self.job == 'Wizard' else 0

        self.inventory_slots = 20
        self.used_slots = 0

    def save(self):
        data = {}
        data['name'] = self.name
        data['lvl'] = self.lvl
        data['xp'] = self.xp
        data['next_lvl'] = self.next_lvl
        data['job'] = self.job
        data['gold'] = self.gold
        data['sell_value'] = self.sell_value
        data['hpotion_belt'] = self.hpotion_belt
        data['mpotion_belt'] = self.mpotion_belt
        data['offensive_skills'] = self.offensive_skills
        data['base_intelligence'] = self.base_intelligence
        data['base_strength'] = self.base_strength
        data['base_dexterity'] = self.base_dexterity
        data['base_vitality'] = self.base_vitality
        data['armor_eff'] = self.armor_eff
        data['main'] = self.main
        data['gear'] = self.gear
        data['healing_modifier'] = self.healing_modifier
        data['mana_modifier'] = self.mana_modifier
        data['base_blocking'] = self.base_blocking
        data['health'] = self.health
        data['mana'] = self.mana
        data['buffs'] = self.buffs
        data['used_slots'] = self.used_slots

        return data

    def load(self, data):
        self.name = data['name']
        self.lvl = data['lvl']
        self.xp = data['xp']
        self.next_lvl = data['next_lvl']
        self.job = data['job']
        self.gold = data['gold']
        self.sell_value = data['sell_value']
        self.hpotion_belt = data['hpotion_belt']
        self.mpotion_belt = data['mpotion_belt']
        self.offensive_skills = data['offensive_skills']
        self.base_intelligence = data['base_intelligence']
        self.base_strength = data['base_strength']
        self.base_dexterity = data['base_dexterity']
        self.base_vitality = data['base_vitality']
        self.armor_eff = data['armor_eff']
        self.main = data['main']
        self.gear = data['gear']
        self.healing_modifier = data['healing_modifier']
        self.mana_modifier = data['mana_modifier']
        self.base_blocking = data['base_blocking']
        self.health = data['health']
        self.mana = data['mana']    
        self.buffs = data['buffs']    
        self.used_slots = data['used_slots']    

    def deriveSecondaryStats(self):
        self.next_lvl = self.nextLvl()
        self.addGearAttBonus()

        # max mana and health
        self.health_max = int(((self.vitality * 10) + (self.lvl * 8)) / 10)
        self.mana_max = int(((self.intelligence * 10) + (self.lvl * 8)) / 10)


        self.mana_regen = 0
        self.life_regen = 0
        self.gold_bonus = 1

        self.armor = 0

        # weaopn damage values
        if not self.gear['weapon']:
            self.base_damage_max = 2
            self.base_damage_min = 1     
        else:
            self.base_damage_max = self.gear['weapon'].damage_max
            self.base_damage_min = self.gear['weapon'].damage_min

        if self.job =='Paladin':
            dam_att = self.strength
        elif self.job == 'Archer':
            dam_att = self.dexterity
        elif self.job == 'Wizard':
            dam_att = self.intelligence

        self.damage_max = int(self.base_damage_max * (dam_att + 100) / 100)
        self.damage_min = int(self.base_damage_min * (dam_att + 100) / 100)

        # take gear into account for secondary bonus
        # Armor, Blocking, Max Health, Max Mana, improved Damage
        self.addGearSecondaryBonus()

        self.belt_size = 4
        if self.gear['armor']['belt']:
            if self.gear['armor']['belt'].lvl < 10:
                self.belt_size += 2
            if self.gear['armor']['belt'].lvl >= 10:
                self.belt_size += 4


        # Calculate Block chance based on Blocking, Dexterity and clvl
        dext = max(self.dexterity - 5, 1)
        block = ((self.blocking * dext) / (self.lvl * 2))
        self.block_chance = int(min(block, 75))
       
    def addGearAttBonus(self):
        self.intelligence = self.base_intelligence
        self.strength = self.base_strength
        self.dexterity = self.base_dexterity
        self.vitality = self.base_vitality

        for id, stuff in iter(self.gear['armor'].items()):
            if stuff:
                if stuff.enchanted:
                    for key, value in iter(stuff.enchant.items()):
                        if key == 'int': 
                            self.intelligence += value
                        if key == 'dex': 
                            self.dexterity += value
                        if key == 'str': 
                            self.strength += value
                        if key == 'vit': 
                            self.vitality += value
                        if key == 'all':
                            self.intelligence += value
                            self.dexterity += value
                            self.strength += value
                            self.vitality += value


        for id, stuff in iter(self.gear['jewel'].items()):
            if stuff:
                if stuff.enchanted:
                    for key, value in iter(stuff.enchant.items()):
                        if key == 'int': 
                            self.intelligence += value
                        if key == 'dex': 
                            self.dexterity += value
                        if key == 'str': 
                            self.strength += value
                        if key == 'vit': 
                            self.vitality += value
                        if key == 'all':
                            self.intelligence += value
                            self.dexterity += value
                            self.strength += value
                            self.vitality += value
        
        if self.gear['weapon']:
            if self.gear['weapon'].enchanted:
                for key, value in iter(self.gear['weapon'].enchant.items()):
                    if key == 'int': 
                        self.intelligence += value
                    if key == 'dex': 
                        self.dexterity += value
                    if key == 'str': 
                        self.strength += value
                    if key == 'vit': 
                        self.vitality += value
                    if key == 'all':
                        self.intelligence += value
                        self.dexterity += value
                        self.strength += value
                        self.vitality += value

    def addGearSecondaryBonus(self):

        self.blocking = self.base_blocking

        for id, stuff in iter(self.gear['armor'].items()):
            if stuff:
                self.armor += stuff.armor
                # add shield blocking value
                if stuff.subtype == 'shield':
                    self.blocking += stuff.block
                if stuff.enchanted:
                    for key, value in iter(stuff.enchant.items()):
                        if key == 'mana': 
                            self.mana_max += value
                        if key == 'life': 
                            self.mana_max += value
                        if key == 'mana_regen': 
                            self.mana_regen += value
                        if key == 'life_regen': 
                            self.life_regen += value
                        if key == 'armor':
                            self.armor += value

        for id, stuff in iter(self.gear['jewel'].items()):
            if stuff:
                if stuff.enchanted:
                    for key, value in iter(stuff.enchant.items()):
                        if key == 'mana': 
                            self.mana_max += value
                        if key == 'life': 
                            self.mana_max += value
                        if key == 'mana_regen': 
                            self.mana_regen += value
                        if key == 'life_regen': 
                            self.life_regen += value
                        if key == 'gold':
                            self.gold_bonus += value

        if self.gear['weapon']:
            # add evasion bonus given by the bow
            if self.gear['weapon'].subtype in ['crossbow','bow']:
                self.blocking += self.gear['weapon'].evasion

            if self.gear['weapon'].enchanted:
                for key, value in iter(self.gear['weapon'].enchant.items()):
                    if key == 'mana': 
                        self.mana_max += value
                    if key == 'life': 
                        self.mana_max += value
                    if key == 'mana_regen': 
                        self.mana_regen += value
                    if key == 'life_regen': 
                        self.life_regen += value

    def addMpotion(self, nb_potion, potion_type):
        for _ in range(nb_potion):
            self.mpotion_belt.append(potion_type)

    def addHpotion(self, nb_potion, potion_type):
        for _ in range(nb_potion):
            self.hpotion_belt.append(potion_type)

    def addSkill(self, name):
        if name in list(self.offensive_skills):
            # try to increase skill lvl, if hero lvl high enough
            if self.baseAtt() < self.offensive_skills[name]['next_att']:
                log.info("Hero :: Not strong enough to improve skill")
                log.debug("Hero :: required, actual :: {0}, {1}".format(self.offensive_skills[name]['next_att'], self.baseAtt()))

                return False
            else:
                log.info("Hero :: Skill improved :: {}".format(name))
                self.offensive_skills[name]['lvl'] += 1

                # calculate next attribut level required
                # lvl + step + 1 + current_att
                next_att = self.offensive_skills[name]['next_att'] + oskill_list[name]['step_att']
                next_att = next_att + self.offensive_skills[name]['lvl']

                # calculate cost
                cost = oskill_list[name]['base_cost'] - ((self.offensive_skills[name]['lvl'] - 1) * oskill_list[name]['step_cost'])

                self.offensive_skills[name]['cost'] = cost
                self.offensive_skills[name]['next_att'] = next_att

                return 'improved'

        else:
            if self.baseAtt() < oskill_list[name]['base_att']:
                log.info("Hero :: Not strong enough to learn skill")
                log.debug("Hero :: required, actual :: {0}, {1}".format(oskill_list[name]['base_att'], self.baseAtt()))
                return False
            else:
                log.info("Hero :: Learned new skill :: {}".format(name))
                skill = {}
                skill['name'] = oskill_list[name]['name']
                skill['lvl'] = 1

                # calculate next attribut level required
                # lvl + step + 1 + base
                next_att = oskill_list[name]['base_att'] + oskill_list[name]['step_att'] + 1

                # calculate cost
                cost = max(oskill_list[name]['base_cost'], oskill_list[name]['min_cost'])

                skill['damage'] = oskill_list[name]['damage']
                skill['cost'] = cost
                skill['next_att'] = next_att
                self.offensive_skills[name] = skill

                return 'added'

    def bestSkill(self, damage, weakness, resistance):
        # calculate most effective skill to use to kill an opponent
        # default is weapon, always available
        default_skill = 'weapon'
        # first, weapon hit. Assume min damage, 
        # if we can kill it in one hit, go for it
        
        weapon_damage = self.damage_min

        # Take ennemy weakness nad weapon debuff into account
        if self.gear['weapon']:
            if self.gear['weapon'].enchanted:
                if 'damage' in self.gear['weapon'].enchant:
                    weapon_damage += self.gear['weapon'].enchant['damage']
                if 'debuff' in self.gear['weapon'].enchant:
                    if self.gear['weapon'].enchant['debuff'] in weakness:
                        # if weapon debuff matches weakness: +20% damage
                        weapon_damage += weapon_damage * 0.2
                        log.debug("Hero :: +10% damage because weapon has {} enchant which matches ennemy weakness".format(self.gear['weapon'].enchant['debuff']))
                    elif self.gear['weapon'].enchant['debuff'] in resistance:
                        # if weapon debuff matches resistance: -10% damage
                        weapon_damage -= weapon_damage * 0.1
                        log.debug("Hero :: -10% damage because weapon has {} enchant which matches ennemy resistance".format(self.gear['weapon'].enchant['debuff']))
                    else:
                        # weapon debuff causes +10% special damage in any case
                        weapon_damage += weapon_damage * 0.1
                        log.debug("Hero :: +10% damage because weapon has {} enchant".format(self.gear['weapon'].enchant['debuff']))

        if 'Physical' in weakness:
            weapon_damage += weapon_damage * 0.1
            log.debug("Hero :: Increased weapon damage due to ennemy weakness :: {}".format(weakness))
        elif 'Physical' in resistance:
            weapon_damage -= weapon_damage * 0.1
            log.debug("Hero :: Decreased weapon damage due to ennemy resistance :: {}".format(weakness))

        log.debug("Hero :: weapon will do at least {} damage".format(weapon_damage))
        if damage <= weapon_damage:
            return default_skill

        # test skills
        skill_over = {}
        skill_under = {}
        skill_tactical = {}

        for skill in list(self.offensive_skills):
            if self.mana < self.offensive_skills[skill]['cost']:
                # not enough mana for this skill, try another
                log.debug("Hero :: cannot use {0} :: need {1} mana, {2:.1f} available".format(skill, self.offensive_skills[skill]['cost'], self.mana))
                continue

            if not self.skillReqMet(skill):
                continue

            # calculate the min amount of damage the skill can do
            skill_damage = self.calcSkillMinDamage(skill)

            if skill_damage == 0:
                if skill not in ['heal']:
                    skill_tactical[skill] = oskill_list[skill]['duration']

            # take ennemy weakness into account
            if oskill_list[skill]['type'] in weakness:
                log.info("Hero: Skill {} has increased damage due to creature weakness".format(skill))
                log.debug("Hero :: skill has {0} type, Creature is weak to {1}".format(oskill_list[skill]['type'], weakness))
                skill_damage += skill_damage * 0.1

            if oskill_list[skill]['type'] in resistance:
                log.info("Hero: Skill {} has decreased damage due to creature resistance".format(skill))
                log.debug("Hero :: skill has {0} type, Creature resists to {1}".format(oskill_list[skill]['type'], weakness))
                skill_damage -= skill_damage * 0.1

            log.debug("Hero :: {0} will cause at least {1} damage".format(skill, skill_damage))

            overhead = damage - skill_damage
            log.debug("Hero :: skill / distance to ennemy hitpoint :: {0} / {1:.1f}".format(skill, overhead))

            if overhead <= 0:
                # make a list of skill and how much they cost
                skill_over[skill] = self.offensive_skills[skill]['cost']
                log.debug("Hero :: Mana use :: {0}: {1:.1f}".format(skill, skill_over[skill]))

            if overhead > 0:
                # make a list of non-killing skill and how much damage they do
                skill_under[skill] = skill_damage


        # if we overshoot the kill, let's use the less mana possible
        if len(skill_over) > 0:
            sorted_skill = sorted(skill_over.items(), key=operator.itemgetter(1))
            return sorted_skill[0][0]

        # if we can't overshoot the kill, calculate if 2 weapon hit would kill       
        if damage <= weapon_damage * 2: 
            return default_skill

        highest_damage = sorted(skill_under.items(), key=operator.itemgetter(1), reverse=True)

        # if ennemy has more than 5 times the best damage we guess we will cause. try a tactical skill
        if len(highest_damage) > 0 and len(skill_tactical) > 0:
            sorted_skill = sorted(skill_tactical.items(), key=operator.itemgetter(1), reverse=True)
            if damage > 5 * highest_damage[0][1]:
                for skill, value in sorted_skill:
                    if oskill_list[skill]['type'] in weakness:
                        return skill
                # if we haven't found a skill matching his weakness, return the skill with the longest duration
                return sorted_skill[0][0]

        # If that doesn't work, do maximal amount of damage with a skill
        if len(skill_under) > 0:
            return highest_damage[0][0]

        # if no good skill found (or no mana), use the default
        return default_skill

    def skillReqMet(self, skill):
        if oskill_list[skill]['requirement']:
            req = oskill_list[skill]['requirement'].split()
            if req[0] == 'weapon':
                if req[1] in self.gear['weapon'].subtype:
                    log.debug("Hero :: cannot use {0} :: need {1}".format(skill, req))
                    return False
            elif req[0] == 'armor':
                if not self.gear['armor'][req[1]]:
                    log.debug("Hero :: cannot use {0} :: need {1}".format(skill, req))
                    return False
        return True


    def calcSkillMinDamage(self, skill):
        slvl =  self.offensive_skills[skill]['lvl'] if skill in self.offensive_skills else 0

        if 'min_damage' in list(oskill_list[skill]):
            s = oskill_list[skill]['min_damage']
            s = s.format(d6=1, d20=1, d100=1, clvl=self.lvl, slvl=slvl, int=self.intelligence, weapon=self.damage_max)
        else:
            s = oskill_list[skill]['damage']
            s = s.format(d6=1, d20=1, d100=1, clvl=self.lvl, slvl=slvl, int=self.intelligence, weapon=self.damage_max)

        damage = eval(s)

        return damage

    def calcSkillMaxDamage(self, skill):
        slvl =  self.offensive_skills[skill]['lvl'] if skill in self.offensive_skills else 0

        s = oskill_list[skill]['damage']
        s = s.format(d6=6, d20=20, d100=100, clvl=self.lvl, slvl=slvl, int=self.intelligence, weapon=self.damage_max)

        damage = eval(s)

        return damage

    def calcSkillDamage(self, skill):
        slvl =  self.offensive_skills[skill]['lvl'] if skill in self.offensive_skills else 0

        s = oskill_list[skill]['damage']
        s = s.format(d6=d6(), d20=d20(), d100=d100(), clvl=self.lvl, slvl=slvl, int=self.intelligence, weapon=self.damage_max)
        damage = eval(s)

        if 'min_damage' in list(oskill_list[skill]):
            s = oskill_list[skill]['min_damage']
            s = s.format(d6=d6(), d20=d20(), d100=d100(), clvl=self.lvl, slvl=slvl, int=self.intelligence, weapon=self.damage_max)
            min_damage = eval(s)

            dice = d20()
            log.debug("Hero :: Skill Damage Dice :: {}".format(dice))

            if dice > 12:
                pass
            elif dice < 5:
                damage = min_damage
            else:
                damage = (min_damage + damage) / 2

        return damage

    def useSkill(self, skill, weakness, resistance):
        if skill == 'weapon':
            dice = d20()
            log.debug("Hero :: Skill Damage Dice :: {}".format(dice))

            if dice > 12:
                damage = self.damage_max
            elif dice < 5:
                damage = self.damage_min
            else:
                damage = (self.damage_min + self.damage_max) / 2

            if self.gear['weapon']:
                if self.gear['weapon'].enchanted:
                    if 'damage' in self.gear['weapon'].enchant:
                        damage += self.gear['weapon'].enchant['damage']
                    if 'debuff' in self.gear['weapon'].enchant:
                        if self.gear['weapon'].enchant['debuff'] in weakness:
                            # if weapon debuff matches weakness: +20% damage
                            damage += damage * 0.2
                            log.debug("Hero :: +10% damage because weapon has {} enchant which matches ennemy weakness".format(self.gear['weapon'].enchant['debuff']))
                        elif self.gear['weapon'].enchant['debuff'] in resistance:
                            # if weapon debuff matches resistance: -10% damage
                            damage -= damage * 0.1
                            log.debug("Hero :: -10% damage because weapon has {} enchant which matches ennemy resistance".format(self.gear['weapon'].enchant['debuff']))
                        else:
                            # weapon debuff causes +10% special damage in any case
                            damage += damage * 0.1
                            log.debug("Hero :: +10% damage because weapon has {} enchant".format(self.gear['weapon'].enchant['debuff']))

            if 'Physical' in weakness:
                damage += damage * 0.1
                log.debug("Hero :: Increased weapon damage due to ennemy weakness :: {}".format(weakness))
            elif 'Physical' in resistance:
                damage -= damage * 0.1
                log.debug("Hero :: Decreased weapon damage due to ennemy resistance :: {}".format(weakness))


            return round(damage, 1)
        else:
            if self.offensive_skills[skill]['cost'] > self.mana:
                return 0

            if oskill_list[skill]['damage'] == 0:
                return 0

            damage = self.calcSkillDamage(skill)
            self.mana = round(self.mana - self.offensive_skills[skill]['cost'], 1)

            if oskill_list[skill]['type'] in weakness:
                damage += damage * 0.1   
                log.debug("Hero :: Increased spell damage due to ennemy weakness :: {}".format(weakness))
            elif oskill_list[skill]['type'] in resistance:
                damage -= damage * 0.1   
                log.debug("Hero :: Decreased spell damage due to ennemy resistance :: {}".format(weakness))            

            return round(damage, 1)

    def healthLow(self):
        if len(self.hpotion_belt) > 0:
            next_potion = hpotion_type[self.hpotion_belt[0]]
        else:
            next_potion = self.health_max

        if self.health < self.lvl + 2:
            return True
        elif self.health + next_potion <= self.health_max:
            return True
        else:
            return False

    def heal(self, method='potion'):
        if method == 'potion':
            if len(self.hpotion_belt) < 1:
                return False
            potion = self.hpotion_belt.popleft()
            restore = int(hpotion_type[potion] * self.healing_modifier)
            self.health = min(self.health_max, self.health + restore)
            return restore
        elif method == 'healer':
            self.health = self.health_max
        elif method == 'spell':
            log.debug("Hero ::  Try healing spell")
            if len(self.offensive_skills) == 0:
                return False
            for skill in self.offensive_skills:
                if oskill_list[skill]['type'] == "Healing":
                    if self.offensive_skills[skill]['cost'] > self.mana:
                        log.debug("Hero ::  Healing spell too expensive")
                        return False
                    self.health += self.health_max * 0.5
                    self.health = max(self.health, self.health_max)
                    self.mana -= self.offensive_skills[skill]['cost']
                    log.debug("Hero :: Used Healing Spell")
                    return True
            log.debug("Hero :: No Healing spell available")
            return False
        return True

    def manaLow(self):
        min_mana = self.mana_max
        for skill in list(self.offensive_skills):
            if min_mana > self.offensive_skills[skill]['cost']:
                min_mana = self.offensive_skills[skill]['cost']

        if len(self.mpotion_belt) > 0:
            next_potion = mpotion_type[self.mpotion_belt[0]]
        else:
            next_potion = self.mana_max

        if len(self.offensive_skills) == 0:
            return False
        elif self.mana < min_mana:
            return True
        elif self.mana + next_potion <= self.mana_max:
            return True
        else:
            return False

    def mana_restore(self, method='potion'):
        if method == 'potion':
            if len(self.mpotion_belt) < 1:
                return False
            potion = self.mpotion_belt.popleft()
            restore = int(mpotion_type[potion] * self.mana_modifier)
            self.mana = min(self.mana_max, self.mana + restore)
            return restore
        elif method == 'healer':
            self.mana = self.mana_max

        pass

    def hpotion_type(self):
        potions = sorted(hpotion_type.items(), key=operator.itemgetter(1))
        for key, value in potions:
            if (value * self.healing_modifier) <= self.health_max / 2:
                continue
            else:
                log.debug("Hero :: potion type :: {}".format(key))
                return key

    def mpotion_type(self):
        potions = sorted(mpotion_type.items(), key=operator.itemgetter(1))
        for key, value in potions:

            if (value * self.mana_modifier) <= self.mana_max / 2:
                continue
            else:
                log.debug("Hero :: potion type :: {}".format(key))
                return key

    def needsHPotion(self):
        money = hpotion_type[self.hpotion_type()]
        if len(self.hpotion_belt) == 0:
            if self.job == 'Wizard':
                if self.gold / 3 > money:
                    return True
            else:
                if (self.gold / 3) * 2 > money:
                    return True

        return False

    def needsMPotion(self):
        money = mpotion_type[self.mpotion_type()]
        if len(self.mpotion_belt) == 0 and self.job == 'Wizard':
            if (self.gold / 3) * 2 > money:
                return True
        return False

    def regen(self):
        self.mana = min(self.mana + self.mana_regen, self.mana_max)
        self.health = min(self.health + self.life_regen, self.health_max)

    def lvlUp(self):
        self.lvl += 1
        overflow = int(self.xp - self.next_lvl)
        self.xp = overflow

        self.base_vitality += 2

        if self.job == 'Wizard':
            self.base_intelligence += 2
        elif self.job == 'Paladin':
            self.base_strength += 2    
        elif self.job == 'Archer':
            self.base_dexterity += 2

        # Every 2 level, the hero gains 1 bonus intelligence (for mana needs)
        if self.lvl % 2 == 0:
            self.base_intelligence += 1

        # recalculate all stats
        self.recalculate()

        # set health to max
        self.heal('healer')
        self.mana_restore('healer')

        # select message for the lvlUp
        log.info("Hero :: LVL UP")
        return choice(s['lvl_up'][self.job])

    def nextLvl(self):
        return 500 * pow(self.lvl, 2) + 600 * self.lvl

    def equip(self, item):
        # test if item can be equipped

        if item.type != 'weapon':
            if not self.gear[item.type][item.subtype]:
                log.info('Hero :: Equip item (empty slot)')
                self.gear[item.type][item.subtype] = item
                return True            
            elif self.gear[item.type][item.subtype].compare(item, self.main):
                log.info('Hero :: Equip item (better item)')
                self.sell_value += self.gear[item.type][item.subtype].value()
                self.gear[item.type][item.subtype] = item
                return True
            elif self.inventory_slots > self.used_slots:
                value = item.value()
                self.sell_value += value
                self.used_slots += 1
                log.info('Hero :: Sell item :: {}'.format(value))
                return False
            else:
                log.info('Hero :: Drop item (not enough space in inventory) :: {}'.format(value))
                return False
        else:
            if not self.gear['weapon']:
                log.info('Hero :: Equip item (empty slot)')
                self.gear['weapon'] = item
                return True            
            elif self.gear['weapon'].compare(item, self.main):
                log.info('Hero :: Equip item (better item)')
                self.sell_value += self.gear['weapon'].value()
                self.gear['weapon'] = item
                return True
            elif self.inventory_slots > self.used_slots:
                value = item.value()
                self.sell_value += value
                self.used_slots += 1
                log.info('Hero :: Sell weapon :: {}'.format(value))
                return False
            else:
                log.info('Hero :: Drop item (not enough space in inventory) :: {}'.format(value))
                return False
        
    def baseAtt(self):
        if self.job == 'Wizard':
            return self.intelligence
        elif self.job == 'Paladin':
            return self.strength
        elif self.job == 'Archer':
            return self.dexterity

    def pronoun(self, kind):
        return pronouns[self.gender][kind]

    def recalculate(self):
        self.addGearAttBonus()
        self.deriveSecondaryStats()

    def __str__(self):
        string = "Health: {0} / {1:0.1f}\n".format(self.health, self.health_max)
        string += "Mana: {0} / {1:0.1f}\n".format(self.mana, self.mana_max)
        string += "Gold: {0} + {1}\n".format(self.gold, self.sell_value)
        return string
