# Idle RPG

Idle RPG is a Idle game, a game that plays itself
It's based upon vague memory I have from a similar game that I "played" years ago.

On Idle games:

What you often see labelled Idle games, aren't really idle games because they require you to interact with the game to make progress. The correct name is Incremental games. Because the gameplay consist in incrementing stuff to progress.

Idle RPG is really an idle game because once, the game starts, you have no way of influencing it. The game plays itself.

## Gameplay

None

Well none involving the player.

## Current project status

[![Code Climate](https://codeclimate.com/github/DanielNautre/idle-rpg/badges/gpa.svg)](https://codeclimate.com/github/DanielNautre/idle-rpg)

## Hero

### Attributes

There are 4 main attributes

* Strength
* Intelligence
* Dexterity
* Vitality


### Stats

#### Blocking / Evasion

Blocking (called Evasion for the Archer) allows the Hero to avoid being hit by the ennemy.
It is hard capped a 75% chance of blocking and takes dexterity, Hero level and the gear bonus into account
Only shields, bows and crossbows provide a bonus towards Blocking / Evasion

#### Armor

Armor allows the player to absorb part of the damage received. It is hard capped a 90% meaning that no matter how much armor the player has, it will take at least 10% of the damage or 0.1 damage.
Armor is complemented by a secondary stat: Armor effectiveness. 
This determines how effective armor is. e.g.

10 armor at 80% effectiveness will absorb up to 8 damage. The player will take 2 damage
5 armor at 50% effectiveness will absorb up to 2.5 damage. The player will take 2.5 damage

Armor effectiveness depends on the Hero's class

#### Damage

Damage is determined based on the Hero's main attribut and the weapon he is currently holding.

### Classes

#### Paladin

The Paladin starts with higher Vitality and Strength and has a bonus to healing potion.
He is the only class who can equip a shield which increases his Block chance.
He also has the highest armor effectiveness: 80%


#### Wizard

The Wizard start with higher intelligence and has already learned a spell: Firebolt
It cannot wear a shield and can only equip Swords and Staves as weapons
It has the lowest armor effectiveness: 50%


#### Archer

The Archer start with high dexterity and a bonus to evasion
It is the only class who can use bows and crossbows which may provide a bonus to evasion
it has an armor effectiveness of 70%

### Gear

Your Hero may use a variety of gear. While most of the gear can be used by any classes, there are exceptions.

Bows and Crossbows can only be used by archers, Staves can only be used by Wizards and Shields, Axes, Maces, Flails can only be used by Paladins. Sword may only be used by Wizards and Paladins.

Starting at level 3, your Hero can find enchanted gear. and at level 10 you'll find gear with more enchants.

### Leveling up

Once the Hero has gained sufficient experience, he will gain a level. This will increase his vitality as well as his main attribut. His life and Mana will also be replenished. He will start encountering stronger ennemies and find better gear

### Death

Your Hero is not immortal, and he might fight an ennemy that is too strong for him. In which case, you have two options:

* Reload the latest save: with some luck, your Hero might survive this time
* Start a new character


## Ennemies

### Type

Ennemies can be of several types:

* Undead
* Demon
* Animal

Depending on their type, they mau also inflict various debuffs on the Hero (NOT YET IMPLEMENTED)

### Champions

Every once in a while, your Hero will stumble upon a Champion. This is a unique monster which has more hitpoints than usual and which is named. Champions may be stronger than the usual but not necessarly and they may drop unique loot.

### Resistance and Weakness

Each monster may have one or more Weakness and One or more Resistance. This influences how much damage the Hero does to it depending on the Spell / Weapon used.

Here is the list of possible weakness/resistance:

* Fire
* Ice
* Electricity
* Poison
* Arcane
* Sacred

### Kill

Once you have dealt enough damage to kill an ennemy you will be rewarded with experience points (xp) and gold.

### Loot

Once an ennemy has been disposed of, you will be able to loot its body. There is a 1 out of 6 chance to find something. 

## Combat

Combat is turn based. When a combat is started, the Hero will start and perform an action, then on the next turn, the ennemy will perform its action and so on.

When it is time for the Hero to attack, the game will try to guess which is the best action to take. Depending on the results, the Hero will either cast a spell or straigth up use his weapon. If the Hero deals a killing blow, he will get gold, XP and possibly some loot. If the ennemy survives, it will attack the Hero on the next turn. The Hero can try to block/evade. This depends on the corresponding value in the Hero's stats. If this is not successful, the Hero will be hit and loose health depending on the ennemy's strength and the Hero's armor. Ennemies can deal weak or critical hits which affects the amount of damage dealt.

### Spells

Hero's will learn various spells on their journey. The Wizard is the only class who already knows a spell when the adventure starts. Casting a spell will use the Hero's mana. The amount of mana used up depends on the spell and it's level.

Every time the Hero finds a spell Tome, he will have a chance to improve or learn a spell. Spells have an attribut requirement, meaning they require the Hero main attribut to have a minimum value before they can be learned/improved, this value increases with the spell level.

Everytime the Hero improves a spell, its mana cost decreases. This is caped, spells have a minimum mana cost. 

Some spells may also have gear requirements. (NOT YET IMPLEMENTED)

### Debuffs

Spells and weapons may inflict debuffs on ennemies. This is determined by the type of damage of the spell/weapon. These have various effects listed below:

The chance that the effects are applied as well as the length of the effect depends on the spell used. 
Weapons get a fixed 10% chance of inflicting the corresponding effect and a fixed length for each effect.

* Ice      -> Stunned: The ennemy cannot attack on the next turn
* Fire     -> Burning: The ennemy will lose 10% of his hitpoints at the end of its turn for X turns 
* Poison   -> Poissoned : The ennemy will lose 10% of its level as hitpoints at the end of its turn for X turns 
* Electric -> Weakness: The ennemy looses 10% of its strength until the end of the combat

The damage is increased if the ennemy has a matching weakness, but if it has a matching resistance, then the effect will not be applied.

## Locations

### Home

This is the place where the adventure starts. There isn't much to say: When you first start a character, you'll be at his home which he will promptly leave and never visit again.

### Town

Every once in a while you Hero may go back to town where he will perform a number of actions:

* Visit the Healer to restore his health
* visit the Enchanter to restore his mana
* Sell the gear he found and do not want to use
* Buy Health and Mana potions

### Dungeons

Dungeons are generately randomly from a predefined list. When travelling, your Hero has a certain chance of stumbling upon a dungeon.
Your Hero will always enter them when he finds them.
Dungeons are generated based on your Hero's level.
There is a slightly higher chance of finding a champion in a dungeon than outside.


#### Chests

While visiting a dungeon, your hero has a chance of finding a chest which contains random loot. This includes: 

* Gear
* Potions
* Spell Tomes
* Attribut Potions

#### Unique Dungeons

Every time a new dungeon is generated, there is a small chance it will be a unique dungeon. Unique dungeons have their own name and will generally feature a unique boss in the last room.

## Items

### Gear

Your Hero being as real badass, he start the adventure in his pajamas. It turns out, it's not an effective strategy to fight the forces of evil. Luckily, he will quickly start to find various piece of equipment by looting his ennemies or by finding chests in dungeons.

Items found by the Hero have always the same level as the Hero.

If the Hero decides that the equipment piece he is currently wearing is better than the one he found, he will keep the new gear to sell it later.

The Hero can hold on to 20 items before he has to sell them.

#### Enchantements

Starting at level 3 your Hero will find enchanted gear. At level 10 enchanting gear will be more frquent and will have more enchants.

Enchanted gear is garanteed to have one of the following enchants:

* Bonus to Vitality
* Bonus to main attribut (Strength for Paladins, Intelligence for Wizards, and Dexterity for Archers)
* Bonus to all 4 attributs

Adding to the main enchant, items may have 0 to 3 additionnal enchants taken from the list below.

* Bonus to armor (only for armor pieces)
* Bonus to damage (only for weapons)
* Damage type (only for weapons)
* Mana regeneration per tick
* Health regeneration per tick
* Bonus Gold per kill (only for jewels)
* Bonus max. Life
* Bonus max. Mana 

##### Damage Type

This is a special enchant for weapon which add 10% damage to the weapon in the form of special elemental damage.
This bonus is subjet to weakness and resistance of the target.


#### Naming

Item are named depending on their type and their level. e.g: a level 5 mace is a Morning Star
If the item is enchanted it will have a suffix and possibly a prefix depending on the enchants.


### Potions

The game feature two main potion types: Health and Mana

These come in 10 different sizes depending on how much Life/Mana they regenerate. 
How many potions the Hero can hold on to depends on whether or not he wears a belt and the level of his belt.
The Hero can carry up to 8 potions of each type with a level 10 belt


### Attribut Potions (need better name)

Starting at level 25, there is a rare chance that the hero may find special potions which will permanently increase one of his main attribute (Intelligence, Dexterity, Strength, Vitality). 



## Credits

Game icons come from http://game-icons.net/

Menu icons are from the Tango icon set: http://tango-project.org/

## Contributions

Contributions in any form are most welcome.
