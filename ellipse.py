# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 19:35:10 2018

@author: Bohao
"""
import numpy as np

def calculateEllipse(stringLength, x_1, y_1, x_2, y_2):
    distance = np.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)
    ellipseCentre_x1 = 0.25 * x_1 +0.75 * x_2
    ellipseCentre_x2 = 0.75 * x_1 +0.25 * x_2
    ellipseCentre_y1 = 0.25 * y_1 +0.75 * y_2
    ellipseCentre_y2 = 0.75 * y_1 +0.25 * y_2
    
    axisLength_1  = distance * 0.25
    axisLength_2 = ((np.sqrt(distance) + np.sqrt(24 * stringLength / np.pi - distance * 8)) / 6) ** 2
    
    return axisLength_1, axisLength_2, ellipseCentre_x1, ellipseCentre_x2, ellipseCentre_y1, ellipseCentre_y2
    