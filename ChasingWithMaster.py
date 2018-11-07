# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 17:28:06 2018

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

def MasterForce(position_wolf,position_master,action_wolf,distancelevel=5,k=0.01):
    distance = Distance(position_wolf,position_master)
    [theta,d] = Cart2Pol(position_master[0]-position_wolf[0],position_master[1]-position_wolf[1])
    if distance>=distancelevel:
        force = np.multiply(np.add(distance,-distancelevel),k)
        action_force = Pol2Cart(theta,force)
        action_wolf = np.add(action_wolf,action_force)
    return action_wolf
    
def RandomWalk(position_master,position_wolf,position_sheep,position_distractor,theta=-45,speed=1,cov=10):
    if isnan(theta):
        theta=np.random.uniform(-180,180)
    theta_new = np.random.normal(theta,cov)
    theta_new=np.round((np.int(np.round(theta_new))+45)/90)*90
    action = Pol2Cart(theta_new,speed)
    position_new = list(np.add(position_master,action))
    if (np.min(position_new)<3)|(np.max(position_new)>27)|(Distance(position_new,position_wolf)<4)|(Distance(position_new,position_sheep)<4)|(Distance(position_new,position_distractor)<4):
        position_new=RandomWalk(position_master,position_wolf,position_sheep,position_distractor,theta=theta,speed=1,cov=200)
    return map(np.int,position_new)
    
def Chasing(policy_sheep,w=600,h=600,speed=1,time=1000):
    pygame.init()
    screen=pygame.display.set_mode([w,h])
    circleR=10
    color_sheep=[0,255,0]
    color_wolf=[255,0,0]
    color_master = [255,255,255]
    color_distractor = [255,255,255]
    position = dict()
    position['sheep'] = [[5,5],[5,5],[5,5],[5,5],[5,5]]
    position['wolf'] = [[5,25],[5,25],[5,25],[5,25],[5,25]]
    position['master'] = [[25,5],[25,5],[25,5],[25,5],[25,5]]
    position['distractor'] = [[25,25],[25,25],[25,25],[25,25],[25,25]]
    screen.fill([0,0,0])
    drawpositionsheep = list(np.multiply(position['sheep'][-1],20))
    drawpositionwolf = list(np.multiply(position['wolf'][-1],20))
    drawpositionmaster = list(np.multiply(position['master'][-1],20))
    drawpositiondistractor = list(np.multiply(position['master'][-1],20))
    pygame.draw.circle(screen,color_sheep,drawpositionsheep,circleR)
    pygame.draw.circle(screen,color_wolf,drawpositionwolf,circleR)
    pygame.draw.circle(screen,color_master,drawpositionmaster,circleR)
    pygame.draw.circle(screen,color_distractor,drawpositiondistractor,circleR)
    pygame.display.flip()
    pygame.time.wait(100)
    for i in range(time):
        screen=pygame.display.set_mode([w,h])
        action_sheep = ActionofSheep(position['sheep'][-1],position['wolf'][-1],policy_sheep,speed)
        action_wolf = ActionofWolf(position['sheep'][-4],position['wolf'][-1],speed,subtlety=0)
        action_wolf = MasterForce(position['wolf'][-1],position['master'][-1],action_wolf,distancelevel=7,k=0.2)
#        action_wolf = ActionofSheep(position['wolf'][-1],position['master'][-1],policy_sheep,speed)
#        action_master = ActionofSheep(position['master'][-1],position['sheep'][-1],policy_sheep,speed)
        position_sheep = list(np.add(position['sheep'][-1],action_sheep))
        position_wolf = map(np.int,list(np.round(np.add(position['wolf'][-1],action_wolf))))
#        position_master = list(np.add(position['master'][-1],action_master))
        action_master_old = list(np.add(position['master'][-1],np.multiply(-1,position['master'][-2])))
        action_distractor_old = list(np.add(position['distractor'][-1],np.multiply(-1,position['distractor'][-2])))
        [theta_master,r_master] = Cart2Pol(action_master_old[0],action_master_old[1])
        [theta_distractor,r_distractor] = Cart2Pol(action_distractor_old[0],action_distractor_old[1])
        position_master = RandomWalk(position['master'][-1],position['wolf'][-1],position['sheep'][-1],position['distractor'][-1],theta_master,speed=1,cov=30)
        position_distractor = RandomWalk(position['distractor'][-1], position['wolf'][-1], position['sheep'][-1], position['master'][-1],theta_distractor,speed=1,cov=30)
#        position_master = position['master'][-1]
#        position_wolf = list(np.add(position['wolf'][-1],action_wolf))
#        position_master = list(np.add(position['master'][-1],action_master))
        position['sheep'].append(position_sheep)
        position['wolf'].append(position_wolf)
        position['master'].append(position_master)
        position['distractor'].append(position_distractor)
        screen.fill([0,0,0])
        drawpositionsheep = list(np.multiply(position['sheep'][-1],20))
        drawpositionwolf = list(np.multiply(position['wolf'][-1],20))
        drawpositionmaster = list(np.multiply(position['master'][-1],20))
        drawpositiondistractor = list(np.multiply(position['distractor'][-1],20))
        print drawpositionsheep,drawpositionwolf,drawpositionmaster,drawpositiondistractor
        pygame.draw.circle(screen,color_sheep,drawpositionsheep,circleR)
        pygame.draw.circle(screen,color_wolf,drawpositionwolf,circleR)
        pygame.draw.circle(screen,color_master,drawpositionmaster,circleR)
        pygame.draw.circle(screen,color_distractor,drawpositiondistractor,circleR)
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
    "(sheep,wolf:action)"
    position = Chasing(policy_sheep,w=600,h=600,speed=1,time=200)
    SaveTrajectory(position,'wolf_with_masterforce_4objs_d7k2_10.xls')      
    pygame.quit()
#    print position_list
    return

if __name__ == '__main__':
    main()