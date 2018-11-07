#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-05 14:48:04
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

def Distance(position1,position2):
    sumsquar=np.power([np.array(position1)-np.array(position2)],2)
    distance=np.float(np.sqrt(sumsquar.sum()))
    return distance

def saveTrajectory(position_alltime_list,filename):
    file = xlwt.Workbook()
    table = file.add_sheet('Sheet 1',cell_overwrite_ok=True)
    for time in range(len(position_alltime_list)):
    	for object in range(len(position_alltime_list[time])):
    		table.write(time,np.int(np.multiply(object,2)),position_alltime_list[time][object][0])
    		table.write(time,np.int(np.multiply(object,2)+1),position_alltime_list[time][object][1])
    file.save(filename)
    return

def judgmentInSameNode(m,n,node_guest_list):
	return (m in node_guest_list)&(n in node_guest_list)

def computeCommonNodes(m,n,tree_dict,current_level=0,nodes_number=0):
	level_node_list = tree_dict[current_level][0]
	level_judgment_list = [judgmentInSameNode(m, n, node_guest_list) for node_guest_list in level_node_list]
	nodes_number = nodes_number+(True in level_judgment_list)
	if current_level==max(tree_dict.keys()):
		return nodes_number
	else:
		current_level = current_level+1
		return computeCommonNodes(m, n, tree_dict,current_level,nodes_number)

def computeKernel(position_list,tree_dict,tau=2):
	kernel_list = list()
	for i in range(len(position_list)):
		kernel_line_list = list()
		for j in range(len(position_list)):
			if i==j:
				k_element = np.multiply(1,tau)
			else:
				k_element = np.multiply(np.divide(np.float(1),np.float(len(position_list))),np.multiply(1,tau))
			nodes_number = computeCommonNodes(i+1,j+1,tree_dict)
			kernel_line_list.append(np.sqrt(np.multiply(np.power(k_element,2),nodes_number)))
		kernel_list.append(kernel_line_list)
	return kernel_list

'''Generate Motion From Tree, Goal, Order'''

def initialMotionOnNode(tree_dict,step_length):
	'''motion_dict = {0:[[x,y]],1:[[x1,y1],[x2,y2]]...}'''
	cov = np.multiply([[1,0],[0,1]],np.multiply(step_length,10))
	motion_dict = dict()
	for key in tree_dict.keys():
		motion_dict[key] = tree_dict[key][0][:]
		for n in range(len(motion_dict[key])):
			motion_vector = list(np.random.multivariate_normal([step_length,step_length],cov))
			motion_dict[key][n] = motion_vector
	return motion_dict

def assignMotionOnNode(old_motion_dict,step_length,tau=1):
	motion_dict = dict()
	for key in old_motion_dict.keys():
		motion_dict[key] = old_motion_dict[key]
		for n in range(len(old_motion_dict[key])):
			old_motion_vector = old_motion_dict[key][n]
			step_length_old = Distance(old_motion_vector,[0,0])
			motion_vector_mean = np.multiply(old_motion_vector,np.divide(np.float(step_length),np.float(step_length_old)))
			cov = np.multiply([[1,0],[0,1]],np.multiply(step_length,tau))
			motion_vector = np.random.multivariate_normal(motion_vector_mean,cov)
			motion_dict[key][n] = list(motion_vector)
	return motion_dict

def computePath(tree_dict,guest,path=list(),level=0):
	'''guest = 1/2/3/4'''
	'''output: path = [node_level1,node_level2...]'''
	level_node_list = tree_dict[level][0]
	judgment_list = [guest in level_node_list[i] for i in range(len(level_node_list))]
	if (True in judgment_list):
		path.append(judgment_list.index(True))
	# print tree_dict,level,guest,judgment_list,(True not in judgment_list),path
	if (level == max(tree_dict.keys())):
		# print "here",guest,path
		return path
	else:
		level = level+1
		return computePath(tree_dict,guest,path,level)

def assignChaseMotionOnNode(tree_dict,old_motion_dict,order,wolf_position,sheep_position,step_length,policy_sheep,tau):
	motion_dict = assignMotionOnNode(old_motion_dict,step_length,tau)
	wolf_index = order[0]
	sheep_index = order[1]
	wolf_path = computePath(tree_dict, wolf_index,path=list())
	sheep_path = computePath(tree_dict, sheep_index,path=list())
	wolf_node = wolf_path[-1]
	sheep_node = sheep_path[-1]
	mean_motion = (np.array(sheep_position)-np.array(wolf_position))/Distance(sheep_position,wolf_position)*np.float(step_length*1.1)
	# print "here"
	cov = np.multiply([[1,0],[0,1]],np.multiply(step_length,tau))
	motion_dict[len(wolf_path)-1][wolf_node] = list(np.random.multivariate_normal(mean_motion,cov))
	sheep_position = [np.int(i) for i in sheep_position]
	wolf_position = [np.int(i) for i in wolf_position]
	action_sheep = policy_sheep[(tuple(sheep_position),tuple(wolf_position))]
	action_sheep = list(np.multiply(np.array(action_sheep),step_length))
	# print "action_sheep =",action_sheep
	motion_dict[len(sheep_path)-1][sheep_node] = list(np.random.multivariate_normal(action_sheep,cov))
	return motion_dict

def computeGuestMotion(tree_dict,motion_dict,step_length):
	object_number = len(tree_dict[0][0][0])
	motion_all_guest = range(object_number)
	# print motion_dict
	motion_dict[0][0] = [0,0]
	for guest in range(1,object_number+1):
		guest_path = computePath(tree_dict, guest,path=list())
		if guest==3:
			motion_dict[len(guest_path)-1][guest_path[-1]]=motion_dict[len(guest_path)-2][guest_path[-2]]
		motion_list = [motion_dict[level][guest_path[level]] for level in range(len(guest_path))]
		motion_guest = np.sum(motion_list,0)
		motion_guest = list(np.multiply(motion_guest,np.divide(np.float(step_length),Distance(motion_guest,[0,0]))))
		print guest,motion_guest
		motion_all_guest[guest-1] = motion_guest
	return motion_all_guest

def judgmentPositionInRange(position_list,range_area):
	'''range_area = [0,0,600,600]'''
	def positionInRange(position,range_area):
		if (position[0]<range_area[0])|(position[1]<range_area[1])|(position[0]>range_area[2])|(position[1]>range_area[3]):
			return False
		else:
			return True
	judgment_list = [positionInRange(position, range_area) for position in position_list]
	if False in judgment_list:
		flag = False
	else:
		flag = True
	return flag

def judgmentPositionDistance(position_list,distance_range):
	def positionDistance(position1,position2,distance_range):
		if Distance(position1,position2)>distance_range:
			return False
		else:
			return True
	judgment_list = [positionDistance(position_list[i[0]],position_list[i[1]],distance_range) for i in list(it.combinations(range(len(position_list)),2))]
	if False in judgment_list:
		flag = False
	else:
		flag = True
	return flag

def generateOneStepMotion(old_position_list,tree_dict,order,old_motion_dict,goal,range_area,step_length,policy_sheep,tau):
	if goal==1:
		wolf_position = old_position_list[order[0]-1]
		sheep_position = old_position_list[order[1]-1]
		new_motion_dict = assignChaseMotionOnNode(tree_dict, old_motion_dict, order, wolf_position, sheep_position,step_length,policy_sheep,tau)
	else:
		new_motion_dict = assignMotionOnNode(old_motion_dict,step_length,tau)
	motion_all_guest = computeGuestMotion(tree_dict, new_motion_dict,step_length)
	new_position_list = [list(np.add(old_position_list[i],motion_all_guest[i])) for i in range(len(old_position_list))]
	distance_range = np.divide(range_area[3],np.float(600))*np.multiply(np.divide(5,0.6),24)
	if (judgmentPositionInRange(new_position_list,range_area)):
	# &(judgmentPositionDistance(new_position_list,distance_range)):
		# print new_motion_dict[1][0]
		return new_position_list,new_motion_dict
	else:
		return generateOneStepMotion(old_position_list, tree_dict, order, old_motion_dict, goal, range_area,step_length,policy_sheep,tau=10.0*tau)

def generateMotion(position_list,tree_dict,order,old_motion_dict,goal,range_area,step_length,policy_sheep,tau,time):
	'''range = [0,0,600,600]'''
	old_position_list = position_list[-1]
	[new_position_list,new_motion_dict] = generateOneStepMotion(old_position_list, tree_dict, order, old_motion_dict, goal, range_area,step_length,policy_sheep,tau)
	position_list.append(new_position_list)
	pygame.init()
	screen=pygame.display.set_mode([np.multiply(range_area[2],20),np.multiply(range_area[3],20)])
	circleR=10
	color=[255,0,0]
	screen.fill([0,0,0])
	color = [[255,50,50],[50,255,50],[255,255,255]]
	for drawposition in position_list[-1]:
		position_list_time = position_list[-1]
		# print drawposition,position_list_time
		pygame.draw.circle(screen,color[position_list_time.index(drawposition)],[np.int(np.multiply(i,20)) for i in drawposition],circleR)
	pygame.display.flip()
	pygame.time.wait(200)
	print time
	if time==0:
		pygame.quit()
		return position_list
	else:
		time=time-1
		# print position_list,tree_dict,order,new_motion_dict,goal,range_area,time
		return generateMotion(position_list,tree_dict,order,new_motion_dict,goal,range_area,step_length,policy_sheep,tau,time)

'''End of Generate Part'''
'''Compute probability of Motion Given Tree, Goal, Order'''


def computeChaseProbabilityCorrect(policy_sheep,tree_dict,wolf_index,sheep_index,position_wolf_oldtime,position_wolf_currenttime,position_wolf_newtime,position_sheep_oldtime,position_sheep_currenttime,position_sheep_newtime,tau=2):
	wolf_step_length = Distance(position_wolf_oldtime,position_wolf_currenttime)
	sheep_step_length = Distance(position_sheep_oldtime,position_sheep_currenttime)
	sheep_wolf_distance = Distance(position_sheep_currenttime,position_wolf_currenttime)
	direction_vector_currenttime = np.add(position_sheep_currenttime,np.multiply(-1,position_wolf_currenttime))
	wolf_chase_newtime = np.multiply(direction_vector_currenttime,np.divide(wolf_step_length,sheep_wolf_distance))
	action_sheep_currenttime = policy_sheep[(tuple([np.int(i) for i in position_sheep_currenttime]),tuple([np.int(i) for i in position_wolf_currenttime]))]
	sheep_chase_newtime = np.multiply(action_sheep_currenttime,sheep_step_length)
	wolf_motion_newtime = np.add(position_wolf_newtime,np.multiply(-1,position_wolf_currenttime))
	sheep_motion_newtime = np.add(position_sheep_newtime,np.multiply(-1,position_sheep_currenttime))
	direction_vector_oldtime = np.add(position_sheep_oldtime,np.multiply(-1,position_wolf_oldtime))
	wolf_chase_currenttime = np.multiply(direction_vector_oldtime,np.divide(wolf_step_length,sheep_wolf_distance))
	action_sheep_oldtime = policy_sheep[(tuple([np.int(i) for i in position_sheep_oldtime]),tuple([np.int(i) for i in position_wolf_oldtime]))]
	sheep_chase_currenttime = np.multiply(action_sheep_oldtime,sheep_step_length)
	wolf_motion_currenttime = np.add(position_wolf_currenttime,np.multiply(-1,position_wolf_oldtime))
	sheep_motion_currenttime = np.add(position_sheep_currenttime,np.multiply(-1,position_sheep_oldtime))
	wolf_nodes = computeCommonNodes(wolf_index,wolf_index,tree_dict)
	sheep_nodes = computeCommonNodes(sheep_index,sheep_index, tree_dict)
	cov_wolf_chase = np.array([[1,0],[0,1]])*tau*np.float(wolf_nodes-1)
	cov_sheep_chase = np.array([[1,0],[0,1]])*tau*np.float(sheep_nodes-1)
	p_wolf_chase = scipy.stats.multivariate_normal.pdf(wolf_motion_newtime - wolf_chase_newtime,wolf_motion_currenttime - wolf_chase_currenttime,cov_wolf_chase)
	p_sheep_chase = scipy.stats.multivariate_normal.pdf(sheep_motion_newtime - sheep_chase_newtime,sheep_motion_currenttime - sheep_chase_currenttime,cov_sheep_chase)
	cov_wolf_nochase = np.array([[1,0],[0,1]])*tau*np.float(wolf_nodes)
	cov_sheep_nochase = np.array([[1,0],[0,1]])*tau*np.float(sheep_nodes)
	p_wolf_nochase = scipy.stats.multivariate_normal.pdf(wolf_motion_newtime,wolf_motion_currenttime,cov_wolf_nochase)
	p_sheep_nochase = scipy.stats.multivariate_normal.pdf(sheep_motion_newtime,sheep_motion_currenttime,cov_sheep_nochase)
	p_correct = np.divide(np.multiply(p_wolf_chase,p_sheep_chase),np.multiply(p_wolf_nochase,p_sheep_nochase))
	return p_correct



def probabilitySingleDimSingleTime(position_oldtime_list,position_currenttime_list, position_newtime_list,dim,tree_dict):
	'''all position = [[x1,y1],[x2,y2],...,[xn,yn]]'''
	position_dim_oldtime_list = [position_oldtime_list[i][dim] for i in range(len(position_oldtime_list))]
	position_dim_currenttime_list = [position_currenttime_list[i][dim] for i in range(len(position_currenttime_list))]
	position_dim_newtime_list = [position_newtime_list[i][dim] for i in range(len(position_newtime_list))]
	mean_step_length = np.add(position_dim_currenttime_list,np.multiply(-1,position_dim_oldtime_list))
	cov = computeKernel(position_currenttime_list, tree_dict)
	# print position_dim_newtime_list,np.add(mean_step_length,position_dim_currenttime_list),cov
	p_dim_likelihood = scipy.stats.multivariate_normal.pdf(position_dim_newtime_list,np.add(mean_step_length,position_dim_currenttime_list),cov)
	# print p_dim_likelihood
	return p_dim_likelihood

def probabilitySingleTime(policy_sheep,position_oldtime_list,position_currenttime_list,position_newtime_list,tree_dict,goal,order):
	'''order = [1,2,3,4]'''
	p_likelihood_list_uncorrect = [probabilitySingleDimSingleTime(position_oldtime_list, position_currenttime_list, position_newtime_list, dim, tree_dict) for dim in range(len(position_currenttime_list[0]))]
	p_likelihood_uncorrect = reduce(np.multiply,p_likelihood_list_uncorrect)
	if goal==1:
		wolf_index = order[0]-1
		sheep_index = order[1]-1
		position_wolf_oldtime = position_oldtime_list[wolf_index]
		position_wolf_currenttime = position_currenttime_list[wolf_index]
		position_wolf_newtime = position_newtime_list[wolf_index]
		position_sheep_oldtime = position_oldtime_list[sheep_index]
		position_sheep_currenttime = position_currenttime_list[sheep_index]
		position_sheep_newtime = position_newtime_list[sheep_index]
		p_correct = computeChaseProbabilityCorrect(policy_sheep,tree_dict,wolf_index+1,sheep_index+1,position_wolf_oldtime, position_wolf_currenttime, position_wolf_newtime, position_sheep_oldtime, position_sheep_currenttime, position_sheep_newtime)
	else:
		p_correct = 1
	p_time_likelihood = np.multiply(p_likelihood_uncorrect,p_correct)
	# print "goal=",goal,p_time_likelihood,p_correct
	return p_time_likelihood

def likelihoodMotionFromTreeGoalOrder(policy_sheep,position_alltime_list,tree_dict,goal,order):
	'''position_alltime_list = [[[x1,y1],[x2,y2],...,[xn,yn]],[[x1,y1],[x2,y2],...,[xn,yn]]'''
	time = np.size(position_alltime_list,0)
	p_time_likelihood_list = map(lambda t:probabilitySingleTime(policy_sheep,position_alltime_list[t], position_alltime_list[t+1], position_alltime_list[t+2], tree_dict, goal, order),range(time-2))
	log_p_time_likelihood_list = [np.log(i) for i in p_time_likelihood_list]
	log_p_likelihood = np.divide(reduce(np.add,log_p_time_likelihood_list),np.float(time-2))
	p_likelihood = np.exp(log_p_likelihood)
	return p_likelihood,log_p_likelihood

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
	tree_list = pickle.load(open("tree_list.pkl","rb"))
	tree_number = 2
	tree_dict = tree_list[tree_number]
	order = [1,2,3]
	filename = "masterchase1.xls"
	position_alltime_list = readTrajectory(filename)
	position_alltime_list = position_alltime_list[0:10]
	goal = 1
	[p_likelihood,log_p_likelihood] = likelihoodMotionFromTreeGoalOrder(policy_sheep,position_alltime_list, tree_dict, goal, order)
	print p_likelihood,log_p_likelihood
	goal = 0
	[p_likelihood,log_p_likelihood] = likelihoodMotionFromTreeGoalOrder(policy_sheep,position_alltime_list, tree_dict, goal, order)
	print p_likelihood,log_p_likelihood
	# step_length = 1
	# initial_position = [[10,20],[20,20],[10,10]]
	# position_list = [initial_position]
	# initial_motion_dict = initialMotionOnNode(tree_dict, step_length)
	# range_area = [0,0,30,30]
	# time = 300
	# tau=0.2
	# position_alltime_list = generateMotion(position_list, tree_dict, order, initial_motion_dict, goal, range_area, step_length,policy_sheep,tau,time)
	# saveTrajectory(position_alltime_list, "masterchase4.xls")
	# print tree_dict
	return

if __name__ == '__main__':
	main()
