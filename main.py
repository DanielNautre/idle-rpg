#!/usr/bin/python3
# -*- coding: utf8 -*

# Fix for file paths errors
import os, sys

if getattr(sys, 'frozen', False):
    # frozen
    PATH = os.path.dirname(sys.executable)
else:
    # unfrozen
    PATH = os.path.dirname(os.path.realpath(__file__))

# Import other files from the project
from game import Game
from idlerpg import IdleRPG
from logger import log, story

# Import Graphic Lib
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def main():
    # instatiate the game object
    game = Game()

    # initiate window
    app = QApplication(sys.argv)
    app.setStyleSheet("")
    idlerpg = IdleRPG(game)

    # setup timer for the game tick (1 tick per 2 seconds)
    timer = QTimer()
    timer.start(1500)
    timer.timeout.connect(idlerpg.tick)

    idlerpg.show() 

    # run the main loop
    sys.exit(app.exec_())

if __name__ == '__main__':

    log.info("========== STARTING NEW SESSION ============")
    try:
        ma in()
    exceptException as error:
        log.exception(error)

#EOF