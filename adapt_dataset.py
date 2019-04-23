#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 19:14:02 2019

@author: jace
"""
import cv2
import numpy as np
import xml.etree.ElementTree
import argparse
import sys
import os
from os import listdir

DEBUG=True

class dumb:
	def __init__(self):
		pass

# Interval Tree Node
class it_node:
	def __init__(self,min,max,m=None,i=None,aug=None):
		"""
		   m: maxium value in the left child tree.
		   i: minium value in the right child tree.
		"""
		self.min=min
		self.max=max
		self.m=m
		self.i=i
		self.aug=aug
		self.right=None
		self.left=None

# Interval Tree
class it_tree:
	def __init__(self,doOverLap=lambda x,y:True):
		"""
		doOverLap: use the function to detemined if the nodes are overlap.
		           It take the aug for two nodes as augment.
		"""
		self.root=None
		self.doOverLap=doOverLap
		
	def __insert__(self,root,min,max,aug):
		if(root.m<max): root.m=max
		if(root.i>min): root.i=min
		if(min< root.min):
			if(not root.left):
				root.left=it_node(min,max,max,min,aug)
			else:
				self.__insert__(root.left,min,max,aug)
		else:
			if(not root.right):
				root.right=it_node(min,max,max,min,aug)
			else:
				self.__insert__(root.right,min,max,aug)
	
	def insert(self,min,max,aug=None):
		if(self.root is None):
			self.root=it_node(min,max,max,min,aug)
		else:
			self.__insert__(self.root,min,max,aug)
		return False				
	def overLapSearch(self,min,max,aug=None):
		return self.__overLapSearch__(self.root,min,max,aug)
	
	def __overLapSearch__(self,root,min,max,aug):
		if(root.max>=min and root.min <= max):
			if(self.doOverLap(root.aug,aug)): return root
		tmp=None
		if(root.left and root.left.m >= min):
			tmp=self.__overLapSearch__(root.left,min,max,aug)
		if(tmp): return tmp
		if(root.right and root.right.i<=max):
			tmp=self.__overLapSearch__(root.right,min,max,aug)
		return tmp


# Tests for it_Tree implement.
#tree=it_tree()
#tree.insert(15,20)
#assert(tree.overLapSearch(19,25))
#assert(not tree.overLapSearch(21,25))
#tree.insert(21,23)
#assert(tree.overLapSearch(22,25))
#assert(not tree.overLapSearch(24,25))
#assert(not tree.overLapSearch(11,14))
#assert(tree.overLapSearch(16,19))
#assert(tree.overLapSearch(16,25))
#tree.insert(5,12)
#tree.insert(1,2)
#assert(tree.overLapSearch(0,1))
#assert(not tree.overLapSearch(3,4))
#assert(not tree.overLapSearch(13,14))
#assert(tree.overLapSearch(6,7))
#assert(tree.overLapSearch(3,6))
#assert(tree.overLapSearch(11,14))
#assert(tree.overLapSearch(-1,1))
#assert(not tree.overLapSearch(-1,0))
#assert(not tree.overLapSearch(24,28))
#assert(tree.overLapSearch(-3,29))
#exit()



IMAGE_WIDTH=1440
IMAGE_HEIGHT=900
OUT_IMAGE_WIDTH=640
OUT_IMAGE_HEIGHT=360
TO_REMOVE=['folder','path','source','pose','truncated','difficult']
ISLAPFUN=lambda a,b: a[0]<=b[1] and a[1]>=b[0]

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('img_dir', help='source dir for xml files')
	parser.add_argument('xml_dir', help='source dir for images')
	parser.add_argument('out_img_dir',help='output dir for output the output images')
	parser.add_argument('out_xml_dir',help='output dir for the xml files')
	parser.add_argument('--auto_fix', help='allowed varity size of images to be process')
	parser.add_argument('--allow_mulobj', help='allowed multilue objects image to be sampled')
	parser.add_argument('--allow_bang', help='allowed bondboxs bang image to be sampled')
	parser.add_help=True
	
	if(DEBUG and len(sys.argv) < 5):
		args=dumb()
		args.img_dir='JPEGImages'
		args.xml_dir='Annotations'
		args.out_img_dir='out_images'
		args.out_xml_dir='out_xmls'
		args.auto_fix=False
		args.allow_mulobj=True
	else:
		args = parser.parse_args()
	
	source_images=[]
	source_xmls=[]
	for file in listdir(args.img_dir):
		if('.jpg' in file):
			source_images.append(file)
	for file in listdir(args.xml_dir):
		if('.xml' in file):
			source_xmls.append(file)
	if(not os.path.exists(args.out_img_dir)): 
		os.mkdir(args.out_img_dir)
		print('create output images dir:'+os.path.abspath(args.out_img_dir))
	if(not os.path.exists(args.out_xml_dir)): 
		os.mkdir(args.out_xml_dir)
		print('create output xmls dir:'+os.path.abspath(args.out_xml_dir))
	print('This program will use xml files as clues to match the images')
	for xml_file in source_xmls:
		xml_tree = xml.etree.ElementTree.parse(os.path.join(args.xml_dir,xml_file))
		size=xml_tree.find('size')
		if( not args.auto_fix and not size.find('width').text == str(IMAGE_WIDTH) or not size.find('height').text == str(IMAGE_HEIGHT)):
			print('Found image with wrong size:' + xml_tree.find('filename').text)
			exit(-1)
		else: pass
		image_name=xml_tree.find('filename').text
		image=None
		if('.jpg' not in (image_name).lower()): # Bug Shot.
			image_name+='.jpg'
		if(not os.path.exists(os.path.join(args.img_dir,image_name))):
			print('Warnning: xml for '+os.path.join(args.img_dir,image_name)+' exists but not the image')
			continue
	
		objs=xml_tree.getroot().findall('object')
		
		if(len(objs) <= 0):
			print('Error xml file format. No object tag in it')
			exit()
		elif(len(objs) >1 and not args.allow_mulobj):
			print('Find mul objets in '+ xml_file +', jump to next image.')
			continue
		else:
			xmin=[]
			xmax=[]
			ymin=[]
			ymax=[]
			for attr in TO_REMOVE:
				tmp=xml_tree.find(attr)
				if(tmp): xml_tree.remove(tmp)
			left_objs={}
			for i in range(0,len(objs)):
				obj=objs[i]
				box=obj.find('bndbox')
				if(box is not None):
					xmin.append(int(box.find('xmin').text))
					xmax.append(int(box.find('xmax').text))
					ymin.append(int(box.find('ymin').text))
					ymax.append(int(box.find('ymax').text))
				else: continue
				# use a Interval Tree to slove the problem in O( n*log(n) )
				tree=it_tree(ISLAPFUN)
				left_objs[obj]=True
				another=tree.overLapSearch(xmin[i],xmax[i],(ymin[i],ymax[i]))
				if(another):
					left_objs[another]=False
					left_objs[obj]=False
					print('Throw bang objects')
				tree.insert(xmin[i],xmax[i],(ymin[i],ymax[i]))
			for index in range(0,objs):
				if(left_objs[objs[index]]):
					o_xmin=xmin[i]
					o_xmax=xmax[i]
					o_ymin=ymin[i]
					o_ymax=ymax[i]
					
				
		exit()
		
			
	exit(1)
	if args.gpu:
		os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu

	print(str(args.dump2_train1_test0))

	if args.dump2_train1_test0 == '1':
		if args.data == None:
			print('Provide DAC dataset path with --data')
			sys.exit()

		config = get_config()
		if args.model:
			config.session_init = SaverRestore(args.model)

		SimpleTrainer(config).train()

	elif args.dump2_train1_test0 == '0':
		if args.run == None:
			print('Provide images with --run ')
			sys.exit()
		if args.weights == None:
			print('Provide weights file (.npy) for testing!')
			sys.exit()

		assert args.weights.endswith('.npy')
		run_image(Model(), DictRestore(np.load(args.weights, encoding='latin1').item()), args.run)

	elif args.dump2_train1_test0 == '2':
		if args.meta == None:
			print('Provide meta file (.meta) for dumping')
			sys.exit()
		if args.model == None:
			print('Provide model file (.data-00000-of-00001) for dumping')
			sys.exit()

		dump_weights(args.meta, args.model, args.output)

	elif args.dump2_train1_test0 == '3':
		if args.run == None:
			print('Provide image with --run ')
			sys.exit()
		if args.weights == None:
			print('Provide weights file (.npy) for testing!')
			sys.exit()

		assert args.weights.endswith('.npy')
		run_single_image(Model(), DictRestore(np.load(args.weights, encoding='latin1').item()), args.run)