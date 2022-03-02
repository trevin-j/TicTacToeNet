'''
Cross platform clear screen
https://stackoverflow.com/questions/2084508/clear-terminal-in-python
'''

import os

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')