#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-06 14:01:57
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np 
import scipy.stats
import matplotlib.pyplot as plt 

def plotValue(data_list,marketype,x_min,x_max,y_min,y_max):
	plt.ion()
	plt.cla()
	plt.axis([x_min,x_max,y_min,y_max])
	x=np.size(data_list,0)
	if len(np.shape(data_list))<2:
		plt.plot(range(x),data_list,marketype)
	else:
		y=[[data_list[i][j] for i in range(np.size(data_list,0))] for j in range(np.size(data_list,1))]
		map(lambda j: plt.plot(range(x),j,marketype),y)
	plt.show()
	plt.pause(0.001)
	return

def plotHistgram(data_list,category_number,x_min,x_max,y_min,y_max):
	'''data_list = 1*length'''
	plt.ion()
	plt.cla()
	plt.axis([x_min,x_max,y_min,y_max])
	plt.hist(data_list,category_number)
	plt.show()
	plt.pause(0.001)
	return

def saveVis(filename):
	plt.savefig(filename)
	return

plt.ion()
t=list()
t=list(np.random.vonmises(1,4,10000))
plt.hist(t,20)
plt.show()
plt.pause(5)
# print max(t),min(t)
# print scipy.stats.vonmises.pdf(0,16),(scipy.stats.vonmises.cdf(0.1,200)-scipy.stats.vonmises.cdf(-0.1,400))
