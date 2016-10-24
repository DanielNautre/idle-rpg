import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

includefiles = ['README.md', ('assets', 'assets'), ('saves', 'saves'), ('data','data'), ('logs','logs')]

includes = ['Item', 'Data', 'Config', 'Dice', 'Widgets', 'Hero', 'Game', 'Logger', 'atexit']

options = {
    'build_exe': {
        'includes': includes,
        #'build_exe': 'bin',
        #'include_files': includefiles
    }
}


executables = [Executable(
      script = 'src/main.py', 
      base=base,
      targetName = "IdleRPG.exe",
      #targetDir= ""
      )
]

setup(
      name='Idle RPG',
      version='0.1',
      description='Idle RPG',
      author='Daniel Nautré', 
      options=options,
      executables=executables
      )
