#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  xml_parser.py
#  
#  Copyright 2012 Clean ubuntu 11.10 <ptr@ubuntu>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
from xml.dom.minidom import parse
from elementtree.ElementTree import ElementTree, Element, SubElement, dump
import sys


class XML_Interaction:
	tree = ElementTree(file="./status/tasks.xml")
	solrFolder = "home/ubuntu/status/solrdata"
	topicFolder = "home/ubuntu/status/topicdata"
	
	def update_task(self, taskid, status):
		tasks = self.tree.findall("task")

		for task in tasks:			
			children = task.getchildren()
			for child in children:
				if child.tag == "status":
					print "setting new status to " + str(status)
					child.text = str(status)
		self.tree.write("outfile.xml")					
	
	
	def check_task( self ):
		tasks = self.tree.findall("task")
		for task in tasks:			
			children = task.getchildren()
			for child in children:
				if child.tag == "status":
					return child.text
					
	def add_task( self, taskid, tasktype, folder=None ):
		if tasktype == "processSolr":
			if folder == None:
				folder = self.solrFolder
						
			root = self.tree.getroot()	
			
			newTask = SubElement( root, "task" )
			
			newNode = Element( "status" )
			newNode.text = "pending"
			newTask.append( newNode )
			
			newNode = Element( "taskid" )
			newNode.text = str(taskid)
			newTask.append( newNode )
					
			newNode = Element( "directory" )
			newNode.text = str(folder)
			newTask.append( newNode )
			
			self.tree.write("outfile.xml")
			
		elif tasktype == "processTopic":
			print "Processing topic modeling data"
			if folder == None:
				folder = self.topicFolder
		else:
			print "Unknown task" + tasktype
			
	#def checkTask( self, taskid ):
		
