#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-18 12:03:50
# @Author  : xuhaokui (haokuixu.psy@gmail.com)
# @Link    : ${link}
# @Version : $Id$

import numpy as np
import os

meragefiledir = os.getcwd()+'/results'
filenames=os.listdir(meragefiledir)  

CDfile=open('CD_result.txt','w')
CSfile=open('CS_result.txt','w')
CZfile=open('CZ_result.txt','w')

for filename in filenames:
	filepath=meragefiledir+'/'
	filepath=filepath+filename 
	if 'CD' in filename:
		file = CDfile
	elif 'CS' in filename:
		file = CSfile
	elif 'CZ' in filename:
		file = CZfile
	for line in open(filepath):
		file.writelines(line)
	# file.write('\n')
CDfile.close()
CSfile.close()
CZfile.close()
