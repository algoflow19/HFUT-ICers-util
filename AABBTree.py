#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 09:02:44 2019

@author: jace
"""
from asyncio import Queue
import sys
import copy

def mergeAABB(aabb1,aabb2):
	if(aabb1 is None):
		return aabb2
	if(aabb2 is None):
		return aabb2
	return ((min(aabb1[0][0],aabb2[0][0]),min(aabb1[0][1],aabb2[0][1])),
		 (max(aabb1[1][0],aabb2[1][0]),max(aabb1[1][1],aabb2[1][1])))

def caluatePerimeter(aabb):
	if(aabb is None):
		raise ValueError("Expect AABBNode, get None type.")
	return aabb[1][0]-aabb[0][0]+aabb[1][1]-aabb[0][1]

class AABBnode(object):
	def __init__(self,aabb,height,parent=None,userdata=None):
		self.aabb=aabb
		self.userdata=userdata
		self.parent=parent
		self.height=height
		self.left=None
		self.right=None


def doOverLap(aabb1,aabb2):
	return aabb1[0][0]<aabb2[1][0] and aabb1[0][1]<aabb2[1][1] and aabb1[1][0]>aabb2[0][0] and aabb1[1][1]>aabb2[0][1]

def anyOverLapMuch(aabb,collsion,perctent=0.15):
	for i in collsion:
		if(i==aabb): continue
		x = (min(i[1][0],aabb[1][0])-max(i[0][0],aabb[0][0]))* \
			 ( min(i[1][1],aabb[1][1])-max(i[0][1],aabb[0][1]) )/ \
			 ((i[1][0]-i[0][0])*(i[1][1]-i[0][1]))
		print(x)
		if( x > perctent): return True
	return False



def fixUp(node):
	if(node is None): return
	assert(node.right or node.left)
	node.aabb=mergeAABB(node.right.aabb,node.left.aabb)
	fixUp(node.parent)


class AABBtree(object):
	def __init__(self):
		self.root=None
		self.input=None

	def query(self,aabb,getAABB=False):
		result=[]
		self.input=aabb
		if(getAABB):
			self.__queryAABB__(self.root,result)
		else:
			self.__query__(self.root,result)
		return result

	def __query__(self,node,l):
		if(node == None): return
		if(doOverLap(self.input,node.aabb)):
			if(node.right or node.left):
				if(node.right): self.__query__(node.right,l)
				if(node.left): self.__query__(node.left,l)
			else:
				l.append(node.userdata)


	def __queryAABB__(self,node,l):
		if(node == None): return
		if(doOverLap(self.input,node.aabb)):
			if(node.right or node.left):
				if(node.right): self.__queryAABB__(node.right,l)
				if(node.left): self.__queryAABB__(node.left,l)
			else:
				l.append(node.aabb)

	def insert(self,aabb,userdata=None):
		self.input=aabb
		if(self.root):
			self.__insert__(self.root,userdata)
		else:
			self.root=AABBnode(aabb,0,userdata=userdata)

	def __insert__(self,node,userdata=None):
		new_node=AABBnode(self.input,node.height+1,userdata=userdata)

		if(node.right or node.left):
			parent=node
			while(parent.right or parent.left):
				x=None
				if(not node.left):
					parent.aabb=mergeAABB(parent.right.aabb,self.input)
					parent.left=new_node
					new_node.parent=parent
					fixUp(parent)
					return
				else:
					x=mergeAABB(self.input,node.left.aabb)
				cost1=caluatePerimeter(x)
				if(not node.right):
					parent.aabb=mergeAABB(parent.left.aabb,self.input)
					parent.right=new_node
					new_node.parent=parent
					fixUp(parent)
					return
				else:
					x=mergeAABB(self.input,node.right.aabb)
				cost2=caluatePerimeter(x)

				if(cost1<cost2):
					parent=parent.left
				else:
					parent=parent.right

			self.__insert__(parent,userdata)
		else:
			node.right=copy.deepcopy(node)
			node.left=new_node
			node.right.parent=node
			node.left.parent=node
			node.aabb=mergeAABB(self.input,node.aabb)
			node.userdata=None
			node.right.height=node.height+1
			node.left.height=node.height+1
			assert(node.parent is not node)
			fixUp(node.parent)



def tree_debug_travl(tree):
	root=tree.root
	print('Done')
	if(root is None):
		return
	q=Queue()
	q.put_nowait(root)
	assert(q.qsize() != 0)
	while(not q.empty()):
		size=q.qsize()
		for i in range(0,size):
			tmp=q.get_nowait()
			if(tmp is None):
				sys.stdout.write('((-,-),(-,-)) ')
			else:
				sys.stdout.write(str(tmp.aabb)+' ')
				q.put_nowait(tmp.right)
				q.put_nowait(tmp.left)
		sys.stdout.write('\n')



if __name__ == '__main__':
	print('Run Test case for AABB tree.')
	tree=AABBtree()
	aabb1 = [(154, 673), (976, 745)]
	aabb2 = [(1003, 212), (1092,  688)]
	aabb3 = [(1126, 184), (1230, 569)]
	aabb4 = [(197, 250), (509, 355)]
#	aabb5 = ([(-1, 3), (12, 4)])
	tree.insert(aabb1)
	tree.insert(aabb2)
	tree.insert(aabb3)
	tree.insert(aabb4)
	aabbx=((149,436),(967,562))
	assert(not tree.query(aabbx,True))
	aabbx=((1186,530),(1277,598))
	assert(tree.query(aabbx,True)==[aabb3])
	aabbx=((882,308),(1399,389))
	assert(len(tree.query(aabbx,True))==2)
	aabbx=((268,431),(1398,843))
	assert(len(tree.query(aabbx,True))==3)
	aabbx=((258,190),(332,864))
	assert(len(tree.query(aabbx,True))==2)
	aabbx=((397,302),(1207,741))
	assert(len(tree.query(aabbx,True))==4)
	aabbx=((894,494),(1198,721))
	assert(len(tree.query(aabbx,True))==3)
	aabbx=((683,188),(827,359))
	assert(not tree.query(aabbx,True))
	aabbx=((1336,463),(1507,734))
	assert(not tree.query(aabbx,True))
	aabbx=((16,650),(133,799))
	assert(not tree.query(aabbx,True))
	aabbx=((504,832),(804,936))
	assert(not tree.query(aabbx,True))
	aabbx=((1104,479),(1111,665))
	assert(not tree.query(aabbx,True))
	aabbx=((1322,809),(1676,910))
	tree.insert(aabbx)
	aabbx=((1336,463),(1507,734))
	assert(not tree.query(aabbx,True))
	aabbx=((16,650),(133,799))
	assert(not tree.query(aabbx,True))
	aabbx=((504,832),(804,936))
	assert(not tree.query(aabbx,True))
	aabbx=((1104,479),(1111,665))
	assert(not tree.query(aabbx,True))
#	tree_debug_travl(tree)
	print('All Pass.')
#Test for anyOverLapMuch

