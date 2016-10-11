#!/usr/bin/python3
# -*- coding: utf8 -*

import logging
#from logging.handlers import RotatingFileHandler

# Fix for file paths errors
import os, sys

if getattr(sys, 'frozen', False):
    # frozen
    PATH = os.path.dirname(sys.executable)
else:
    # unfrozen
    PATH = os.path.dirname(os.path.realpath(__file__))


story = logging.getLogger('story')
log = logging.getLogger('logs')

story.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
html_formatter = logging.Formatter('%(asctime)s :: %(message)s <br />')

story_file = logging.FileHandler('{path}/logs/story.html'.format(path=PATH))
log_file = logging.FileHandler('{path}/logs/debug.log'.format(path=PATH))
log_console = logging.StreamHandler()

log_file.setFormatter(formatter)
story_file.setFormatter(html_formatter)

story_file.setLevel(logging.DEBUG)
log_file.setLevel(logging.DEBUG)
log_console.setLevel(logging.WARNING)

story.addHandler(story_file)
log.addHandler(log_file)
log.addHandler(log_console)

# debug log format
# DEBUG :: Method :: action :: result