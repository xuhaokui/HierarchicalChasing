# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 16:40:58 2018

@author: xuhaokui
"""

import pygame, sys, scipy.stats, xlwt
import numpy as np
import networkx as nx
import itertools as it
from math import *

import pickle


"=====Prepared Function====="
def Distance(position1,position2):
    sumsquar=np.power([np.array(position1)-np.array(position2)],2)
    distance=np.double(np.sqrt(sumsquar.sum()))
    return distance
    
def Pol2Cart(theta,r):
    "输入theta是角度，程序内转化为弧度"
    theta=np.double(theta)/180.0*pi
    x=np.multiply(r,np.cos(theta))
    y=np.multiply(r,np.sin(theta))
    y=-1*y
    return x,y
    
def Cart2Pol(x,y):
    r=Distance([0,0],[x,y])
    y=-y
    cos_theta=np.divide(np.double(x),r)
    if y>0:
        theta=np.arccos(cos_theta)
    else:
        theta=-1*np.arccos(cos_theta)
    theta=theta/pi*180.0
    return theta,r

def ActionofSheep(position_sheep,position_wolf,policy_sheep,speed=20):
    action_sheep = policy_sheep[(tuple(position_sheep),tuple(position_wolf))]
    action_sheep = list(np.multiply(np.array(action_sheep),speed))
    return action_sheep

def ActionofWolf(position_sheep,position_wolf,speed=20,subtlety=0):
    distance=Distance(position_sheep,position_wolf)
    p_s=np.double(position_sheep)
    p_w=np.double(position_wolf)
    [theta,r]=Cart2Pol(p_s[0]-p_w[0],p_s[1]-p_w[1])
    subtlety_theta=np.random.uniform(-subtlety,subtlety)
    theta=subtlety_theta+theta
    if distance==0:
        motion=[speed,speed]
        "[x,y]"
    else:
        motion_theta=theta
#        motion_theta=np.round((theta+45)/90)*90
        motion_r=speed
        motion=[motion_theta,motion_r]
        "[theta,r]"
    action_wolf=Pol2Cart(motion[0],motion[1])
    return action_wolf

def Chasing(policy_sheep,w=600,h=600,speed=1,time=1000):
    pygame.init()
    screen=pygame.display.set_mode([w,h])
    circleR=10
    color_sheep=[255,0,0]
    color_wolf=[255,255,255]
    position = dict()
    position['sheep'] = [[20,15],[20,15],[20,15],[20,15],[20,15]]
    position['wolf'] = [[10,15],[10,15],[10,15],[10,15],[10,15]]
    screen.fill([0,0,0])
    drawpositionsheep = list(np.multiply(position['sheep'][-1],20))
    drawpositionwolf = list(np.multiply(position['wolf'][-1],20))
    pygame.draw.circle(screen,color_sheep,drawpositionsheep,circleR)
    pygame.draw.circle(screen,color_wolf,drawpositionwolf,circleR)
    pygame.display.flip()
    pygame.time.wait(100)
    for i in range(time):
        screen=pygame.display.set_mode([w,h])
        action_sheep = ActionofSheep(position['sheep'][-1],position['wolf'][-1],policy_sheep,speed)
        action_wolf = ActionofWolf(position['sheep'][-5],position['wolf'][-1],speed,subtlety=30)
        position_sheep = list(np.add(position['sheep'][-1],action_sheep))
        position_wolf = map(np.int,list(np.round(np.add(position['wolf'][-1],action_wolf))))
        position['sheep'].append(position_sheep)
        position['wolf'].append(position_wolf)
        screen.fill([0,0,0])
        drawpositionsheep = list(np.multiply(position['sheep'][-1],20))
        drawpositionwolf = list(np.multiply(position['wolf'][-1],20))
        print drawpositionsheep,drawpositionwolf,action_wolf
        pygame.draw.circle(screen,color_sheep,drawpositionsheep,circleR)
        pygame.draw.circle(screen,color_wolf,drawpositionwolf,circleR)
        pygame.display.flip()
        pygame.time.wait(100)
    pygame.quit()
    return position
    
def SaveTrajectory(position_dict,filename):
    data = position_dict.values()
    shape=np.array(data).shape   
    "object*time*xy"
    workbook=xlwt.Workbook()
    sheet=workbook.add_sheet('sheet1')
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                sheet.write(j,i*shape[2]+k,data[i][j][k])
    workbook.save(filename)
    return
    
        
def main():
    policy_sheep = pickle.load(open("sheep3030_policy.pkl","rb"))
    '''(sheep,wolf:action)'''
    position = Chasing(policy_sheep,w=600,h=600,speed=1,time=100)
#    SaveTrajectory(position,'wolf_with_5_delays_30subtlety.xls')      
    pygame.quit()
#    print position_list
    return

if __name__ == '__main__':
    main()