#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-04 13:42:52
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np
import scipy.stats
import Visualization
import sys   
sys.setrecursionlimit(1000000)

def covNormal(size):
	cov=list()
	for i in range(size):
		cov_line = list()
		for j in range(size):
			if i==j:
				cov_line.append(1)
			else:
				cov_line.append(0)
		cov.append(cov_line)
	return cov

def probabilityX(x,*args):
	'''x=[x1,x2]'''
	p_x = scipy.stats.multivariate_normal.pdf(x[0],5,1)*scipy.stats.multivariate_normal.pdf(x[1],2,0.01)
	log_p_x = np.log(p_x)
	return log_p_x

def probabilityYOfX(x,y,*args):
	p_x_to_y = scipy.stats.multivariate_normal.pdf(y,x,1)
	log_p_x_to_y = np.log(p_x_to_y)
	return log_p_x_to_y

def sampleYFromX(x,*args):
	# y = np.random.normal(x,1)
	y=list(np.random.multivariate_normal(x,covNormal(len(x))))
	return y

def computeAlpha(probabilityX,probabilityYOfX,x_old,x_new,*args):
	args=args[0]
	alpha_1 = np.add(probabilityX(x_new,args),probabilityYOfX(x_new,x_old,args))
	alpha_2 = np.add(probabilityX(x_old,args),probabilityYOfX(x_old,x_new,args))
	# print probabilityX(x_new,args),probabilityYOfX(x_new,x_old,args),probabilityX(x_old,args),probabilityYOfX(x_old,x_new,args)
	if alpha_1-alpha_2==0:
		alpha = 0
	else:
		alpha = np.min([alpha_1-alpha_2,0])
	return alpha

def mhSample(probabilityX,probabilityYOfX,sampleYFromX,x_initial,x_list,sample_time,viz,*args):
	'''initial: x_list = range(sample_time)'''
	if len(args)==1:
		args=args[0]
	x_old = x_initial
	x_new = sampleYFromX(x_old,args)
	alpha = computeAlpha(probabilityX, probabilityYOfX, x_old, x_new,args)
	if np.log(np.random.uniform(0,1))<alpha:
		received_x_new = x_new
	else:
		received_x_new = x_old
	x_list[-sample_time] = received_x_new
	sample_time = sample_time-1
	print sample_time,np.exp(alpha),received_x_new,x_new,x_old
	if viz==1:
		# Visualization.plotValue(x_list[:-sample_time],'', 0, np.size(x_list,0), 0, 11)
		# visual_list = np.sum(np.array(x_list[:-sample_time])*np.array([[1,20]]*len(x_list[:-sample_time])),1)
		Visualization.plotHistgram(x_list[:-sample_time],10,-1,2,0,100)
	if sample_time == 1:
		if viz==1:
			Visualization.saveVis('masterchasing_hist.png')
		return x_list
	else:
		return mhSample(probabilityX,probabilityYOfX,sampleYFromX,x_list[-sample_time-1],x_list,sample_time,viz,args)

def main():
	x_initial = [0,0]
	sample_time = 1000
	x_list = range(sample_time)
	sample_result_list = mhSample(probabilityX,probabilityYOfX,sampleYFromX,x_initial, x_list, sample_time,1)
	burn = 0
	print np.mean(sample_result_list[burn:],0), np.cov(sample_result_list[burn:])
	return

if __name__ == '__main__':
	main()
