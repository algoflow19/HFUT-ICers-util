#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 19:14:02 2019

@author: jace
"""
import cv2
import numpy as np
import xml.etree.ElementTree as ET
import argparse
import sys
import os
from os import listdir
from AABBTree import AABBtree
from AABBTree import doOverLap
from AABBTree import anyOverLapMuch

DEBUG=True

class dumb(object):
	def __init__(self):
		pass

# Interval Tree Node
class it_node(object):
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
class it_tree(object):
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
OUT_WIDTH=640
OUT_HEIGHT=360

# TO_REMOVE=['folder','path','source','pose','truncated','difficult']
ISLAPFUN=lambda a,b: a.ymin<=b.ymax and a.ymax>=b.ymin

def emliateInterval(toe,l):
	index=0
	while(index<len(l)):
		if(toe[0]<l[index][0]):
			while(index<len(l)):
				if(toe[1]<l[index][0]): return
				if(toe[1]<l[index][1]):
					l[index][0]=toe[1]+1
					return
				del(l[index])
		elif(toe[0]<l[index][1]):
			if(toe[1]<l[index][1]):
				tmp=l[index][1]
				l[index][1]=toe[0]-1
				if(l[index][1]<l[index][0]):
					del(l[index])
					l.insert(index,[toe[1]+1,tmp])
				else:
					l.insert(index+1,[toe[1]+1,tmp])
				return
			l[index][1]=toe[0]-1
			if(l[index][0]>l[index][1]):
				del(l[index])
			else:
				index+=1
			while(index<len(l)):
				if(toe[1]<l[index][0]): return
				if(toe[1]<l[index][1]):
					l[index][0]=toe[1]+1
					return
				else: del(l[index])
		elif(toe[0]==l[index][1]):
			l[index][1]-=1
			if(l[index][0]>l[index][1]):
				del(l[index])
				index-=1
		index+=1


# Test for emliateInterval
#l=[[1,10]]
#emliateInterval([3,5],l)
#assert(len(l)==2)
#assert(l== [[1,2],[6,10]])
#emliateInterval((2,7),l)
#assert(len(l)==2)
#assert(l==[[1,1],[8,10]])
#emliateInterval((8,10),l)
#assert(l==[[1, 1]])
#emliateInterval((0,10),l)
#assert(l==[])
#l=[[1,10]]
#emliateInterval((1,3),l)
#emliateInterval((7,10),l)
#assert(l==[[4,6]])
#l=[[1,2],[4,5],[7,8],[9,14]]
#emliateInterval((1,8),l)
#assert(len(l)==1)
#l=[[1,2],[4,5],[7,8],[9,14]]
#emliateInterval((1,7),l)
#assert(len(l)==2)
#emliateInterval((8,9),l)
#assert(l==[[10,14]])
#l=[[1,2],[4,5],[7,8],[9,14]]
#emliateInterval((2,13),l)
#assert(l==[[1,1],[14,14]])
#emliateInterval( (-12,22),l)
#assert(len(l)==0)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('img_dir', help='source dir for xml files')
	parser.add_argument('xml_dir', help='source dir for images')
	parser.add_argument('out_img_dir',help='output dir for output the output images')
	parser.add_argument('out_xml_dir',help='output dir for the xml files')
	parser.add_argument('--auto_fix', help='allowed varity size of images to be process',default=None)
	parser.add_argument('--allow_mulobj', help='allowed multilue objects image to be sampled',default='True')
	parser.add_argument('--allow_bang', help='allowed bondboxs bang image to be sampled',default=None)
	parser.add_help=True
	parser.description="This Tool is used to corp multiple objects in one image.\
						It will produce images with single object."
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
	
	source_xmls=[]
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
		xml_tree = ET.parse(os.path.join(args.xml_dir,xml_file))
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
			exit(-2)
		elif(len(objs) >1 and not args.allow_mulobj):
			print('Find mul objets in '+ xml_file +', jump to next image.')
			continue
		else:
			# Using a AABB tree for detect collsion.
			AB_tree=AABBtree()
			xmin=[]
			ymin=[]
			xmax=[]
			ymax=[]
			
			crop_pos=[] # size param in output xml.
			bond_pos=[] # bondbox param in output xml
			names=[] # name param in output xml
			
			for i in range(0,len(objs)):
				bndbox = objs[i].find('bndbox')
				xmin.append(int(bndbox.find('xmin').text))
				ymin.append(int(bndbox.find('ymin').text))
				xmax.append(int(bndbox.find('xmax').text))
				ymax.append(int(bndbox.find('ymax').text))
				AB_tree.insert(((xmin[-1],ymin[-1]),(xmax[-1],ymax[-1])),objs[i])
			AB_tree.insert( ((0,-1),(IMAGE_WIDTH,0)) )
			AB_tree.insert( ((-1,0),(0,IMAGE_HEIGHT)) )
			AB_tree.insert(((IMAGE_WIDTH,0),(IMAGE_WIDTH+1,IMAGE_HEIGHT)))
			AB_tree.insert(((0,IMAGE_HEIGHT),(IMAGE_WIDTH,IMAGE_HEIGHT+1)))
			for i in range(0,len(objs)):
				if(ymax[i]-ymin[i]>OUT_HEIGHT or xmax[i]-xmin[i]>OUT_WIDTH):
					print("Object size is bigger than output size, skip...")
					continue
				if(len(AB_tree.query(((xmin[-1],ymin[-1]),(xmax[-1],ymax[-1])))) > 1):
					continue
				box_xmin=xmax[i]-OUT_WIDTH
				box_ymin=ymax[i]-OUT_HEIGHT
				box_xmax=xmin[i]+OUT_WIDTH
				box_ymax=ymin[i]+OUT_HEIGHT
				collsion=AB_tree.query(((box_xmin,box_ymin),(box_xmax,box_ymax)),True)
				# Assume that it return the AABB list.
				marker=[[[0,xmin[i]-box_xmin]]*(ymin[i]-box_ymin)]
				for aabb in collsion:
					if(aabb == ((xmin[i],ymin[i]),(xmax[i],ymax[i]))):
						continue
					if( doOverLap(aabb,((xmin[i],ymax[i]),(xmax[i],box_ymax)))): # Top
						length=min(box_ymax-aabb[0][1],len(marker))
						for tmp in range(len(marker)-length,len(marker)):  # ymin=aabb[0][1]
							marker[tmp]=None
						continue
					if( doOverLap(aabb,((xmin[i],box_ymin),(xmax[i],ymin[i]))) ): # Bottom
						length=min(len(marker),aabb[1][1]-box_ymin)
						for tmp in range(0,length): # ymax=aabb[1][1]
							marker[tmp]=None
						continue
					if(doOverLap(aabb,((box_xmin,ymin[i]),(xmin[i],ymax[i])))): # Left
						length=aabb[1][0]-box_xmin
						for tmp in range(0,len(marker)): #xmax=aabb[1][0]
							if(marker[tmp] is None): continue
							emliateInterval( (0,length),marker[tmp])
							if(len(marker[tmp])==0):
								marker[tmp]=None
						continue ##Correct Above.
					if(doOverLap(aabb,((xmax[i],ymin[i]),(box_xmax,ymax[i]))) ): # Right
						length=max(0,aabb[0][0]-xmax[i])
						for tmp in range(0,len(marker)):
							if(marker[tmp] is None): continue
							emliateInterval((length,xmin[i]-box_xmin),marker[tmp])
							if(len(marker[tmp])==0):
								marker[tmp]=None
						continue
					if(doOverLap(aabb,((box_xmin,ymax[i]),(xmin[i],box_ymax)) ) ): # top left
						length=max(0,aabb[0][1]-ymax[i])
						for tmp in range(length,len(marker)):
							if(marker[tmp] is None): continue
							emliateInterval((0,min(xmin[i]-box_xmin,aabb[1][0]-box_xmin)),marker[tmp])
							if(len(marker[tmp])==0):
								marker[tmp]=None
						continue
					if(doOverLap(aabb,((xmax[i],box_ymin),(box_xmax,ymin[i])))): #bottom right
						length=min(len(marker),aabb[1][1]-box_ymin)
						for tmp in range(0,length):
							if(marker[tmp] is None): continue
							emliateInterval((max(0,aabb[0][0]-xmax[i]),xmin[i]-box_xmin),marker[tmp])
							if(len(marker[tmp])==0):
								marker[tmp]=None
						continue
					if(doOverLap(aabb,((box_xmin,box_ymin),(xmin[i],ymin[i])) ) ): # bottom left
						length=min(aabb[1][1]-box_ymin,len(marker))
						for tmp in range(0,length):
							if(marker[tmp] is None): continue
							emliateInterval( (0,min(aabb[1][0]-box_xmin,xmin[i]-box_xmin)),marker[tmp])
							if(len(marker[tmp])==0):
								marker[tmp]=None
					if(doOverLap(aabb,((xmax[i],ymax[i]),(box_xmax,box_ymax)))): # top right
						length=max(0,aabb[0][1]-ymax[i])
						for tmp in range(length,len(marker)):
							if(marker[tmp] is None): continue
							emliateInterval( (max(0,aabb[0][0]-xmax[i]),xmin[i]-box_xmin),marker[tmp])
							if(len(marker[tmp])==0):
								marker[tmp]=None
						continue
				corp_xmin=None
				corp_ymin=None
				corp_xmax=None
				corp_ymax=None
				kill_x=[]
#				if(i==3):
#					print(np.array(marker))
#					print(len(marker))
				for x in range(1,len(marker)-1):
					if(marker[x] is not None):
						kill_x.append(x)
				if(kill_x):
					x=kill_x[len(kill_x)//2]
					corp_ymin=x+box_ymin
					corp_xmin=int(np.average(marker[x][len(marker[x])//2])+box_xmin)
				if(corp_ymin):
					corp_xmax=corp_xmin+OUT_WIDTH
					corp_ymax=corp_ymin+OUT_HEIGHT
				else:
					corp_xmin=max(0,xmin[i]-5)
					corp_ymin=max(0,ymin[i]-5)
					corp_xmax=min(box_xmax,xmax[i]+5)
					corp_ymax=min(box_ymax,ymax[i]+5)
					collsion=AB_tree.query(((corp_xmin,corp_ymin),(corp_xmax,corp_ymax)),True)
					collsion.remove( ((xmin[i],ymin[i]),(xmax[i],ymax[i])) )
					if(len(collsion)>1 and anyOverLapMuch(((corp_xmin,corp_ymin),(corp_xmax,corp_ymax)),collsion)):
						print("In XML file:"+xml_file+", object:"+objs[i].find('name').text+"("+str(i)+"), is bang clash with other object, so we stop.")
						print("Maybe we can figure out a way to handle it smarter later.")
						continue
					while(True):
						to_move=min(50,OUT_WIDTH-(corp_xmax-corp_xmin),corp_xmin)
						aabb=((corp_xmin-to_move,corp_ymin),(corp_xmin,corp_ymax))
						if( to_move>0 and not anyOverLapMuch(aabb,AB_tree.query(aabb,True),0.15)):
							corp_xmin-=to_move
						else: break
					while(True):
						to_move=min(50,OUT_WIDTH-(corp_xmax-corp_xmin),IMAGE_WIDTH-corp_xmax)
						aabb=((corp_xmax,corp_ymin),(corp_xmax+to_move,corp_ymax))
						if( to_move>0 and not anyOverLapMuch(aabb,AB_tree.query(aabb,True),0.15)):
							corp_xmax+=to_move
						else: break
					while(True):
						to_move=min(50,OUT_HEIGHT-(corp_ymax-corp_ymin),corp_ymin)
						aabb=((corp_xmin,corp_ymin-to_move),(corp_xmax,corp_ymin))
						if( to_move>0 and not anyOverLapMuch(aabb,AB_tree.query(aabb,True),0.15)):
							corp_ymin-=to_move
						else: break
					while(True):
						to_move=min(50,OUT_HEIGHT-(corp_ymax-corp_ymin),IMAGE_HEIGHT-corp_ymax)
						aabb=((corp_xmin,corp_ymax),(corp_xmax,corp_ymax+to_move))
						if( to_move>0 and not anyOverLapMuch(aabb,AB_tree.query(aabb,True),0.15)):
							corp_ymax+=to_move
						else: break
					
				root=xml_tree				
				annotation = ET.Element('annotation')
				tmp=ET.SubElement(annotation,'filename')
				size=ET.SubElement(annotation,'size')
				tmp.text=image_name[:-4]
				tmp=ET.SubElement(size,'width')
				tmp.text=str(corp_xmax-corp_xmin)
				tmp=ET.SubElement(size,'height')
				tmp.text=str(corp_ymax-corp_ymin)
				Object=ET.SubElement(annotation,'object')
				name = ET.SubElement(Object,'name')
				name.text=objs[i].find('name').text
				bndbox= ET.SubElement(Object,'bndbox')
				x_xmin=ET.SubElement(bndbox,'xmin')
				x_ymin=ET.SubElement(bndbox,'ymin')
				x_xmax=ET.SubElement(bndbox,'xmax')
				x_ymax=ET.SubElement(bndbox,'ymax')
				x_xmin.text=str(xmin[i]-corp_xmin)
				x_xmax.text=str(xmax[i]-corp_xmin)
				x_ymin.text=str(ymin[i]-corp_ymin)
				x_ymax.text=str(ymax[i]-corp_ymin)
				tmp_tree=ET.ElementTree(annotation)
				tmp_tree.write(os.path.join(args.out_xml_dir,str(i)+xml_file))
				img=cv2.imread(os.path.join(args.img_dir,image_name))
#				cv2.rectangle(img,(corp_xmin,corp_ymin),(corp_xmax,corp_ymax),1)
#				cv2.imwrite(str(i)+image_name,img)
				cv2.rectangle(img,(xmin[i],ymin[i]),(xmax[i],ymax[i]),2)
				cv2.imwrite(os.path.join(args.out_img_dir,str(i)+image_name),
				img[corp_ymin:corp_ymax,corp_xmin:corp_xmax])
				