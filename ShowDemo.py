#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-14 19:41:37
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np 
import pygame
import xlrd
import sys
sys.setrecursionlimit(1000000)

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

def changePositionFromMujoco(position_alltime_list_old,initial_position_mujoco,range_area_mujoco):
	'''initial_position_mujoco = [[3.5,3.5],[0,0],[4.5,4.5]]'''
	'''range_area_mujoco = [0,0,20,20]'''
	position_alltime_list=list()
	for time in range(len(position_alltime_list_old)):
		position_list_time_old = position_alltime_list_old[time]
		position_list_time = list()
		for position in position_list_time_old:
			index = position_list_time_old.index(position)
			# print index,initial_position_mujoco[index],position
			new_x = np.add(np.divide(range_area_mujoco[2],2.0),np.add(initial_position_mujoco[index][0],position[0]))
			new_y = np.add(np.divide(range_area_mujoco[3],2.0),np.add(initial_position_mujoco[index][1],position[1]))
			new_position = [new_x,new_y]
			position_list_time.append(new_position)
		position_alltime_list.append(position_list_time)
	return position_alltime_list

def showMotion(position_alltime_list,range_area,time=0):
	pygame.init()
	screen=pygame.display.set_mode([np.multiply(range_area[2],20),np.multiply(range_area[3],20)])
	circleR=10
	screen.fill([0,0,0])
	color = [[255,128,182],[255,50,50],[50,255,50],[255,255,255]]
	for drawposition in position_alltime_list[time]:
		position_list_time = position_alltime_list[time]
		pygame.draw.circle(screen,color[position_list_time.index(drawposition)],[np.int(np.multiply(i,20)) for i in drawposition],circleR)
	pygame.display.flip()
	pygame.time.wait(50)
	print "time =",time
	if time==len(position_alltime_list)-1:
		pygame.quit()
		return
	else:
		time=time+5
		return showMotion(position_alltime_list,range_area,time)

def showMotionMasterDelay(position_alltime_list,range_area,delay_time,time=0):
	pygame.init()
	screen=pygame.display.set_mode([np.multiply(range_area[2],20),np.multiply(range_area[3],20)])
	circleR=10
	screen.fill([0,0,0])
	color = [[255,50,50],[50,255,50],[255,255,255]]
	wolf_position = position_alltime_list[time][0]
	sheep_position = position_alltime_list[time][1]
	master_position = position_alltime_list[time+delay_time][2]
	position_list_time = [wolf_position,sheep_position,master_position]
	for drawposition in position_list_time:	
		pygame.draw.circle(screen,color[position_list_time.index(drawposition)],[np.int(np.multiply(i,20)) for i in drawposition],circleR)
	pygame.display.flip()
	pygame.time.wait(50)
	print "time =",time
	if time==len(position_alltime_list)-1-delay_time:
		pygame.quit()
		return
	else:
		time=time+1
		return showMotionMasterDelay(position_alltime_list,range_area,delay_time,time)

def showMotionSheepDelay(position_alltime_list,range_area,delay_time,time=0):
	pygame.init()
	screen=pygame.display.set_mode([np.multiply(range_area[2],20),np.multiply(range_area[3],20)])
	circleR=10
	screen.fill([0,0,0])
	color = [[255,50,50],[50,255,50],[255,255,255]]
	wolf_position = position_alltime_list[time][0]
	sheep_position = position_alltime_list[time+delay_time][1]
	master_position = position_alltime_list[time][2]
	position_list_time = [wolf_position,sheep_position,master_position]
	for drawposition in position_list_time:	
		pygame.draw.circle(screen,color[position_list_time.index(drawposition)],[np.int(np.multiply(i,20)) for i in drawposition],circleR)
	pygame.display.flip()
	pygame.time.wait(0.02)
	print "time =",time
	if time==len(position_alltime_list)-1-delay_time:
		pygame.quit()
		return
	else:
		time=time+1
		return showMotionSheepDelay(position_alltime_list,range_area,delay_time,time)

def main():
	filename = "position_lightmaster.xls"
	range_area=[0,0,20,20]
	position_alltime_list = readTrajectory(filename)
	position_alltime_list = changePositionFromMujoco(position_alltime_list, [[3.5,3.5],[0,0],[4.5,4.5]], [0,0,20,20])
	position_alltime_list = position_alltime_list[800:]
	showMotion(position_alltime_list,range_area)
	# showMotionSheepDelay(position_alltime_list, range_area, delay_time=30)
	return

if __name__=='__main__':
	main()
