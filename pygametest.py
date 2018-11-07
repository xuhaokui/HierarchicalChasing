#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 21:34:28 2018

@author: xuhaokui
"""

import pygame
import time
import sys

pygame.init()
screen = pygame.display.set_mode([400, 300])

t=30

for i in range(t):
    screen = pygame.display.set_mode([400, 300])
    pygame.draw.circle(screen,[255,0,0],[100,i*10],3)
    pygame.display.flip()
    pygame.time.wait(200)

pygame.quit()
#sys.exit()