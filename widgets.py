#!/usr/bin/python3
# -*- coding: utf8 -*

# Import Graphic Lib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolTip, QPushButton, 
    QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
    QFormLayout, QDockWidget, QListWidget, QListWidgetItem, QAction, qApp, 
    QButtonGroup, QProgressBar, QSpacerItem, QTabWidget, QScrollArea, QFrame, QGridLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap

from item import verboseEnchants, verboseSubtype

# Import logger
from logger import log, story

# Import config & data
from data import hpotion_type, mpotion_type, oskill_list, PATH


class HeroSelection(QWidget):
    def __init__(self, parent=None):
        super(HeroSelection, self).__init__(parent)
        self.initUI()
        self.job = None
        self.gender = None
        self.name = None

    def initUI(self):
        # Create the Hero selection UI
        
        # Create the layouts
        fbox = QFormLayout()
        hbox_job = QHBoxLayout()
        hbox_gender = QHBoxLayout()
        hbox_create = QHBoxLayout()
        layout = QHBoxLayout()

        # Create the buttons and field

        btn_archer = QPushButton('Archer', self)
        btn_paladin = QPushButton('Paladin', self)
        btn_wizard = QPushButton('Wizard', self)

        btn_archer.setCheckable(True)
        btn_paladin.setCheckable(True)
        btn_wizard.setCheckable(True)

        btn_archer.pressed.connect(lambda: self.selectJob('Archer'))
        btn_paladin.pressed.connect(lambda: self.selectJob('Paladin'))
        btn_wizard.pressed.connect(lambda: self.selectJob('Wizard'))

        btn_archer.setToolTip('Bows are cool')
        btn_paladin.setToolTip('A warrior of the light')
        btn_wizard.setToolTip('A powerful Hero making use of his arcane knowledge to fight evil')

        btn_male = QPushButton('Male', self)
        btn_female = QPushButton('Female', self)
        
        btn_male.setCheckable(True)
        btn_female.setCheckable(True)
        
        btn_male.pressed.connect(lambda: self.selectGender('male'))
        btn_female.pressed.connect(lambda: self.selectGender('female'))
        
        btns_job = QButtonGroup(self)
        btns_gender = QButtonGroup(self)

        btns_job.addButton(btn_archer)
        btns_job.addButton(btn_paladin)
        btns_job.addButton(btn_wizard)

        btns_gender.addButton(btn_male)
        btns_gender.addButton(btn_female)

        btns_job.setExclusive(True)
        btns_gender.setExclusive(True)

        self.edit_name = QLineEdit(self)

        self.btn_create = QPushButton('Start', self)

        # Create labels
        lbl_title = QLabel('Choose your Hero')
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setFont(QFont('Helvetica', 17))

        lbl_name = QLabel('Name')
        lbl_job = QLabel('Class')
        lbl_gender = QLabel('Gender')

        lbl_name.setFont(QFont('Helvetica', 10))
        lbl_job.setFont(QFont('Helvetica', 10))
        lbl_gender.setFont(QFont('Helvetica', 10))

        # Add everything together
        hbox_job.addWidget(btn_archer)
        hbox_job.addWidget(btn_paladin)
        hbox_job.addWidget(btn_wizard)
        hbox_job.addStretch()

        hbox_gender.addWidget(btn_male)
        hbox_gender.addWidget(btn_female)
        hbox_gender.addStretch()

        hbox_create.addStretch()
        hbox_create.addWidget(self.btn_create)

        fbox.addRow(lbl_title)
        fbox.addRow(lbl_job, hbox_job)
        fbox.addRow(lbl_gender, hbox_gender)
        fbox.addRow(lbl_name, self.edit_name)
        fbox.addRow(hbox_create)

        layout.addStretch()
        layout.addLayout(fbox)
        layout.addStretch()


        self.setLayout(layout)

    def selectJob(self, job):
        self.job = job

    def selectGender(self, gender):
        self.gender = gender


class Adventure(QWidget):
    def __init__(self, parent=None):
        super(Adventure, self).__init__(parent)
        self.hero = parent.hero
        self.game = parent.game
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        hbox_bar = QHBoxLayout()
        hbox_location = QHBoxLayout()
        tabs_displays = QTabWidget()

        self.bar_health = QProgressBar()
        self.bar_mana = QProgressBar()
        self.bar_xp = QProgressBar()

        self.bar_health.setValue(self.hero.health * 10)
        self.bar_health.setMinimum(0)
        self.bar_health.setMaximum(self.hero.health_max * 10)
        self.bar_health.setToolTip("{0}/{1}".format(self.hero.health, self.hero.health_max))
        self.bar_health.setFormat('Health: %.1f' % self.hero.health)
        self.bar_health.setStyleSheet("::chunk {background-color: red}")

        self.bar_mana.setValue(self.hero.mana * 10)
        self.bar_mana.setMinimum(0)
        self.bar_mana.setMaximum(self.hero.mana_max * 10)
        self.bar_health.setToolTip("{0}/{1}".format(self.hero.mana, self.hero.mana_max))
        self.bar_mana.setFormat('Mana %.1f' % self.hero.mana)
        self.bar_mana.setStyleSheet("::chunk {background-color: blue}")

        self.bar_xp.setValue(self.hero.xp)
        self.bar_xp.setMinimum(0)
        self.bar_xp.setMaximum(self.hero.next_lvl)
        self.bar_xp.setToolTip("{0}/{1}".format(self.hero.xp, self.hero.next_lvl))
        self.bar_xp.setFormat('')
        self.bar_xp.setStyleSheet("::chunk {background-color: yellow}")

        hbox_bar.addWidget(self.bar_health)
        hbox_bar.addWidget(self.bar_mana)

        #self.list_action = QListWidget()
        self.scroll_list = QScrollArea()
        self.story_widget = StoryDisplay()
        self.scroll_list.setWidgetResizable(True)
        self.scroll_list.setFixedHeight(300)
        self.scroll_list.setWidget(self.story_widget)

        font_lbl = QFont('Helvetica', 10)
        font_lbl.setBold(True)

        self.lbl_location_name = QLabel("Location")
        self.lbl_location_name.setFont(font_lbl)
        self.lbl_location = QLabel(self.game.verboseLocation(self.hero.lvl))

        hbox_location.addWidget(self.lbl_location_name)
        hbox_location.addWidget(self.lbl_location)
        hbox_location.addStretch()

        self.skill_display = SkillDisplay(self)
        self.belt_display = BeltDisplay(self)

        skill_scroll = QScrollArea()
        belt_scroll = QScrollArea()
        skill_scroll.setWidgetResizable(True)
        belt_scroll.setWidgetResizable(True)

        skill_scroll.setWidget(self.skill_display)
        belt_scroll.setWidget(self.belt_display)

        tabs_displays.addTab(skill_scroll, "Skills")
        tabs_displays.addTab(belt_scroll, "Belt")

        layout.addLayout(hbox_bar)
        layout.addWidget(self.bar_xp)
        layout.addWidget(self.scroll_list)
        layout.addLayout(hbox_location)
        layout.addWidget(tabs_displays)
        layout.addStretch()

        self.setLayout(layout)

    def addStory(self, message, tooltip=None):
        self.story_widget.addStory(message, tooltip)
        #value = self.scroll_list.verticalScrollBar().value()
        #self.scroll_list.verticalScrollBar().setValue(value + 40)
        #self.list_action.addItem(QListWidgetItem(message))
        #self.list_action.scrollToBottom()
        self.scroll_list.verticalScrollBar().rangeChanged.connect(self.ResizeScroll)

    def ResizeScroll(self, min, maxi):
        self.scroll_list.verticalScrollBar().setValue(maxi)

    def updateBars(self):
        self.bar_health.setMaximum(self.hero.health_max * 10)
        self.bar_mana.setMaximum(self.hero.mana_max * 10)
        self.bar_xp.setMaximum(self.hero.next_lvl)

        self.bar_health.setValue(self.hero.health * 10)
        self.bar_mana.setValue(self.hero.mana * 10)
        self.bar_xp.setValue(self.hero.xp)

        self.bar_health.setToolTip("{0}/{1}".format(self.hero.health, self.hero.health_max))
        self.bar_mana.setToolTip("{0}/{1}".format(self.hero.mana, self.hero.mana_max))
        self.bar_xp.setToolTip("{0}/{1}".format(self.hero.xp, self.hero.next_lvl))

        self.bar_health.setFormat('Health: %.1f' % self.hero.health)
        self.bar_mana.setFormat('Mana  %.1f' % self.hero.mana)
        self.lbl_location.setText(self.game.verboseLocation(self.hero.lvl))

    def updateBelt(self):
        self.belt_display.updateBar()

    def updateSkills(self):
        self.skill_display.updateBar()


class StoryDisplay(QWidget):
    def __init__(self, parent=None):
        super(StoryDisplay, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setStyleSheet("background: white")
        self.setLayout(self.layout)

    def addStory(self, message, tooltip=None):
        lbl = QLabel(message)
        lbl.setMinimumHeight(20)
        lbl.setMaximumHeight(20)
        lbl.setMargin(0)
        lbl.setStyleSheet("background: white;")

        story.info(message)
        if tooltip:
            lbl.setToolTip(tooltip)
            story.info(tooltip)


        self.layout.addWidget(lbl)
        self.layout.setAlignment(Qt.AlignTop)


class HeroStats(QWidget):
    def __init__(self, parent=None):
        super(HeroStats, self).__init__(parent)
        self.hero = parent.hero
        self.initUI()

    def initUI(self):
        fbox = QFormLayout()
        fbox.setHorizontalSpacing(10)

        lbl_name = QLabel(self.hero.name)

        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setFont(QFont('Helvetica', 16))
        
        self.lbl_job = QLabel(self.hero.job)
        self.lbl_lvl = QLabel(str(self.hero.lvl))

        text = "<b>{0}</b> ({1})".format(self.hero.intelligence, self.hero.base_intelligence)
        self.lbl_int = QLabel(text)
        text = "<b>{0}</b> ({1})".format(self.hero.strength, self.hero.base_strength)
        self.lbl_str = QLabel(text)
        text = "<b>{0}</b> ({1})".format(self.hero.dexterity, self.hero.base_dexterity)
        self.lbl_dex = QLabel(text)
        text = "<b>{0}</b> ({1})".format(self.hero.vitality, self.hero.base_vitality)
        self.lbl_vit = QLabel(text)

        self.lbl_block = QLabel('%d %%' % self.hero.block_chance)
        block = self.hero.blocking - self.hero.base_blocking 
        dext = max(self.hero.dexterity - 5, 1)
        tt = 'Base: <b>{}</b><br/>'.format(self.hero.base_blocking)
        tt += 'Gear: <b>{0}</b><br />'.format(block)
        tt += '<br />'
        tt +='<i>({block} x {dext}) / 2 x {lvl}</i>'.format(block=self.hero.blocking,dext=dext,lvl=self.hero.lvl)
        self.lbl_block.setToolTip(tt)

        self.lbl_armor = QLabel("{0:0.1f}".format(self.hero.armor))
        tt = "Max Armor absorbtion: <b>{0:0.1f}</b><br />".format(self.hero.armor * self.hero.armor_eff)
        tt += "<br /><i>Armor absorbs up to 90% damage</i>"
        self.lbl_armor.setToolTip(tt)
        self.lbl_damage = QLabel("{0}-{1}".format(self.hero.damage_min, self.hero.damage_max))
        tt = "<b>Base Damage:</b> {0}-{1}".format(self.hero.base_damage_min, self.hero.base_damage_max)
        self.lbl_damage.setToolTip(tt)
        self.lbl_gold = QLabel(str(self.hero.gold))

        lbl_job_name = QLabel('Class')
        lbl_lvl_name = QLabel('Level')

        lbl_int_name = QLabel('Intelligence')
        lbl_str_name = QLabel('Strength')
        lbl_dex_name = QLabel('Dexterity')
        lbl_vit_name = QLabel('Vitality')

        lbl_block_name = QLabel('Block chance')
        lbl_armor_name = QLabel('Armor')
        lbl_damage_name = QLabel('Damage')

        lbl_gold_name = QLabel('Gold')

        font_lbl = QFont('Helvetica', 10)
        font_lbl.setBold(True)

        lbl_job_name.setFont(font_lbl)
        lbl_lvl_name.setFont(font_lbl)
        lbl_int_name.setFont(font_lbl)
        lbl_str_name.setFont(font_lbl)
        lbl_dex_name.setFont(font_lbl)
        lbl_vit_name.setFont(font_lbl)
        lbl_block_name.setFont(font_lbl)
        lbl_armor_name.setFont(font_lbl)
        lbl_damage_name.setFont(font_lbl)
        lbl_gold_name.setFont(font_lbl)

        fbox.addRow(lbl_name)
        fbox.addRow(lbl_lvl_name, self.lbl_lvl)
        fbox.addRow(lbl_job_name, self.lbl_job)

        fbox.addRow(lbl_int_name, self.lbl_int)
        fbox.addRow(lbl_str_name, self.lbl_str)
        fbox.addRow(lbl_dex_name, self.lbl_dex)
        fbox.addRow(lbl_vit_name, self.lbl_vit)

        fbox.addRow(lbl_block_name, self.lbl_block)
        fbox.addRow(lbl_armor_name, self.lbl_armor)
        fbox.addRow(lbl_damage_name, self.lbl_damage)
        fbox.addRow(lbl_gold_name, self.lbl_gold)

        self.setLayout(fbox)
        self.setMinimumWidth(200)

    def updateStats(self):
        self.lbl_job.setText(self.hero.job)
        self.lbl_lvl.setText(str(self.hero.lvl))

        text = "<b>{0}</b> ({1})".format(self.hero.intelligence, self.hero.base_intelligence)
        self.lbl_int.setText(text)
        text = "<b>{0}</b> ({1})".format(self.hero.strength, self.hero.base_strength)
        self.lbl_str.setText(text)
        text = "<b>{0}</b> ({1})".format(self.hero.dexterity, self.hero.base_dexterity)
        self.lbl_dex.setText(text)
        text = "<b>{0}</b> ({1})".format(self.hero.vitality, self.hero.base_vitality)
        self.lbl_vit.setText(text)

        self.lbl_block.setText('%d %%' % self.hero.block_chance)
        block = self.hero.blocking - self.hero.base_blocking 
        dext = max(self.hero.dexterity - 5, 1)
        tt = 'Base: <b>{}</b><br/>'.format(self.hero.base_blocking)
        tt += 'Gear: <b>{0}</b><br />'.format(block)
        tt += '<br />'
        tt +='<i>({block} x {dext}) / 2 x {lvl}</i>'.format(block=self.hero.blocking,dext=dext,lvl=self.hero.lvl)
        self.lbl_block.setToolTip(tt)
        self.lbl_armor.setText("{0:0.1f}".format(self.hero.armor))
        tt = "Max Armor absobtion: <b>{0:0.1f}</b><br />".format(self.hero.armor * self.hero.armor_eff)
        tt += "<br /><i>Armor absorbs up to 90% damage<i>"
        self.lbl_armor.setToolTip(tt)
        self.lbl_damage.setText("{0}-{1}".format(self.hero.damage_min, self.hero.damage_max))
        tt = "Base Damage: <b>{0}-{1}</b>".format(self.hero.base_damage_min, self.hero.base_damage_max)
        self.lbl_damage.setToolTip(tt)
        self.lbl_gold.setText(str(self.hero.gold))


class EnnemyStats(QWidget):
    def __init__(self, ennemy, parent=None):
        super(EnnemyStats, self).__init__(parent)
        self.ennemy = ennemy
        self.initUI()

    def initUI(self):
        self.fbox = QFormLayout()
        self.fbox.setHorizontalSpacing(10)

        lbl_name = QLabel(self.ennemy['name'])

        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setFont(QFont('Helvetica', 16))

        self.lbl_lvl = QLabel(str(self.ennemy['lvl']))
        self.lbl_type = QLabel(str(self.ennemy['type']))
        self.lbl_strength = QLabel("{0:.1f}".format(self.ennemy['strength'] * 2))
        self.lbl_hitpoints = QLabel("{0:.1f}".format(self.ennemy['hitpoints']))
        string = ""
        for weakness in self.ennemy['weakness']:
            string += "{} ".format(weakness)
        self.lbl_weakness = QLabel(string)

        lbl_lvl_name = QLabel('Level:')
        lbl_type_name = QLabel('Type:')
        lbl_strength_name = QLabel('Strength:')
        lbl_hitpoints_name = QLabel('Hitpoints:')
        lbl_weakness_name = QLabel('Weakness:')

        font_lbl = QFont('Helvetica', 10)
        font_lbl.setBold(True)

        lbl_lvl_name.setFont(font_lbl)
        lbl_type_name.setFont(font_lbl)
        lbl_strength_name.setFont(font_lbl)
        lbl_hitpoints_name.setFont(font_lbl)
        lbl_weakness_name.setFont(font_lbl)

        self.fbox.addRow(lbl_name)
        self.fbox.addRow(lbl_lvl_name, self.lbl_lvl)
        self.fbox.addRow(lbl_type_name, self.lbl_type)
        self.fbox.addRow(lbl_strength_name, self.lbl_strength)
        self.fbox.addRow(lbl_hitpoints_name, self.lbl_hitpoints)
        self.fbox.addRow(lbl_weakness_name, self.lbl_weakness)
        self.setLayout(self.fbox)

    def updateStats(self):
        self.lbl_strength.setText("{0:.1f}".format(self.ennemy['strength'] * 2))
        self.lbl_hitpoints.setText("{0:.1f}".format(self.ennemy['hitpoints']))


class NoEnnemyStats(QWidget):
    def __init__(self, parent=None):
        super(NoEnnemyStats, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.fbox = QFormLayout()
        self.fbox.setHorizontalSpacing(10)

        lbl_name = QLabel('No ennemy around')

        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setFont(QFont('Helvetica', 16))

        self.fbox.addRow(lbl_name)
        self.setLayout(self.fbox)

    def updateStats(self):
        pass
    

class GameStats(QWidget):
    def __init__(self, parent=None):
        super(GameStats, self).__init__(parent)
        self.game = parent.game
        self.initUI()

    def initUI(self):
        fbox = QFormLayout()
        fbox.setHorizontalSpacing(10)

        self.lbl_kills = QLabel(str(self.game.kills))
        self.lbl_damage_dealt = QLabel("{0:.1f}".format(self.game.damage_dealt))
        self.lbl_damage_taken = QLabel("{0:.1f}".format(self.game.damage_taken))
        self.lbl_hpotions = QLabel(str(self.game.hpotion_taken))
        self.lbl_mpotions = QLabel(str(self.game.mpotion_taken))
        self.lbl_spell_cast = QLabel(str(self.game.spell_cast))
        self.lbl_dungeon_cleared = QLabel(str(self.game.dungeon_cleared))
        self.lbl_unique_kill = QLabel(str(self.game.unique_kills))
        self.lbl_xp_earned = QLabel(str(self.game.xp_earned))
        self.lbl_gold_earned = QLabel(str(self.game.gold_earned))
        self.lbl_chest_opened = QLabel(str(self.game.chest_opened))
        self.lbl_item_found = QLabel(str(self.game.item_found))
        self.lbl_town_trips = QLabel(str(self.game.town_trips))

        lbl_kills_name = QLabel('Monsters killed:')
        lbl_damage_dealt_name = QLabel('Damage dealt:')
        lbl_damage_taken_name = QLabel('Damage taken:')
        lbl_hpotions_name = QLabel('Health potion drunk:')
        lbl_mpotions_name = QLabel('Mana potion chugged:')
        lbl_spell_cast_name = QLabel('Spell cast:')
        lbl_dungeon_cleared_name = QLabel('Dungeon cleared:')
        lbl_unique_kill_name = QLabel('Champions defeated:')
        lbl_xp_earned_name = QLabel('XP earned:')
        lbl_gold_earned_name = QLabel('Gold earned:')
        lbl_chest_opened_name = QLabel('Chest opened:')
        lbl_item_found_name = QLabel('Item found:')
        lbl_item_town_trips = QLabel('Trips to the town:')

        font_lbl = QFont('Helvetica', 10)
        font_lbl.setBold(True)

        lbl_kills_name.setFont(font_lbl)
        lbl_damage_dealt_name.setFont(font_lbl)
        lbl_damage_taken_name.setFont(font_lbl)
        lbl_hpotions_name.setFont(font_lbl)
        lbl_mpotions_name.setFont(font_lbl)
        lbl_spell_cast_name.setFont(font_lbl)
        lbl_dungeon_cleared_name.setFont(font_lbl)
        lbl_unique_kill_name.setFont(font_lbl)
        lbl_xp_earned_name.setFont(font_lbl)
        lbl_gold_earned_name.setFont(font_lbl)
        lbl_chest_opened_name.setFont(font_lbl)
        lbl_item_found_name.setFont(font_lbl)
        lbl_item_town_trips.setFont(font_lbl)

        fbox.addRow(lbl_kills_name, self.lbl_kills)
        fbox.addRow(lbl_damage_dealt_name, self.lbl_damage_dealt)
        fbox.addRow(lbl_damage_taken_name, self.lbl_damage_taken)
        fbox.addRow(lbl_hpotions_name, self.lbl_hpotions)
        fbox.addRow(lbl_mpotions_name, self.lbl_mpotions)
        fbox.addRow(lbl_spell_cast_name, self.lbl_spell_cast)
        fbox.addRow(lbl_dungeon_cleared_name, self.lbl_dungeon_cleared)
        fbox.addRow(lbl_unique_kill_name, self.lbl_unique_kill)
        fbox.addRow(lbl_xp_earned_name, self.lbl_xp_earned)
        fbox.addRow(lbl_gold_earned_name, self.lbl_gold_earned)
        fbox.addRow(lbl_chest_opened_name, self.lbl_chest_opened)
        fbox.addRow(lbl_item_found_name, self.lbl_item_found)
        fbox.addRow(lbl_item_town_trips, self.lbl_town_trips)

        self.setLayout(fbox)

    def updateStats(self):
        self.lbl_kills.setText(str(self.game.kills))
        self.lbl_damage_dealt.setText("{0:.1f}".format(self.game.damage_dealt))
        self.lbl_damage_taken.setText("{0:.1f}".format(self.game.damage_taken))
        self.lbl_hpotions.setText(str(self.game.hpotion_taken))
        self.lbl_mpotions.setText(str(self.game.mpotion_taken))
        self.lbl_spell_cast.setText(str(self.game.spell_cast))
        self.lbl_dungeon_cleared.setText(str(self.game.dungeon_cleared))
        self.lbl_unique_kill.setText(str(self.game.unique_kills))
        self.lbl_xp_earned.setText(str(self.game.xp_earned))
        self.lbl_gold_earned.setText(str(self.game.gold_earned))
        self.lbl_chest_opened.setText(str(self.game.chest_opened))
        self.lbl_item_found.setText(str(self.game.item_found))
        self.lbl_town_trips.setText(str(self.game.town_trips))


class GearStats(QWidget):
    def __init__(self, parent=None):
        super(GearStats, self).__init__(parent)
        self.hero = parent.hero
        self.initUI()

    def initUI(self):
        fbox = QFormLayout()
        fbox.setHorizontalSpacing(10)

        font_lbl = QFont('Helvetica', 10)
        font_lbl.setBold(True)

        lbl_weapon_name = QLabel('Weapon:')
        lbl_weapon_name.setFont(font_lbl)
        weapon = 'None'
        tt = "No weapon equiped"
        if self.hero.gear['weapon']:
            weapon = self.hero.gear['weapon'].fullname()
            tt = self.createTT(self.hero.gear['weapon'])
        self.lbl_weapon = QLabel(weapon)
        self.lbl_weapon.setToolTip(tt)
        fbox.addRow(lbl_weapon_name, self.lbl_weapon)

        if self.hero.job == "Paladin":
            lbl_shield_name = QLabel('Shield:')
            shield = 'None'
            tt = "No shield equiped"
            if self.hero.gear['armor']['shield']:
                shield = self.hero.gear['armor']['shield'].fullname()
                tt = self.createTT(self.hero.gear['armor']['shield'])
            self.lbl_shield = QLabel(shield)
            self.lbl_shield.setToolTip(tt)
            lbl_shield_name.setFont(font_lbl)
            fbox.addRow(lbl_shield_name, self.lbl_shield)

        lbl_pants_name = QLabel('Pants:')
        pants = 'None'
        tt = "No pants equiped"
        if self.hero.gear['armor']['pants']:
            pants = self.hero.gear['armor']['pants'].fullname()
            tt = self.createTT(self.hero.gear['armor']['pants'])
        self.lbl_pants = QLabel(pants)
        self.lbl_pants.setToolTip(tt)
        lbl_pants_name.setFont(font_lbl)
        fbox.addRow(lbl_pants_name, self.lbl_pants)

        lbl_chest_name = QLabel('Chest:')
        chest = 'None'
        tt = "No chestpiece equiped"
        if self.hero.gear['armor']['chest']:
            chest = self.hero.gear['armor']['chest'].fullname()
            tt = self.createTT(self.hero.gear['armor']['chest'])
        self.lbl_chest = QLabel(chest)
        self.lbl_chest.setToolTip(tt)
        lbl_chest_name.setFont(font_lbl)
        fbox.addRow(lbl_chest_name, self.lbl_chest)

        lbl_gloves_name = QLabel('Gloves:')
        gloves = 'None'
        tt = "No gloves equiped"
        if self.hero.gear['armor']['gloves']:
            gloves = self.hero.gear['armor']['gloves'].fullname()
            tt = self.createTT(self.hero.gear['armor']['gloves'])
        self.lbl_gloves = QLabel(gloves)
        self.lbl_gloves.setToolTip(tt)
        lbl_gloves_name.setFont(font_lbl)
        fbox.addRow(lbl_gloves_name, self.lbl_gloves)

        lbl_boots_name = QLabel('Boots:')
        boots = 'None'
        tt = "No boots equiped"
        if self.hero.gear['armor']['boots']:
            boots = self.hero.gear['armor']['boots'].fullname()
            tt = self.createTT(self.hero.gear['armor']['boots'])
        self.lbl_boots = QLabel(boots)
        self.lbl_boots.setToolTip(tt)
        lbl_boots_name.setFont(font_lbl)
        fbox.addRow(lbl_boots_name, self.lbl_boots)

        lbl_helm_name = QLabel('Helm:')
        helm = 'None'
        tt = "No helmet equiped"
        if self.hero.gear['armor']['helm']:
            helm = self.hero.gear['armor']['helm'].fullname()
            tt = self.createTT(self.hero.gear['armor']['helm'])
        self.lbl_helm = QLabel(helm)
        self.lbl_helm.setToolTip(tt)
        lbl_helm_name.setFont(font_lbl)
        fbox.addRow(lbl_helm_name, self.lbl_helm)

        lbl_belt_name = QLabel('Belt:')
        belt = 'None'
        tt = "No belt equiped"
        if self.hero.gear['armor']['belt']:
            belt = self.hero.gear['armor']['belt'].fullname()
            tt = self.createTT(self.hero.gear['armor']['belt'])
        self.lbl_belt = QLabel(belt)
        self.lbl_belt.setToolTip(tt)
        lbl_belt_name.setFont(font_lbl)
        fbox.addRow(lbl_belt_name, self.lbl_belt)

        lbl_shoulders_name = QLabel('Shoulders:')
        shoulders = 'None'
        tt = "No shoulders equiped"
        if self.hero.gear['armor']['shoulders']:
            shoulders = self.hero.gear['armor']['shoulders'].fullname()
            tt = self.createTT(self.hero.gear['armor']['shoulders'])
        self.lbl_shoulders = QLabel(shoulders)
        self.lbl_shoulders.setToolTip(tt)
        lbl_shoulders_name.setFont(font_lbl)
        fbox.addRow(lbl_shoulders_name, self.lbl_shoulders)

        lbl_bracers_name = QLabel('Bracers:')
        bracers = 'None'
        tt = "No bracers equiped"
        if self.hero.gear['armor']['bracers']:
            bracers = self.hero.gear['armor']['bracers'].fullname()
            tt = self.createTT(self.hero.gear['armor']['bracers'])
        self.lbl_bracers = QLabel(bracers)
        self.lbl_bracers.setToolTip(tt)
        lbl_bracers_name.setFont(font_lbl)
        fbox.addRow(lbl_bracers_name, self.lbl_bracers)

        lbl_amulet_name = QLabel('Amulet:')
        amulet = 'None'
        tt = "No amulet equiped"
        if self.hero.gear['jewel']['amulet']:
            amulet = self.hero.gear['jewel']['amulet'].fullname()
            tt = self.createTT(self.hero.gear['jewel']['amulet'])
        self.lbl_amulet = QLabel(amulet)
        self.lbl_amulet.setToolTip(tt)
        lbl_amulet_name.setFont(font_lbl)
        fbox.addRow(lbl_amulet_name, self.lbl_amulet)

        lbl_ring_name = QLabel('Ring:')
        ring = 'None'
        tt = "No ring equiped"
        if self.hero.gear['jewel']['ring']:
            ring = self.hero.gear['jewel']['ring'].fullname()
            tt = self.createTT(self.hero.gear['jewel']['ring'])
        self.lbl_ring = QLabel(ring)
        self.lbl_ring.setToolTip(tt)
        lbl_ring_name.setFont(font_lbl)
        fbox.addRow(lbl_ring_name, self.lbl_ring)

        self.setLayout(fbox)
        self.setMinimumWidth(200)

    def createTT(self, gear):  

        color = 'blue' if gear.enchanted else 'black'

        tt = "<h2 align='center' style='color:{color}'>{name}</h2>".format(color=color, name=gear.fullname())

        if gear.type == "weapon":
            tt += "<h1 align='center'>{min}-{max}</h1>".format(min=gear.damage_min, max=gear.damage_max)
            if gear.subtype in ['bow', 'crossbow']:
                tt += "<h3 align='center'>{block}</h3>".format(block=gear.evasion)
        elif gear.type == 'armor':
            tt += "<h1 align='center'>{armor:0.1f}</h1>".format(armor=gear.armor)
            if gear.subtype == 'shield':
                tt += "<h3 align='center'>{block}</h3>".format(block=gear.block)
        elif gear.type == 'jewel':
            tt += ""

        if gear.enchanted:
                if 'debuff' in gear.enchant:
                    if gear.enchant['debuff'] == "Fire":
                        color = 'red'
                    elif gear.enchant['debuff'] == "Ice":
                        color = 'blue'
                    elif gear.enchant['debuff'] == "Electric":
                        color = 'yellow'
                    elif gear.enchant['debuff'] == "Poison":
                        color = 'green'
                    elif gear.enchant['debuff'] == "Arcane":
                        color = 'purple'
                    elif gear.enchant['debuff'] == "Sacred":
                        color = 'black'


                    debuff = verboseEnchants(gear.enchant['debuff'])
                    tt += "<h3 align='center' style='color:{color}'>{debuff}</h3>".format(debuff=debuff, color=color)
                for key, value in gear.enchant.items():
                    if key == 'debuff':
                        continue
                    tt += "<b>{0}</b>: <span style='color:green'>{1}</span><br \>".format(verboseEnchants(key), value) 

        tt += "<p>{desc}</p>".format(desc=gear.desc)

        tt += "<h5>level {lvl} {sub}</h5>".format(lvl=gear.lvl, sub=gear.verboseSubtype())

        return tt

    def updateStats(self):
        weapon = 'None'
        tt = "No weapon equiped"
        if self.hero.gear['weapon']:
            weapon = self.hero.gear['weapon'].fullname()
            tt = self.createTT(self.hero.gear['weapon'])
        self.lbl_weapon.setToolTip(tt)
        self.lbl_weapon.setText(weapon)

        if self.hero.job == "Paladin":
            shield = 'None'
            tt = "No shield equiped"
            if self.hero.gear['armor']['shield']:
                shield = self.hero.gear['armor']['shield'].fullname()
                tt = self.createTT(self.hero.gear['armor']['shield'])
            self.lbl_shield.setToolTip(tt)
            self.lbl_shield.setText(shield)

        pants = 'None'
        tt = "No pants equiped"
        if self.hero.gear['armor']['pants']:
            pants = self.hero.gear['armor']['pants'].fullname()
            tt = self.createTT(self.hero.gear['armor']['pants'])
        self.lbl_pants.setToolTip(tt)
        self.lbl_pants.setText(pants)
        
        chest = 'None'
        tt = "No chestpiece equiped"
        if self.hero.gear['armor']['chest']:
            chest = self.hero.gear['armor']['chest'].fullname()
            tt = self.createTT(self.hero.gear['armor']['chest'])
        self.lbl_chest.setToolTip(tt)
        self.lbl_chest.setText(chest)
            
        gloves = 'None'
        tt = "No gloves equiped"
        if self.hero.gear['armor']['gloves']:
            gloves = self.hero.gear['armor']['gloves'].fullname()
            tt = self.createTT(self.hero.gear['armor']['gloves'])
        self.lbl_gloves.setToolTip(tt)
        self.lbl_gloves.setText(gloves)
            
        boots = 'None'
        tt = "No boots equiped"
        if self.hero.gear['armor']['boots']:
            boots = self.hero.gear['armor']['boots'].fullname()
            tt = self.createTT(self.hero.gear['armor']['boots'])
        self.lbl_boots.setToolTip(tt)
        self.lbl_boots.setText(boots)
            
        helm = 'None'
        tt = "No helmet equiped"
        if self.hero.gear['armor']['helm']:
            helm = self.hero.gear['armor']['helm'].fullname()
            tt = self.createTT(self.hero.gear['armor']['helm'])
        self.lbl_helm.setToolTip(tt)
        self.lbl_helm.setText(helm)
            
        belt = 'None'
        tt = "No belt equiped"
        if self.hero.gear['armor']['belt']:
            belt = self.hero.gear['armor']['belt'].fullname()
            tt = self.createTT(self.hero.gear['armor']['belt'])
        self.lbl_belt.setToolTip(tt)
        self.lbl_belt.setText(belt)
            
        shoulders = 'None'
        tt = "No shoulders equiped"
        if self.hero.gear['armor']['shoulders']:
            shoulders = self.hero.gear['armor']['shoulders'].fullname()
            tt = self.createTT(self.hero.gear['armor']['shoulders'])
        self.lbl_shoulders.setToolTip(tt)
        self.lbl_shoulders.setText(shoulders)
            
        bracers = 'None'
        tt = "No bracers equiped"
        if self.hero.gear['armor']['bracers']:
            bracers = self.hero.gear['armor']['bracers'].fullname()
            tt = self.createTT(self.hero.gear['armor']['bracers'])
        self.lbl_bracers.setToolTip(tt)
        self.lbl_bracers.setText(bracers)
            
        amulet = 'None'
        tt = "No amulet equiped"
        if self.hero.gear['jewel']['amulet']:
            amulet = self.hero.gear['jewel']['amulet'].fullname()
            tt = self.createTT(self.hero.gear['jewel']['amulet'])
        self.lbl_amulet.setToolTip(tt)
        self.lbl_amulet.setText(amulet)
            
        ring = 'None'
        tt = "No ring equiped"
        if self.hero.gear['jewel']['ring']:
            ring = self.hero.gear['jewel']['ring'].fullname()
            tt = self.createTT(self.hero.gear['jewel']['ring'])
        self.lbl_ring.setToolTip(tt)
        self.lbl_ring.setText(ring)


class BeltDisplay(QWidget):
    def __init__(self, parent=None):
        super(BeltDisplay, self).__init__(parent)
        self.hero = parent.hero
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        #self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.populate()
        self.setLayout(self.layout)

    def populate(self):
        i = 0
        for potion in list(self.hero.hpotion_belt):
            self.layout.addWidget(PotionItem(potion, self.hero.healing_modifier), 1, i)            
            self.layout.setAlignment(Qt.AlignLeft)
            i += 1

        # Fill the rest of the empty spots with blank
        while i < self.hero.belt_size:
            self.layout.addWidget(PotionItem('empty', self.hero.healing_modifier), 1, i)            
            self.layout.setAlignment(Qt.AlignLeft)
            i += 1

        i = 0
        for potion in list(self.hero.mpotion_belt):
            self.layout.addWidget(PotionItem(potion, self.hero.mana_modifier), 0, i)
            self.layout.setAlignment(Qt.AlignLeft)
            i += 1

        # Fill the rest of the empty spots with blank
        while i < self.hero.belt_size:
            self.layout.addWidget(PotionItem('empty', self.hero.mana_modifier), 0, i)
            self.layout.setAlignment(Qt.AlignLeft)
            i += 1

    def updateBar(self):
        # remove everything first
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        self.layout.setSpacing(0)
        self.populate()


class PotionItem(QFrame):
    def __init__(self, type, modifier, parent=None):
        super(PotionItem, self).__init__(parent)
        self.type = type
        self.modifier = modifier
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        
        if "Mana" in self.type:
            lbl_potion = QLabel(self.type)
            amount = mpotion_type[self.type] * self.modifier
            tt = "<h2>{type}</h2> restores <b>{amount}</b> Mana"
            self.setToolTip(tt.format(type=self.type, amount=amount))
            image_path = '{0}/assets/mana.png'.format(PATH)
        elif "Health" in self.type:
            lbl_potion = QLabel(self.type)
            amount = hpotion_type[self.type] * self.modifier
            tt = "<h2>{type}</h2> restores <b>{amount}</b> Life"
            self.setToolTip(tt.format(type=self.type, amount=amount))
            image_path = '{0}/assets/health.png'.format(PATH)
        else:
            lbl_potion = QLabel("Empty")
            image_path = '{0}/assets/empty.png'.format(PATH)

        potion_img = QPixmap(image_path)
        lbl_potion.setPixmap(potion_img)

        layout.addWidget(lbl_potion)

        self.setLayout(layout)
        self.setMinimumWidth(54)
        self.setMaximumWidth(54)
        self.setMinimumHeight(54)
        self.setMaximumHeight(54)
        self.setStyleSheet("border: 1px solid black; background: white;")
        lbl_potion.setStyleSheet("border: 0px")


class SkillDisplay(QWidget):
    def __init__(self, parent=None):
        super(SkillDisplay, self).__init__(parent)
        self.hero = parent.hero
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10,0,0,0)
        self.layout.setSpacing(0)
        self.populate()
        self.setLayout(self.layout)
        #self.setStyleSheet("border: 1px solid black; background: yellow;")

    def populate(self):
        i = 0
        for key, value in self.hero.offensive_skills.items():
            self.layout.addWidget(SkillItem(key, self.hero), 0, i)
            self.layout.setAlignment(Qt.AlignLeft)
            log.info("Interface :: Create skill icon :: {}".format(key))
            i += 1


    def updateBar(self):
        # remove everything first
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
        self.populate()


class SkillItem(QFrame):
    def __init__(self, skill, hero, parent=None):
        super(SkillItem, self).__init__(parent)
        self.skill = skill
        self.hero = hero
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        min = self.hero.calcSkillMinDamage(self.skill)
        max = self.hero.calcSkillMaxDamage(self.skill)
        cost = self.hero.offensive_skills[self.skill]['cost']
        name = self.hero.offensive_skills[self.skill]['name']
        lvl = self.hero.offensive_skills[self.skill]['lvl']
        desc = oskill_list[self.skill]['desc']
        type = oskill_list[self.skill]['type']
        att = self.hero.main
        value = self.hero.offensive_skills[self.skill]['next_att']

        lbl_skill = QLabel(name)
        tt = "<h1 align='center'>{name}</h1>".format(name=name)
        tt += "<h2 align='center'>{min:.1f}-{max:.1f}</h2>".format(min=min, max=max)
        tt += "<h3>level: {lvl}</h3>".format(lvl=lvl)
        tt += "<p>{desc}</p>".format(desc=desc)
        tt += "Type: <b>{type}</b><br />".format(type=type)
        tt += "Next level require: <b>{value}</b> {att}<br />".format(value=value, att=att)
        tt += "Cost: <b>{cost}</b> Mana".format(desc=desc, cost=cost)

        if oskill_list[self.skill]['requirement']:
            if self.hero.skillReqMet(self.skill):
                color = 'black'
            else:
                color = 'red'

            req = oskill_list[self.skill]['requirement'].split()
            tt += "<h4 style='color:{color}>Requires: {req}</h4>".format(color=color, req=verboseSubtype(req[1]))


        self.setToolTip(tt)

        image_path = '{0}/assets/{1}.png'.format(PATH, self.skill)
        potion_img = QPixmap(image_path)
        lbl_skill.setPixmap(potion_img)
        layout.addWidget(lbl_skill)

        self.setLayout(layout)
        self.setMinimumWidth(86)#150)
        self.setMaximumWidth(86)#150)
        self.setMinimumHeight(86)#154)
        self.setMaximumHeight(86)#154)
        self.setStyleSheet("border: 1px solid black; background: white;")
        lbl_skill.setStyleSheet("border:0px")
