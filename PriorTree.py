#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-05 13:51:11
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np
import scipy.stats
import pickle

def softFactorial(n):
	return np.math.factorial(n-1)

def probabilityCRP(partial_list):
	'''eg.: partial_list = [[1,2,3],[4,5],[6],[7,8]]'''
	length_list = map(len,partial_list)
	total_length = np.sum(length_list)
	factorial_list = map(softFactorial,length_list)
	molecule = np.float(reduce(np.multiply,factorial_list))
	denominator = np.float(np.math.factorial(total_length))
	p = np.divide(molecule,denominator)
	return p

def probabilityLevel(current_level_list,next_level_list,p=1):
	next_level_guest_list = next_level_list[0][:]
	for i in range(len(current_level_list[1])):
		if current_level_list[1][i]==0:
			p_node=1
		else:
			index_start=np.int(np.sum(current_level_list[1][0:i]))
			partial_list=next_level_guest_list[index_start:index_start+current_level_list[1][i]]
			p_node=probabilityCRP(partial_list)
		p=p*p_node
	return p

def priorTree(tree_number,tree_list,current_level=0,p_tree=1):
	tree_dict = tree_list[tree_number]
	current_level_list = tree_dict[current_level]
	next_level_list = tree_dict[current_level+1]
	p = probabilityLevel(current_level_list, next_level_list)
	p_tree = p*p_tree
	if current_level==(max(tree_dict.keys())-1):
		return p_tree
	else:
		current_level=current_level+1
		return priorTree(tree_number,tree_list,current_level,p_tree)

def priorTreeRenormalize(tree_number,tree_list):
	p_tree_list = [priorTree(i,tree_list) for i in range(len(tree_list))]
	p_tree = priorTree(tree_number,tree_list)
	p_tree_renormalize = np.divide(p_tree,np.sum(p_tree_list))
	return p_tree_renormalize

def main():
	tree_list = pickle.load(open("tree_list.pkl","rb"))
	tree_number = 1
	p_tree_list = [priorTree(i, tree_list) for i in range(len(tree_list))]
	p_tree_renormalize = priorTreeRenormalize(tree_number, tree_list)
	print p_tree_list,np.sum(p_tree_list),p_tree_renormalize
	return

if __name__ == '__main__':
	main()