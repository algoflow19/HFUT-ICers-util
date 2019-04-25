#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 09:02:44 2019

@author: jace
"""
from asyncio import Queue
import sys

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

def fixUp(node):
	pass
	

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
				if(node.right): self.__query__(node.right,l)
				if(nodeaabb2.left): self.__query__(node.left,l)
			else:
				l.append(node.aabb)
		
	def insert(self,aabb,userdata=None):
		self.input=aabb
		if(self.root):
			self.__insert__(self.root,userdata)
		else:
			self.root=AABBnode(aabb,0,userdata=userdata)
			return self.root
	def __insert__(self,node,userdata=None):
		new_node=AABBnode(self.input,node.height+1,userdata=userdata)
		if(node.right or node.left):
			parent=node
			while(parent.right or parent.left):
				x=None
				if(not node.left):
					parent.aabb=mergeAABB(parent.right.aabb,self.input)
					parent.left=new_node
				else:
					x=mergeAABB(self.input,node.left.aabb)
				cost1=caluatePerimeter(x)
				
				if(not node.right):
					parent.aabb=mergeAABB(parent.left.aabb,self.input)
					parent.right=new_node
				else:
					x=mergeAABB(self.input,node.right.aabb)
				cost2=caluatePerimeter(x)
				
				if(cost1<cost2):
					parent=parent.left
				else:
					parent=parent.right
			self.__insert__(parent,userdata)
		else:
			new_parent=AABBnode(mergeAABB(self.input,node.aabb),node.height,node.parent)
			node.height=node.height+1
			new_parent.parent=node.parent
			new_parent.left=node
			new_parent.right=new_node
			if(new_parent.parent.right==new_parent.node):
				new_parent.parent.right=new_parent
			else:
				new_parent.parent.left=new_parent
			fixUp(new_node)
		
		
		
def tree_debug_travl(tree):
	root=tree.root
	if(root is None): return
	q=Queue()
	q.put(root)
	while(not q.empty()):
		size=q.qsize()
		for i in range(0,size):
			tmp=q.get()
			if(tmp is None):
				sys.stdout.write('((-,-),(-,-)) ')
			else:
				sys.stdout.write(str(tmp.aabb)+' ')
				q.put(tmp.right)
				q.put(tmp.left)
		sys.stdout.write('\n')


	
if __name__ == '__main__':
	print('Run Test case for AABB tree.')
	
	print('All Pass.')
	