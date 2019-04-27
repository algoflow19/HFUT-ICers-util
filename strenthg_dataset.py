#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 12:05:14 2019

@author: jace
"""

import cv2
import numpy as np
import xml.etree.ElementTree

import argparse
import sys
import os
from os import listdir

EFFECT={'paddle':0,'rotate':1,None:1}
out_width=None
out_height=None


if __name__ == '__main__':
	parser=argparse.ArgumentParser()
	parser.add_argument('img_dir')
	parser.add_argument('xml_dir')
	parser.add_argument('out_img_dir')
	parser.add_argument('out_xml_dir')
	parser.add_argument('--effect',help='default = "rotate", support "rotate" and "resize" operation.')
	parser.add_argument('--width',help='')
	parser.add_argument('--height',help='')
	parser.add_argument('--mode',help='choose do what strenthg to original dataset')
	# '0' for only Horizontal flip, 1 for all directions flip.
	args=parser.parse_args()
	
	effect=EFFECT[args.effect]
	
	if(effect == None):
		print('This script not support '+args.effect+' yet')
		exit()
	if(effect==0):
		out_width=int(args.width)
		out_height=int(args.height)
		if(args.width is None or args.height is None):
			print('paddle image need to specify the width and height of output image')
	if(len(sys.argv)<=5):
		args.mode=1	
	
	if(not os.path.exists(args.out_img_dir)): 
		os.mkdir(args.out_img_dir)
		print('create output images dir:'+os.path.abspath(args.out_img_dir))
	if(not os.path.exists(args.out_xml_dir)): 
		os.mkdir(args.out_xml_dir)
		print('create output xmls dir:'+os.path.abspath(args.out_xml_dir))
	xml_files=[]
	for file in listdir(args.xml_dir):
		if('.xml' in file or '.XML' in file):
			back='.xml'
			if('.XML' in file): back='.XML'
			file=file[:-4]
			if(os.path.exists(os.path.join(args.img_dir,file+'.jpg')) or os.path.exists(os.path.join(args.img_dir,file+'.JPG'))):
				img_back='.JPG'
				if(os.path.exists(os.path.join(args.img_dir,file+'.jpg'))):
					img_back='.jpg'
				tree=xml.etree.ElementTree.parse(os.path.join(args.xml_dir,file+back))
				img=cv2.imread(os.path.join(args.img_dir,file+img_back))
				root=tree.getroot()
				if(effect==0):
					size=root.find('size')
					width=int(size.find('width').text)
					height=int(size.find('height').text)
					if(width>out_width):
						print('Warning detect image width bigger then output width:'+str(width))
					if(height>out_height):
						print('Warning detect image height bigger then output height:'+str(height))
					toFull=np.zeros((max(height,out_height),max(width,out_width),3))+128+127*np.random.rand(max(height,out_height),max(width,out_width),3)
					toFull[0:height,0:width]=img
					cv2.imwrite(os.path.join(args.out_img_dir,file+img_back),toFull)
					size.find('width').text=str(toFull.shape[1])
					size.find('height').text=str(toFull.shape[0])
					tree.write(os.path.join(args.out_xml_dir,file+back))
					print('Done one')
					continue
				
				objs=root.findall('object')
				
				width = int(root.find('size').find('width').text)
				height = int(root.find('size').find('height').text)
				xmin=[]
				xmax=[]
				ymin=[]
				ymax=[]
				for i in range(0,len(objs)):
					obj=objs[i]
					box=obj.find('bndbox')
					xmin.append(int(box.find('xmin').text))
					xmax.append(int(box.find('xmax').text))
					ymin.append(int(box.find('ymin').text))
					ymax.append(int(box.find('ymax').text))
				
				cv2.imwrite(os.path.join(args.out_img_dir,file+'3'+img_back),img)
				tree.write(os.path.join(args.out_xml_dir,file+'3'+back))
				# 0 Vertical
				# 1 Horizontal
				# -1 Simultaneous
				f0=cv2.flip(img,1)
				for i in range(0,len(objs)):
					obj=objs[i]
					box=obj.find('bndbox')
					box.find('xmin').text = str(width-xmax[i])
					box.find('xmax').text = str(width-xmin[i])
					box.find('ymin').text = str(ymin[i])
					box.find('ymax').text = str(ymax[i])
#					cv2.rectangle(f0,(width-xmax[i],ymin[i]),(width-xmin[i],ymax[i]),(255,0,0),1)
				cv2.imwrite(os.path.join(args.out_img_dir,file+'2'+img_back),f0)
				tree.write(os.path.join(args.out_xml_dir,file+'2'+back))
				if(args.mode == 0): continue
				
				f0=cv2.flip(img,-1)
				for i in range(0,len(objs)):
					obj=objs[i]
					box=obj.find('bndbox')
					box.find('xmin').text = str(width-xmax[i])
					box.find('xmax').text = str(width-xmin[i])
					box.find('ymin').text = str(height-ymax[i])
					box.find('ymax').text = str(height-ymin[i])
#					cv2.rectangle(f0,(width-xmax[i],height-ymax[i]),(width-xmin[i],height-ymin[i]),(255,0,0),1)
				cv2.imwrite(os.path.join(args.out_img_dir,file+'0'+img_back),f0)
				tree.write(os.path.join(args.out_xml_dir,file+'0'+back))
				
				f0=cv2.flip(img,0)
				for i in range(0,len(objs)):
					obj=objs[i]
					box=obj.find('bndbox')
					box.find('xmin').text = str(xmin[i])
					box.find('xmax').text = str(xmax[i])
					box.find('ymin').text = str(height-ymax[i])
					box.find('ymax').text = str(height-ymin[i])
					
				cv2.imwrite(os.path.join(args.out_img_dir,file+'1'+img_back),f0)
				tree.write(os.path.join(args.out_xml_dir,file+'1'+back))
			else:
				print('Found xml file:'+file+'.xml, however no image file match it, skip.')
		
			
		
	