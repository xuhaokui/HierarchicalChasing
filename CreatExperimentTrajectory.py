#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-14 14:16:25
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np 
import xlrd
import xlwt
import itertools as it
import matplotlib.pyplot as plt 
import sys
sys.setrecursionlimit(1000000)
pi = 3.14


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
    r=Distance([0,0],[x,y])
    y=-y
    cos_theta=np.divide(np.float(x),r)
    if y>0:
        theta=np.arccos(cos_theta)
    else:
        theta=-1*np.arccos(cos_theta)
    theta=theta/pi*180.0
    return theta,r

def computeSubtlety(position_alltime_list,wolf_index=0,sheep_index=1):
	def computeSubtletySingletime(wolf_oldtime_position,wolf_currenttime_position,sheep_oldtime_position):
		direction_vector = list(np.array(sheep_oldtime_position)-np.array(wolf_oldtime_position))
		motion_vector = list(np.array(wolf_currenttime_position)-np.array(wolf_oldtime_position))
		[direction_theta,direction_r] = Cart2Pol(direction_vector[0],direction_vector[1])
		[motion_theta,motion_r] = Cart2Pol(motion_vector[0],motion_vector[1])
		diff_theta = np.abs(np.float(direction_theta)-np.float(motion_theta))
		if diff_theta>180:
			diff_theta = 360-diff_theta
		return diff_theta
	diff_theta_list = [computeSubtletySingletime(position_alltime_list[time][wolf_index],position_alltime_list[time+1][wolf_index],position_alltime_list[time][sheep_index]) for time in range(len(position_alltime_list)-1)]
	mean_diff_theta = np.mean(diff_theta_list)
	return diff_theta_list,mean_diff_theta

def computeDistance(position_alltime_list,index1,index2):
	distance_list = [Distance(position_alltime_list[time][index1], position_alltime_list[time][index2]) for time in range(len(position_alltime_list))]
	mean_distance = np.mean(distance_list)
	return distance_list,mean_distance

def insertPosition(position_currenttime_list,position_newtime_list,min_distance):
	position_currenttime_newtime_list = list()
	distance_list = [Distance(position_currenttime_list[i], position_newtime_list[i]) for i in range(len(position_currenttime_list))]
	if np.divide(max(distance_list),min_distance)<1:
		position_currenttime_newtime_list = list()
	else:
		point_number = np.int(np.divide(max(distance_list),min_distance))
		direction_vector_list = list(np.array(position_newtime_list)-np.array(position_currenttime_list))
		object_theta_length_list = [Cart2Pol(direction_vector[0],direction_vector[1]) for direction_vector in direction_vector_list]
		insert_position_list = list()
		for i in range(point_number):
			insert_position_vector = [Pol2Cart(object_theta_length_list[j][0],np.float(object_theta_length_list[j][1])/np.float(point_number+1)*np.float(i+1)) for j in range(len(object_theta_length_list))]
			insert_position = [list(np.add(insert_position_vector[j],position_currenttime_list[j])) for j in range(len(insert_position_vector))]
			insert_position_list.append(insert_position)
		position_currenttime_newtime_list = insert_position_list
	position_currenttime_newtime_list.append(position_newtime_list)
	return position_currenttime_newtime_list

def insertAllPosition(position_alltime_list,min_distance):
	position_alltime_new_list = list()
	position_alltime_new_list.append(position_alltime_list[0])
	for time in range(1,len(position_alltime_list)):
		position_currenttime_list = position_alltime_list[time-1]
		position_newtime_list = position_alltime_list[time]
		position_currenttime_newtime_list = insertPosition(position_currenttime_list, position_newtime_list, min_distance)
		position_alltime_new_list.extend(position_currenttime_newtime_list)
	return position_alltime_new_list

def masterDelay(position_alltime_list,delay_time):
	if delay_time>0:
		position_alltime_new_list = position_alltime_list[0:0-delay_time]
		for i in range(len(position_alltime_new_list)):
			position_alltime_new_list[i][2] = position_alltime_list[i+delay_time][2]
	else:
		position_alltime_new_list = position_alltime_list[0-delay_time:]
		for i in range(len(position_alltime_new_list)):
			position_alltime_new_list[i][0] = position_alltime_list[i-delay_time][0]
			position_alltime_new_list[i][1] = position_alltime_list[i-delay_time][1]
	return position_alltime_new_list

def wolfDelay(position_alltime_list,delay_time):
	if delay_time>0:
		position_alltime_new_list = position_alltime_list[0:0-delay_time]
		for i in range(len(position_alltime_new_list)):
			position_alltime_new_list[i][0] = position_alltime_list[i+delay_time][0]
	else:
		position_alltime_new_list = position_alltime_list[0-delay_time:]
		for i in range(len(position_alltime_new_list)):
			position_alltime_new_list[i][1] = position_alltime_list[i-delay_time][1]
			position_alltime_new_list[i][2] = position_alltime_list[i-delay_time][2]
	return position_alltime_new_list

def sheepDelay(position_alltime_list,delay_time):
	if delay_time>0:
		position_alltime_new_list = position_alltime_list[0:0-delay_time]
		for i in range(len(position_alltime_new_list)):
			position_alltime_new_list[i][1] = position_alltime_list[i+delay_time][1]
	else:
		position_alltime_new_list = position_alltime_list[0-delay_time:]
		for i in range(len(position_alltime_new_list)):
			# position_alltime_new_list[i][0] = position_alltime_list[i-delay_time][0]
			# position_alltime_new_list[i][2] = position_alltime_list[i-delay_time][2]
			position_alltime_new_list[i][2] = position_alltime_list[i][2]
	return position_alltime_new_list

def mirrorObject(position_alltime_list,object_index,range_area):
	position_alltime_new_list = position_alltime_list[0:]
	for time in range(len(position_alltime_new_list)):
		position_alltime_new_list[time][object_index][0] = np.multiply(range_area[2],1.0)-np.float(position_alltime_list[time][object_index][0])
		position_alltime_new_list[time][object_index][1] = np.multiply(range_area[3],1.0)-np.float(position_alltime_list[time][object_index][1])
	return position_alltime_new_list

def main():
	filename="3(5).xls"
	filename_new = filename[0:-4]+"_insert.xls"
	# filename_new = "1(1)_subtlety.xls"
	# filename_new = '4'+filename[1:]
	min_distance = 0.5
	position_alltime_list = readTrajectory(filename)
	# position_alltime_list = position_alltime_list[150:]
	position_alltime_new_list = insertAllPosition(position_alltime_list, min_distance)
	# position_alltime_new_list = mirrorObject(position_alltime_list, 1, [0,0,25,25])
	# position_alltime_new_list = masterDelay(position_alltime_list,15)
	# position_alltime_new_list = wolfDelay(position_alltime_list, 30)
	# position_alltime_new_list = sheepDelay(position_alltime_list, -60)
	print len(position_alltime_list),len(position_alltime_new_list)
	saveTrajectory(position_alltime_new_list,filename_new)
	# wm=list()
	# for i in range(736):
	# 	position_used_alltime_list = position_alltime_list[i:i+600]
	# 	[diff_theta_list,wolfmaster_mean_diff_theta] = computeSubtlety(position_used_alltime_list,0,2)
	# 	wm.append(wolfmaster_mean_diff_theta)
	# print min(wm),wm.index(min(wm))
	# begin_index = 5
	# position_used_alltime_list = position_alltime_list[begin_index:]
	# position_used_alltime_list = position_alltime_list
	# [wolfsheep_diff_theta_list,wolfsheep_mean_diff_theta] = computeSubtlety(position_used_alltime_list,0,1)
	# [wolfmaster_diff_theta_list,wolfmaster_mean_diff_theta] = computeSubtlety(position_used_alltime_list,0,2)
	# wolfsheep_subtlety = [np.mean(wolfsheep_diff_theta_list[i*120:(i+1)*120]) for i in range(4)]
	# wolfmaster_subtlety = [np.mean(wolfmaster_diff_theta_list[i*120:(i+1)*120]) for i in range(4)]
	# print wolfsheep_subtlety,wolfmaster_subtlety
	# print wolfsheep_mean_diff_theta,wolfmaster_mean_diff_theta
	# [wolfsheep_distance_list,wolfsheep_mean_distance] = computeDistance(position_alltime_list, 0,1)
	# [wolfmaster_distance_list,wolfmaster_mean_distance] = computeDistance(position_alltime_list,0,2)
	# print "wolfsheep =",wolfsheep_mean_distance
	# print "wolfmaster =",wolfmaster_mean_distance
	# plt.ion()
	# # # plt.hist(diff_theta_list,20)
	# plt.plot(range(len(wolfsheep_diff_theta_list)),wolfsheep_diff_theta_list)
	# plt.plot(range(len(wolfmaster_diff_theta_list)),wolfmaster_diff_theta_list)
	# plt.show()
	# plt.pause(5)
	return

if __name__=='__main__':
	main()
