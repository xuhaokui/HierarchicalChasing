#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-20 10:57:09
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-13 13:09:47
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np 
import scipy.stats
import pygame
import pickle
import xlrd
import xlwt
import itertools as it
import sys
sys.setrecursionlimit(1000000)
pi = 3.14

def Distance(position1,position2):
    sumsquar=np.power([np.array(position1)-np.array(position2)],2)
    distance=np.float(np.sqrt(sumsquar.sum()))
    return distance
    
def Pol2Cart(theta,r):
    "输入theta是角度，程序内转化为弧度"
    theta=np.float(theta)/180.0*pi
    x=np.multiply(r,np.cos(theta))
    y=np.multiply(r,np.sin(theta))
    y=-1*y
    return x,y
    
def Cart2Pol(x,y):
	if (x==0)&(y==0):
		x=0.1
		y=0.1
	r=Distance([0,0],[x,y])
	y=-y
	cos_theta=np.divide(np.float(x),r)
	if y>0:
		theta=np.arccos(cos_theta)
	else:
		theta=-1*np.arccos(cos_theta)
	theta=theta/pi*180.0
	return theta,r

def rejectSampleNorm(mean,cov,min_value,max_value):
	result = np.random.normal(mean,cov)
	if (result<=max_value)&(result>=min_value):
		return result
	else:
		return rejectSampleNorm(mean, cov, min_value, max_value)

def positionInRange(position,range_area):
	if (position[0]<range_area[0])|(position[1]<range_area[1])|(position[0]>range_area[2])|(position[1]>range_area[3]):
		return False
	else:
		return True

# def positionDistance(position1,position2,distance_range):
# 	if Distance(position1,position2)>distance_range:
# 		return False
# 	else:
# 		return True

def computeWolfChase(wolf_current_position,sheep_current_position,step_length,step_length_old,kappa,time):
	direction_vector = list(np.array(sheep_current_position)-np.array(wolf_current_position))
	# print direction_vector,wolf_current_position,sheep_current_position
	[direction_theta,r] = Cart2Pol(direction_vector[0],direction_vector[1])
	direction_theta = np.divide(np.multiply(direction_theta,pi),180.0)
	# chase_theta = np.multiply(np.random.vonmises(direction_theta,kappa),180.0/pi)
	chase_theta = np.multiply(direction_theta,180.0/pi)
	strength_range = [0.5,3]
	# step_length = np.float(step_length)/0.5
	# print "step_length =",step_length
	if np.mod(time,8)==0:
		# step_length_use = rejectSampleNorm(step_length, 1, strength_range[0], strength_range[1])
		step_length_use = step_length_old
	else:
		step_length_use = step_length_old
	[chase_x,chase_y] = Pol2Cart(chase_theta,step_length_use*2.0)
	chase_vector = [chase_x,chase_y]
	# print chase_vector,direction_theta,chase_theta
	return chase_vector,step_length_use

def computeSheepEscape(wolf_current_position,sheep_current_position,policy_sheep,step_length,kappa):
	wolf_current_position_trans = list(np.multiply(wolf_current_position,30.0/25.0))
	sheep_current_position_trans = list(np.multiply(sheep_current_position,30.0/25.0))
	action_sheep = policy_sheep[(tuple([np.int(i) for i in sheep_current_position_trans]),tuple([np.int(i) for i in wolf_current_position_trans]))]
	# action_sheep = [0,0]
	if action_sheep[0]==0&action_sheep[1]==0:
		x = (np.random.binomial(1,0.5)-0.5)*2.0
		y = (np.random.binomial(1,0.5)-0.5)*2.0
		# print x,y
		action_sheep = [x,y]
	[direction_theta,r] = Cart2Pol(action_sheep[0],action_sheep[1])
	# print direction_theta
	# direction_theta = np.divide(np.multiply(direction_theta,pi),180.0)
	# escape_theta = np.multiply(np.random.vonmises(direction_theta,400),180.0/pi)
	escape_theta = direction_theta
	# print escape_theta
	if Distance(wolf_current_position,sheep_current_position)<8:
		step_length = step_length*(2.0+np.abs(Distance(wolf_current_position,sheep_current_position)-8.0)*0.1)
	[escape_x,escape_y] = Pol2Cart(escape_theta,step_length)
	escape_vector = [escape_x,escape_y]
	# print action_sheep,direction_theta,escape_theta,escape_vector
	return escape_vector

def computeMasterWalk(wolf_current_position,sheep_current_position,master_current_position,master_old_position,step_length,kappa):
	master_old_vector = list(np.array(master_current_position)-np.array(master_old_position))
	[direction_theta,r] = Cart2Pol(master_old_vector[0],master_old_vector[1])
	# if master_current_position[1]<1:
	# 	direction_theta = -90.0
	# elif master_current_position[1]>24:
	# 	direction_theta = 90.0
	direction_theta = np.divide(np.multiply(direction_theta,pi),180.0)
	walk_theta = np.multiply(np.random.vonmises(direction_theta,np.float(kappa/1)),180.0/pi)
	[walk_x1,walk_y1] = Pol2Cart(walk_theta,step_length)
	walk_vector1 = [walk_x1,walk_y1]
	direction_sheep = list(np.array(sheep_current_position)-np.array(wolf_current_position))
	[direction_sheep_theta,r] = Cart2Pol(direction_sheep[0],direction_sheep[1])
	direction_sheep_theta = np.add(np.divide(np.multiply(direction_sheep_theta,pi),180.0),np.random.binomial(1,0.5)*180.0-90.0)
	alongchase_theta = np.multiply(np.random.vonmises(direction_sheep_theta,kappa),180.0/pi)
	[walk_x2,walk_y2] = Pol2Cart(alongchase_theta,step_length)
	walk_vector2 = [walk_x2,walk_y2]
	walk_vector2 = [0,0]
	walk_vector = list(np.add(walk_vector1,walk_vector2))
	return walk_vector

def computeSheepWalk(sheep_current_position,sheep_old_position,step_length,kappa):
	sheep_old_vector = list(np.array(sheep_current_position)-np.array(sheep_old_position))
	[direction_theta,r] = Cart2Pol(sheep_old_vector[0],sheep_old_vector[1])
	direction_theta = np.divide(np.multiply(direction_theta,pi),180.0)
	walk_theta = np.multiply(np.random.vonmises(direction_theta,np.float(kappa/1)),180.0/pi)
	[walk_x,walk_y] = Pol2Cart(walk_theta,step_length*2)
	walk_vector = [walk_x,walk_y]
	return walk_vector

def computeDistractorWalk(distractor_current_position,distractor_old_position,step_length,kappa):
	distractor_old_vector = list(np.array(distractor_current_position)-np.array(distractor_old_position))
	[direction_theta,r] = Cart2Pol(distractor_old_vector[0],distractor_old_vector[1])
	direction_theta = np.divide(np.multiply(direction_theta,pi),180.0)
	walk_theta = np.multiply(np.random.vonmises(direction_theta,np.float(kappa/1)),180.0/pi)
	[walk_x,walk_y] = Pol2Cart(walk_theta,step_length*2)
	walk_vector = [walk_x,walk_y]
	return walk_vector

def computeMasterLeave(wolf_current_position,sheep_current_position,step_length,kappa):
	master_leave_vector = list(np.array(wolf_current_position)-np.array(sheep_current_position))
	[direction_theta,r] = Cart2Pol(master_leave_vector[0],master_leave_vector[1])
	# flag = np.random.normal(0,1)
	# if flag<0:
	# 	direction_theta = direction_theta-90
	# else:
	# 	direction_theta = direction_theta+90
	direction_theta = np.divide(np.multiply(direction_theta,pi),180.0)
	leave_theta = np.multiply(np.random.vonmises(direction_theta,np.float(kappa/1)),180.0/pi)
	[leave_x,leave_y] = Pol2Cart(leave_theta,step_length)
	leave_vector = [leave_x,leave_y]
	return leave_vector

def computeLeashForce(position_from,position_self,length_limit,k_old,time):
	'''leash force without noise'''
	leashforce_vector = list(np.array(position_from)-np.array(position_self))
	[direction_theta,r] = Cart2Pol(leashforce_vector[0],leashforce_vector[1])
	leash_length = Distance(position_from,position_self)
	# print position_from,position_self,leash_length,length_limit
	if np.mod(time,10)==0:
		# k_use = rejectSampleNorm(1, 0.1, 0.9, 1.1)
		k_use = k_old
	else:
		k_use = k_old
	if leash_length>length_limit:
		force = np.abs(np.float(leash_length)-np.float(length_limit))*np.float(k_use)
	else:
		force = 0
	[force_x,force_y] = Pol2Cart(direction_theta,force)
	force_vector = [force_x,force_y]
	return force_vector,k_use

def computeWolf(wolf_old_position,wolf_current_position,sheep_current_position,master_current_position,step_length,step_length_old,kappa,length_limit,k_old,range_area,time):
	[chase_vector,step_length_use] = computeWolfChase(wolf_current_position, sheep_current_position, step_length,step_length_old, kappa,time)
	[force_wolf_vector,k_use] = computeLeashForce(master_current_position, wolf_current_position, length_limit, k_old,time)
	wolf_speed = list(np.array(wolf_current_position)-np.array(wolf_old_position))
	# print wolf_speed,chase_vector,force_wolf_vector
	wolf_motion = list(np.add(chase_vector,force_wolf_vector))
	# wolf_motion = list(np.add(chase_vector,force_wolf_vector)+np.array(wolf_speed))
	wolf_new_position = list(np.add(wolf_current_position,wolf_motion))
	# return wolf_motion,wolf_new_position,k_use,step_length_use
	if positionInRange(wolf_new_position, range_area):
		# print wolf_current_position,wolf_new_position
		return wolf_motion,wolf_new_position,k_use,step_length_use
	else:
		kappa = np.divide(np.float(kappa),10.0)
		return computeWolf(wolf_old_position,wolf_current_position, sheep_current_position, master_current_position, step_length, step_length_old, kappa, length_limit, k_old, range_area, time)

def computeSheep(wolf_current_position,sheep_current_position,sheep_old_position,policy_sheep,step_length,kappa,range_area):
	escape_vector = computeSheepEscape(wolf_current_position, sheep_current_position, policy_sheep, step_length, kappa)
	sheep_walk_vector = computeSheepWalk(sheep_current_position, sheep_old_position, step_length, kappa)
	wolf_sheep_distance = Distance(wolf_current_position,sheep_current_position)
	if wolf_sheep_distance>8:
		p_escape = np.exp(np.divide(np.float(8-wolf_sheep_distance),2.0))
	else:
		p_escape = 1
	sheep_motion = list(np.add(np.multiply(p_escape,escape_vector),np.multiply(1-p_escape,sheep_walk_vector)))
	# print "sheep_walk_vector =",sheep_walk_vector
	sheep_new_position = list(np.add(sheep_current_position,sheep_motion))
	# sheep_new_position = sheep_current_position
	if positionInRange(sheep_new_position, range_area):
		return sheep_motion,sheep_new_position
	else:
		kappa = np.divide(np.float(kappa),10.0)
		return computeSheep(wolf_current_position, sheep_current_position,sheep_old_position, policy_sheep, step_length, kappa, range_area)

def computeMaster(wolf_current_position,sheep_current_position,master_current_position,master_old_position,step_length,kappa,length_limit,k,range_area):
	walk_vector = computeMasterWalk(wolf_current_position,sheep_current_position,master_current_position, master_old_position, 2.0*step_length, kappa)
	leave_vector = computeMasterLeave(wolf_current_position, sheep_current_position, step_length, kappa)
	wolf_sheep_distance = Distance(wolf_current_position,sheep_current_position)
	if (wolf_sheep_distance>3):
		p_leave = np.exp(np.divide(np.float(3-wolf_sheep_distance),2.0))
		# p_leave = np.random.uniform(0,0.5)
		# p_leave = -1*np.exp(np.divide(np.float(wolf_sheep_distance-8),2.0))
	else:
		p_leave = 1
	# force_master_vector = computeLeashForce(wolf_current_position, master_current_position, length_limit, k)
	# force_master_vector = list(np.multiply(force_master_vector,0))
	# p_leave = 0
	master_motion = list(np.add(np.multiply(p_leave,leave_vector),np.multiply(1-np.abs(p_leave),walk_vector)))
	master_new_position = list(np.add(master_current_position,master_motion))
	# master_new_position = master_current_position
	if positionInRange(master_new_position, range_area)&(Distance(master_new_position,sheep_current_position)>0)&(Distance(master_new_position,sheep_current_position)<22):
		return master_motion,master_new_position
	else:
		kappa = np.divide(np.float(kappa),10.0)
		return computeMaster(wolf_current_position, sheep_current_position,master_current_position, master_old_position, step_length, kappa, length_limit, k, range_area)

def computeDistractor(distractor_current_position,distractor_old_position,step_length,kappa,range_area):
	walk_vector = computeDistractorWalk(distractor_current_position, distractor_old_position, step_length, kappa)
	distractor_new_position = list(np.add(distractor_current_position,walk_vector))
	if positionInRange(distractor_new_position,range_area):
		return walk_vector,distractor_new_position
	else:
		kappa = np.divide(np.float(kappa),10.0)
		return computeDistractor(distractor_current_position, distractor_old_position, step_length, kappa, range_area)

def initiateMotion(position_list,policy_sheep,step_length,kappa,length_limit,k,range_area):
	wolf1_current_position = position_list[-1][0]
	sheep1_current_position = position_list[-1][1]
	master1_current_position = position_list[-1][2]
	wolf2_current_position = position_list[-1][3]
	sheep2_current_position = position_list[-1][4]
	master2_current_position = position_list[-1][5]
	distractor1_current_position = position_list[-1][6]
	distractor2_current_position = position_list[-1][7]
	distractor3_current_position = position_list[-1][8]
	step_length_old = np.float(step_length)/0.5
	[wolf1_motion,wolf1_new_position,k_use1,step_length_use1] = computeWolf(wolf1_current_position,wolf1_current_position, sheep1_current_position, master1_current_position, step_length,step_length_old, kappa, length_limit, k,range_area,1)
	[wolf2_motion,wolf2_new_position,k_use2,step_length_use2] = computeWolf(wolf2_current_position,wolf2_current_position, sheep2_current_position, master2_current_position, step_length,step_length_old, kappa, length_limit, k,range_area,1)
	sheep1_walk_theta = np.random.uniform(-180,180)
	[sheep1_walk_x,sheep1_walk_y] = Pol2Cart(sheep1_walk_theta,step_length)
	sheep1_motion = [sheep1_walk_x,sheep1_walk_y]
	# sheep1_new_position = list(np.add(sheep1_current_position,sheep1_motion))
	sheep1_new_position = sheep1_current_position
	sheep2_walk_theta = np.random.uniform(-180,180)
	[sheep2_walk_x,sheep2_walk_y] = Pol2Cart(sheep2_walk_theta,step_length)
	sheep2_motion = [sheep2_walk_x,sheep2_walk_y]
	# sheep2_new_position = list(np.add(sheep2_current_position,sheep2_motion))
	sheep2_new_position = sheep2_current_position
	# walk_theta = np.random.uniform(-180,180)
	walk1_theta = 90.0
	[walk1_x,walk1_y] = Pol2Cart(walk1_theta,step_length)
	master1_motion = [walk1_x,walk1_y]
	master1_new_position = list(np.add(master1_current_position,master1_motion))
	master1_new_position = master1_current_position
	walk2_theta = 90.0
	[walk2_x,walk2_y] = Pol2Cart(walk2_theta,step_length)
	master2_motion = [walk2_x,walk2_y]
	master2_new_position = list(np.add(master2_current_position,master2_motion))
	master2_new_position = master2_current_position
	walk3_theta = np.random.uniform(-180,180)
	[walk3_x,walk3_y] = Pol2Cart(walk3_theta,step_length)
	distractor_motion = [walk3_x,walk3_y]
	distractor1_new_position = list(np.add(distractor1_current_position,distractor_motion))
	walk3_theta = np.random.uniform(-180,180)
	[walk3_x,walk3_y] = Pol2Cart(walk3_theta,step_length)
	distractor_motion = [walk3_x,walk3_y]
	distractor2_new_position = list(np.add(distractor2_current_position,distractor_motion))
	walk3_theta = np.random.uniform(-180,180)
	[walk3_x,walk3_y] = Pol2Cart(walk3_theta,step_length)
	distractor_motion = [walk3_x,walk3_y]
	distractor3_new_position = list(np.add(distractor3_current_position,distractor_motion))
	new_position_list = [wolf1_new_position,sheep1_new_position,master1_new_position,wolf2_new_position,sheep2_new_position,master2_new_position,distractor1_new_position,distractor2_new_position,distractor3_new_position]
	return new_position_list

def generateMotion(position_alltime_list,policy_sheep,step_length,step_length_old,length_limit,kappa,k,range_area,time):
	'''position_alltime_list = [[wolf_position_t0],[sheep_position_t0],[master_position_t0]][[wolf_position_t1]...]'''
	wolf1_current_position = position_alltime_list[-1][0]
	wolf1_old_position = position_alltime_list[-2][0]
	sheep1_current_position = position_alltime_list[-1][1]
	sheep1_old_position = position_alltime_list[-2][1]
	master1_current_position = position_alltime_list[-1][2]
	master1_old_position = position_alltime_list[-2][2]
	wolf2_current_position = position_alltime_list[-1][3]
	wolf2_old_position = position_alltime_list[-2][3]
	sheep2_current_position = position_alltime_list[-1][4]
	sheep2_old_position = position_alltime_list[-2][4]
	master2_current_position = position_alltime_list[-1][5]
	master2_old_position = position_alltime_list[-2][5]
	distractor1_current_position = position_alltime_list[-1][6]
	distractor2_current_position = position_alltime_list[-1][7]
	distractor3_current_position = position_alltime_list[-1][8]
	distractor1_old_position = position_alltime_list[-2][6]
	distractor2_old_position = position_alltime_list[-2][7]
	distractor3_old_position = position_alltime_list[-2][8]
	[wolf1_motion,wolf1_new_position,k_use1,step_length_use1] = computeWolf(wolf1_old_position,wolf1_current_position, sheep1_current_position, master1_current_position, step_length,step_length_old, kappa, length_limit, k,range_area,time)
	[wolf2_motion,wolf2_new_position,k_use2,step_length_use2] = computeWolf(wolf2_old_position,wolf2_current_position, sheep2_current_position, master2_current_position, step_length,step_length_old, kappa, length_limit, k,range_area,time)
	[sheep1_motion,sheep1_new_position] = computeSheep(wolf1_current_position, sheep1_current_position, sheep1_old_position, policy_sheep, step_length, kappa, range_area)
	[sheep2_motion,sheep2_new_position] = computeSheep(wolf2_current_position, sheep2_current_position, sheep2_old_position, policy_sheep, step_length, kappa, range_area)
	[master1_motion,master1_new_position] = computeMaster(wolf1_current_position,sheep1_current_position, master1_current_position, master1_old_position, step_length, kappa, length_limit, k,range_area)
	[master2_motion,master2_new_position] = computeMaster(wolf2_current_position,sheep2_current_position, master2_current_position, master2_old_position, step_length, kappa, length_limit, k,range_area)
	[distractor1_motion,distractor1_new_position] = computeDistractor(distractor1_current_position, distractor1_old_position, step_length, kappa, range_area)
	[distractor2_motion,distractor2_new_position] = computeDistractor(distractor2_current_position, distractor2_old_position, step_length, kappa, range_area)
	[distractor3_motion,distractor3_new_position] = computeDistractor(distractor3_current_position, distractor3_old_position, step_length, kappa, range_area)
	new_position_list = [wolf1_new_position,sheep1_new_position,master1_new_position,wolf2_new_position,sheep2_new_position,master2_new_position,distractor1_new_position,distractor2_new_position,distractor3_new_position]
	position_alltime_list.append(new_position_list)
	pygame.init()
	screen=pygame.display.set_mode([np.multiply(range_area[2],20),np.multiply(range_area[3],20)])
	circleR=10
	screen.fill([0,0,0])
	color = [[0,0,0],[0,0,0],[255,182,182],[255,255,50],[50,255,255],[255,0,255],[0,0,0],[0,0,0],[0,0,0]]
	# pygame.draw.line(screen,[255,255,255],np.multiply(master1_new_position,20.0),np.multiply(wolf1_new_position,20.0))
	pygame.draw.line(screen,[255,255,255],np.multiply(master2_new_position,20.0),np.multiply(wolf2_new_position,20.0))
	for drawposition in position_alltime_list[-1]:
		position_list_time = position_alltime_list[-1]
		# print drawposition,position_list_time
		# print drawposition
		pygame.draw.circle(screen,color[position_list_time.index(drawposition)],[np.int(np.multiply(i,20)) for i in drawposition],circleR)
	pygame.display.flip()
	pygame.time.wait(200)
	print time, new_position_list
	if time==0:
		pygame.quit()
		return position_alltime_list
	else:
		time = time-1
		return generateMotion(position_alltime_list, policy_sheep, step_length,step_length_old, length_limit, kappa, k,range_area, time)

def replaceMaster(filename,position_alltime_list,step_length,kappa,range_area,time=1):
	filename_new = filename[0:-4]+"_replace.xls"
	wolf_current_position = position_alltime_list[time][0]
	sheep_current_position = position_alltime_list[time][1]
	master_old_position = position_alltime_list[time-1][2]
	master_current_position = position_alltime_list[time][2]
	[master_motion,master_new_position] = computeMaster(wolf_current_position, sheep_current_position, master_current_position, master_old_position, step_length, kappa, 1, 1, range_area)
	pygame.init()
	screen=pygame.display.set_mode([np.multiply(range_area[2],20),np.multiply(range_area[3],20)])
	circleR=10
	color=[255,0,0]
	screen.fill([0,0,0])
	color = [[255,50,50],[50,255,50],[255,255,255]]
	for drawposition in position_alltime_list[time]:
		position_list_time = position_alltime_list[time]
		# print drawposition,position_list_time
		pygame.draw.circle(screen,color[position_list_time.index(drawposition)],[np.int(np.multiply(i,20)) for i in drawposition],circleR)
	pygame.display.flip()
	pygame.time.wait(200)
	print time,master_current_position,master_new_position
	if time==len(position_alltime_list)-1:
		pygame.quit()
		saveTrajectory(position_alltime_list,filename_new)
		return position_alltime_list
	else:
		position_alltime_list[time+1][2] = master_new_position
		time=time+1
		return replaceMaster(filename, position_alltime_list,step_length, kappa, range_area,time)



def saveTrajectory(position_alltime_list,filename):
    file = xlwt.Workbook()
    table = file.add_sheet('Sheet 1',cell_overwrite_ok=True)
    for time in range(len(position_alltime_list)):
    	for object in range(len(position_alltime_list[time])):
    		table.write(time,np.int(np.multiply(object,2)),position_alltime_list[time][object][0])
    		table.write(time,np.int(np.multiply(object,2)+1),position_alltime_list[time][object][1])
    file.save(filename)
    return

def readTrajectory(filename):
	data_list=list()
	file = xlrd.open_workbook(filename)
	table = file.sheets()[0]
	row_number = table.nrows
	column_number = table.ncols
	for row in range(row_number):
		data_row_list = list()
		for column in range(0,column_number,2):
			data_row_list.append(table.row_values(row)[column:column+2])
		data_list.append(data_row_list)
	return data_list

def main():
	policy_sheep = pickle.load(open("sheep3030_policy.pkl","rb"))
	step_length = 1.0
	kappa = 800
	range_area = [0,0,25,25]
	# filename = "test.xls"
	# position_alltime_list = readTrajectory(filename)
	# new_position_alltime_list = replaceMaster(filename, position_alltime_list, step_length, kappa, range_area)
	length_limit = 6.0
	k = 1.5
	position_list = [[[13,12],[7,12],[17,12],[13,20],[7,20],[17,20],[13,6],[7,6],[17,6]]]
	new_position_list = initiateMotion(position_list, policy_sheep, step_length, kappa, length_limit, k,range_area)
	position_list.append(new_position_list)
	time = 300
	position_alltime_list = generateMotion(position_list, policy_sheep, step_length,step_length, length_limit, kappa, k, range_area, time)
	saveTrajectory(position_alltime_list,"5.xls")
	return

if __name__=='__main__':
	main()

