#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-04 15:42:55
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np
import scipy.stats
import pickle
import itertools as it
import MHSample as mh
import PriorTree
import GenerateMotion
import sys   
sys.setrecursionlimit(1000000)

def readTrajectory(filename):
	'''input: filename = string'''
	'''output: position_alltime_list = [[[x1t1,y1t1],[x2t1,y2t1]],[[x1t2,y1t2],[x2t2,y2t2]]], t*object_number*2'''
	position_alltime_list = GenerateMotion.readTrajectory(filename)
	return position_alltime_list

def priorTree(tree_number,tree_list):
	'''input: tree_number=scalar(0-9); tree_list read from .pkl file with all tree_dict'''
	'''output: probability of the tree'''
	p_tree = PriorTree.priorTreeRenormalize(np.int(tree_number), tree_list)
	return p_tree

def priorGoal(goal,p=0.5):
	'''input: goal=0: nochase, goal=1: chase'''
	'''output: probability of goal'''
	p_list = [1-p,p]
	return p_list[goal]

def priorOrder(order):
	'''order = [1,2,3,4]'''
	all_possible_order_list = list(it.permutations(order,len(order)))
	p_order = np.divide(1.0,np.float(len(all_possible_order_list)))
	return p_order

def likelihoodMotionFromTreeGoalOrder(policy_sheep,position_alltime_list,tree_number,goal,tree_list,order):
	'''input: tree_dict=key is level/value is list of list indicates guest with nodes'''
	'''output: probability of particular motion given tree and goal'''
	tree_dict = tree_list[np.int(tree_number)]
	[p_likelihood,log_p_likelihood] = GenerateMotion.likelihoodMotionFromTreeGoalOrder(policy_sheep,position_alltime_list, tree_dict, goal, order)
	return p_likelihood,log_p_likelihood

def posteriorTreeGoalOrderFromMotion(policy_sheep,position_alltime_list,tree_number,goal,tree_list,order):
	'''posterior from likelihood * prior'''
	p_tree = priorTree(tree_number,tree_list)
	p_goal = priorGoal(goal)
	p_order = priorOrder(order)
	[p_likelihood,log_p_likelihood] = likelihoodMotionFromTreeGoalOrder(policy_sheep,position_alltime_list, tree_number, goal, tree_list, order)
	# print "testhere",np.log(p_tree),np.log(p_goal),log_p_likelihood
	log_p_posterior = np.log(p_tree) + np.log(p_goal) + np.log(p_order) + log_p_likelihood
	p_posterior = np.exp(log_p_posterior)
	# print p_posterior
	return p_posterior

def posteriorGoalFromMotion(position_alltime_list,goal,tree_list,policy_sheep):
	object_number = len(position_alltime_list[0])
	all_possible_order_list = list(it.permutations(range(1,object_number+1),object_number))
	tree_number_list = range(len(tree_list))
	p_posterior_list = [posteriorTreeGoalOrderFromMotion(policy_sheep,position_alltime_list, tree_number, goal, tree_list, order) for tree_number in tree_number_list for order in all_possible_order_list]
	# print p_posterior_list
	p_posterior = reduce(np.add,p_posterior_list)
	log_p_posterior = np.log(p_posterior)
	return p_posterior,log_p_posterior

def posteriorOrderFromMotion(position_alltime_list,order,tree_list,policy_sheep,goal=1):
	tree_number_list = range(len(tree_list))
	p_posterior_list = [posteriorTreeGoalOrderFromMotion(policy_sheep,position_alltime_list, tree_number, goal, tree_list, order) for tree_number in tree_number_list]
	p_posterior = reduce(np.add,p_posterior_list)
	log_p_posterior = np.log(p_posterior)
	return p_posterior,log_p_posterior


def probabilityGoal(x,*args):
	'''x=[goal]'''
	'''args=((position_alltime_list,tree_list)'''
	position_alltime_list = args[0][0]
	tree_list = args[0][1]
	policy_sheep = args[0][2]
	goal = x
	[p_posterior,log_p_posterior] = posteriorGoalFromMotion(position_alltime_list, goal, tree_list,policy_sheep)
	log_p_x = log_p_posterior
	return log_p_x

def probabilityYOfXGoal(x,y,*args):
	'''x=[old_goal],y=[new_goal]'''
	p_x_to_y = 0.5
	log_p_x_to_y = np.log(p_x_to_y)
	return log_p_x_to_y

def sampleYFromXGoal(x,*args):
	'''x=[old_goal]'''
	new_goal = np.random.binomial(1,0.5)
	y = new_goal
	return y

def probabilityOrder(x,*args):
	position_alltime_list = args[0][0]
	tree_list = args[0][1]
	policy_sheep = args[0][2]
	goal = 1
	order = x
	[p_posterior,log_p_posterior] = posteriorOrderFromMotion(position_alltime_list, order, tree_list,policy_sheep)
	return log_p_posterior

def probabilityYOfXOrder(x,y,*args):
	p_x_to_y = np.divide(np.float(1.0),np.float(len(x)))
	log_p_x_to_y = np.log(p_x_to_y)
	return log_p_x_to_y

def sampleYFromXOrder(x,*args):
	all_possible_order_list = list(it.permutations(range(1,len(x)+1),len(x)))
	p = np.divide(np.float(1.0),np.float(len(all_possible_order_list)))
	sample_list = list(np.random.multinomial(1,[p]*len(all_possible_order_list)))
	y = all_possible_order_list[sample_list.index(1)]
	return y

def mhSample(probabilityX,probabilityYOfX,sampleYFromX,x_initial,sample_time,viz,position_alltime_list,tree_list,policy_sheep):
	x_list = range(sample_time)
	sample_result_list = mh.mhSample(probabilityX, probabilityYOfX, sampleYFromX, x_initial, x_list, sample_time,viz,position_alltime_list,tree_list,policy_sheep)
	return sample_result_list

def mhSampleOnline(probabilityYOfX,sampleYFromX,x_initial,sample_time,viz,position_alltime_list,tree_list,policy_sheep,begin_point=0,window=3,prior_old=0.5):
	def probabilityGoalOnline(x,*args):
		'''x=[goal]'''
		'''args=((position_alltime_list,tree_list)'''
		position_alltime_list = args[0][0]
		tree_list = args[0][1]
		goal = x
		[p_posterior,log_p_posterior] = posteriorGoalFromMotion(position_alltime_list, goal, tree_list,policy_sheep)
		prior_old_list = [1-prior_old,prior_old]
		p_posterior_correct = np.multiply(p_posterior,np.divide(np.float(prior_old_list[x]),0.5))
		log_p_x = np.log(p_posterior_correct)
		return log_p_x
	x_list = range(sample_time)
	sample_result_list = mh.mhSample(probabilityGoalOnline, probabilityYOfX, sampleYFromX, x_initial, x_list, sample_time, viz,position_alltime_list[begin_point:begin_point+window],tree_list,policy_sheep)
	sample_posterior = np.divide(np.float(sample_result_list.count(1)),np.float(len(sample_result_list)))
	prior_new = sample_posterior
	if begin_point==len(position_alltime_list)-window:
		return sample_posterior
	else:
		begin_point = begin_point+1
		return mhSampleOnline(probabilityYOfX, sampleYFromX, x_initial, sample_time, viz, position_alltime_list, tree_list,policy_sheep,begin_point,window,prior_new)

def main():
	tree_list = pickle.load(open("tree_list.pkl","rb"))
	policy_sheep = pickle.load(open("sheep3030_policy.pkl","rb"))
	filename = "masterchase1.xls"
	position_alltime_list = readTrajectory(filename)
	# position_alltime_list = position_alltime_list[10:20]
	goal_initial=0
	x_initial = goal_initial
	order_initial = [1,2,3]
	sample_time = 100
	burn = 0
	sample_result_list = mhSample(probabilityGoal,probabilityYOfXGoal,sampleYFromXGoal,x_initial,sample_time,1,position_alltime_list,tree_list,policy_sheep)
	result_list = sample_result_list[burn:-1]
	counter = [result_list.count(i) for i in result_list]
	most_frequency_result = result_list[counter.index(max(counter))]
	print result_list,most_frequency_result
	# if most_frequency_result==1:
	# 	order_sample_result_list = mhSample(probabilityOrder,probabilityYOfXOrder,sampleYFromXOrder,order_initial,sample_time,0,position_alltime_list,tree_list)
	# 	order_result_list = order_sample_result_list[burn:-1]
	# 	counter = [order_result_list.count(i) for i in order_result_list]
	# 	most_frequency_order = order_result_list[counter.index(max(counter))]
	# 	print order_result_list,most_frequency_order
	# sample_posterior = mhSampleOnline(probabilityYOfXGoal, sampleYFromXGoal, x_initial, sample_time, 1, position_alltime_list, tree_list,policy_sheep)
	# print sample_posterior
	return

if __name__ == '__main__':
	main()