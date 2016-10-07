#!/usr/bin/python3
# -*- coding: utf8 -*

import sys, pickle
from random import choice

# Import other files from the project
from dice import d6, d20, d100
from hero import Hero
from item import Item
from game import Game

# Import logger
from logger import log, story

from widgets import HeroSelection, Adventure, HeroStats, EnnemyStats, NoEnnemyStats, GameStats, GearStats, BeltDisplay, SkillDisplay, PATH

# Import Graphic Lib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolTip, QPushButton, 
    QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
    QFormLayout, QDockWidget, QListWidget, QListWidgetItem, QAction, qApp, 
    QButtonGroup, QProgressBar, QSpacerItem, QStatusBar, QFileDialog, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QDir
from PyQt5.QtGui import QFont, QIcon

# Import config & data
from data import s


class IdleRPG(QMainWindow):
    def __init__(self, game):
        super(IdleRPG, self).__init__()
        self.initUI()
        self.game = game
        self.ticks = 0

    def initUI(self):
        self.setGeometry(50,50,1024,620)
        self.setWindowTitle('Idle RPG')

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Create actions
        
        icon_exit = QIcon('{}/assets/exit.png'.format(PATH))
        icon_load = QIcon('{}/assets/load.png'.format(PATH))
        icon_save = QIcon('{}/assets/save.png'.format(PATH))
        icon_new = QIcon('{}/assets/new.png'.format(PATH))
        icon_reset = QIcon('{}/assets/reset.png'.format(PATH))
        icon_about = QIcon('{}/assets/about.png'.format(PATH))

        action_exit = QAction(icon_exit, '&Exit', self)
        action_exit.setShortcut('Ctrl+Q')
        action_exit.setStatusTip('Leave the Game')
        action_exit.triggered.connect(qApp.quit)

        action_load = QAction(icon_load, '&Load', self)
        action_load.setShortcut('Ctrl+L')
        action_load.setStatusTip('Load a save')
        action_load.triggered.connect(self.loadGame)

        action_save = QAction(icon_save, '&Save', self)
        action_save.setShortcut('Ctrl+S')
        action_save.setStatusTip('Save the Game')
        action_save.triggered.connect(self.saveGame) 

        action_new = QAction(icon_new, '&Create Hero', self)
        action_new.setShortcut('Ctrl+N')
        action_new.setStatusTip('Create a new Hero (don\'t forget to save before)')
        action_new.triggered.connect(self.newGame) 

        action_about = QAction(icon_about, '&About', self)
        action_about.setShortcut('Ctrl+?')
        action_about.setStatusTip('About the Idle RPG')
        action_about.triggered.connect(self.aboutGame) 

        action_reset = QAction(icon_reset, '&Reset Docks', self)
        action_reset.setShortcut('Ctrl+R')
        action_reset.setStatusTip('Reset Docks to their initial position')
        action_reset.triggered.connect(self.resetDocks) 

        # Create the Status Bar
        menubar = self.menuBar()
        menu_file = menubar.addMenu('&File')
        menu_file.addAction(action_save)
        menu_file.addAction(action_load)
        menu_file.addAction(action_new)
        menu_file.addSeparator()
        menu_file.addAction(action_about)
        menu_file.addSeparator()
        menu_file.addAction(action_exit)
        menu_view = menubar.addMenu('&View')
        menu_view.addAction(action_reset)
        #menu_about = menubar.addMenu('&About')

        self.stack = QStackedWidget(self)
        
        self.hero_selection = HeroSelection(self)
        self.stack.addWidget(self.hero_selection)
        self.setCentralWidget(self.stack)

        self.hero_selection.btn_create.pressed.connect(lambda:self.startGame(self.hero_selection))

    def loadGame(self):
        log.debug("Interface :: Opening load save dialog")
        filename = QFileDialog.getOpenFileName(self, 'Load save', 
                '{}/saves/'.format(PATH), 'Save files (*.sav)')
        if not filename:
            log.debug('Interface :: loading cancelled')
            return False

        log.info("Save :: Loading {}".format(filename))
        file = open(filename[0], 'rb')
        data = pickle.load(file)
        log.debug("Save :: Loading profile ::\n{}".format(data))

        self.hero = Hero()
        self.hero.load(data['hero'])
        self.game.load(data['game'])
        self.game.started = True
        self.game.hero = self.hero

        # recalculate hero's stats
        self.hero.recalculate()

        self.createGameInterface()

    def saveGame(self):

        if not self.game.started:
            log.info("Interface :: tried to save a game that wasn't started")
            return False

        game_data = self.game.save()
        hero_data = self.hero.save()

        data = {}

        data['game'] = game_data
        data['hero'] = hero_data

        fileObject = open('{0}/saves/{1}.sav'.format(PATH, self.hero.name),'wb')
        success = pickle.dump(data, fileObject, pickle.HIGHEST_PROTOCOL)
        fileObject.close()
        return success

    def startGame(self, hero_val):
        hero_val.name = hero_val.edit_name.text()

        if not hero_val.name or not hero_val.job or not hero_val.gender:
            return

        # Create the hero and start the game
        log.info("Start :: Creating new Hero")
        log.debug("Start :: Name: {0}, Gender: {1}, Class: {2}".format(hero_val.name, hero_val.gender, hero_val.job))
        self.hero = Hero(hero_val.job, hero_val.gender, hero_val.name)
        self.game.started = True
        self.game.hero = self.hero

        self.createGameInterface()

    def newGame(self):

        # Remove everything
        self.game = Game()
        self.docks['stats'].hide()
        self.docks['gear'].hide()
        self.docks['ennemy'].hide()
        self.docks['game_stats'].hide()

        self.stack = QStackedWidget(self)

        self.hero_selection = HeroSelection(self)
        self.stack.addWidget(self.hero_selection)
        self.setCentralWidget(self.stack)

        self.hero_selection.btn_create.pressed.connect(lambda:self.startGame(self.hero_selection))

    def aboutGame(self):
        QMessageBox.about(self, s['about_title'], s['about_dialog'])

    def createGameInterface(self):
        # switch the interface to the adventure one
        self.adventure = Adventure(self)
        self.stack.addWidget(self.adventure)
        self.stack.setCurrentIndex(1)

        # Create Docks
        self.docks = {}
        self.docks['stats'] = QDockWidget("Hero's Stats", self) 
        self.docks['gear'] = QDockWidget("Equipped Gear", self)
        self.docks['ennemy'] = QDockWidget("Ennemy's Stats", self)
        self.docks['game_stats'] = QDockWidget("Game Stats", self)

        self.widget_hero_stats = HeroStats(self)
        self.widget_game_stats = GameStats(self)
        self.widget_gear_stats = GearStats(self)

        self.docks['stats'].setWidget(self.widget_hero_stats)
        self.docks['gear'].setWidget(self.widget_gear_stats)
        self.docks['ennemy'].setWidget(NoEnnemyStats())
        self.docks['game_stats'].setWidget(self.widget_game_stats)

        self.docks['gear'].setFloating(False)
        self.docks['stats'].setFloating(False)
        self.docks['ennemy'].setFloating(False)
        self.docks['game_stats'].setFloating(False)
   

        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks['stats'])
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks['gear'])
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks['ennemy'])
        self.tabifyDockWidget(self.docks['gear'], self.docks['game_stats'])

    def resetDocks(self):
        if not self.game.started:
            log.info("Interface :: tried to reset docks before a game was started")
            return False

        # show
        self.docks['gear'].show()
        self.docks['stats'].show()
        self.docks['ennemy'].show()
        self.docks['game_stats'].show()

        # dock
        self.docks['gear'].setFloating(False)
        self.docks['stats'].setFloating(False)
        self.docks['ennemy'].setFloating(False)
        self.docks['game_stats'].setFloating(False)
   
        # place
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks['stats'])
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks['gear'])
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks['ennemy'])
        self.tabifyDockWidget(self.docks['gear'], self.docks['game_stats'])
        self.docks['gear'].raise_()

    def tick(self):
        if not self.game.started:
            return False

        if self.game.inCombat():
            self.game.handleCombat(self.adventure, self.docks)
        else:
            self.game.handleMoving(self.adventure, self.docks)

        if self.hero.health == 0:
            self.game.started = False
            message = s['hero_killed'].format(hero=self.hero.name)
            self.adventure.addStory(message)
            log.info("Game :: Hero Deceased")
            return

        if self.hero.xp >= self.hero.next_lvl:
            message = self.hero.lvlUp()
            message = message.format(hero=self.hero.name, he=self.hero.pronoun('he'))
            self.adventure.addStory(message)
            self.adventure.updateSkills()

        # before trying to heal check if we go back to town
        
        if (self.hero.needsHPotion() or self.hero.needsMPotion()) and not self.game.inCombat():
            self.game.returnToTown()


        if self.hero.healthLow() and not self.game.location == 'town':
            log.info("Game :: Healing required")
            success = self.hero.heal('potion')
            if not success:
                if self.game.inCombat():
                    message = s['hurt'].format(hero=self.hero.name)
                    self.adventure.addStory(message)
                else:
                    self.game.returnToTown()
            else:
                message = s['health_potion'].format(hero=self.hero.name, restore=success)
                self.adventure.addStory(message)
                self.adventure.updateBelt()
                # update stats
                self.game.hpotion_taken += 1
                log.info("Game :: Consumed 1 Health potion")

        if self.hero.manaLow() and not self.game.location == 'town':
            success = self.hero.mana_restore('potion')
            
            if not success:
                if self.game.inCombat():
                    pass
                elif self.hero.job == 'Wizard':
                    # Only a Wizard runs back to town to buy Mana
                    self.game.returnToTown()
            else:
                message = s['mana_potion'].format(hero=self.hero.name, restore=success)
                self.adventure.addStory(message)
                self.adventure.updateBelt()
                # update stats
                self.game.mpotion_taken += 1
                log.info("Game :: Consumed 1 Mana potion")

        # recalculate hero stats needed only in those cases
        # - lvl up
        # - new gear

        self.hero.regen()

        self.hero.addGearAttBonus()
        self.hero.deriveSecondaryStats()

        #update the bars each tick
        self.adventure.updateBars()
        self.widget_hero_stats.updateStats()
        self.widget_game_stats.updateStats()
        self.widget_gear_stats.updateStats()
        if self.game.inCombat():
            ennemy_widget = self.docks['ennemy'].widget()
            ennemy_widget.updateStats()

        self.statusBar.showMessage("Time passed: {0}s".format(self.ticks * 2))
        self.ticks += 1

        if self.ticks % 40 == 0:
            if self.saveGame():
                self.statusBar.showMessage("Game Saved")


        #log.debug("Ennemy:\n{}".format(self.game.ennemy))
        #log.debug("Dungeon:\n{}".format(self.game.dungeon))
        #log.debug("Hero:\n{}".format(self.hero))
        log.info("==== End of tick {} ====".format(self.ticks))
