#!/usr/bin/env python2

import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
from dwchargen import dungeon_galaxy

try:
    while True:
        dungeon_galaxy.Char.new_random().print_lines()
        if '--auto' in sys.argv[1:]:
            print '---'
            time.sleep(10)
        else:
            raw_input()
except KeyboardInterrupt:
    pass
