#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
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

from AWS_Interaction     import AWSInteraction
from network_interaction import NetInteraction
import sys
import time

def startSingleEC2():
    instance_Conn = AWSInteraction()
    instance_name = instance_Conn.startEC2Instance()
    print "Function returned dns name: "
    print str(instance_name)
	
def main():
	
	instantiate = False
	terminate   = False
	connect     = False
	
	#if system arguments were passed in, parse
	if( len(sys.argv) > 1 ):
		for arg in sys.argv:
			if arg == "-r":
				instantiate = True
			elif arg == "-t":
				terminate = True
			elif arg == "-c":
				connect = True
			elif arg == "-h" or arg == "--help":
				print "\nOptions are:\n\n\t-r\n\t\tRun a new instance\n\n\t-t\n\t\tTerminate all running instances\n\n\t-c\n\t\tConnect to instance with ssh\n\n"
	else:
		print "No command line arguments provided, please use -h for options"
		
	s3_Conn = AWSInteraction()
	net_Conn = NetInteraction()
    
	#ifname = "", ofname = "", foldername = "", permissions = "private" ):
	#s3_Conn.uploadAWS(ofname = "output_test2", foldername = "folderuploadtestaws2")
	if instantiate:
		dns = s3_Conn.startEC2Instance( )
		print "Connecting to " + str(dns)
		
	if connect:
		net_Conn.netConnect( dns )
		print "Connection established at %s" % time.time()
		os.popen( "ssh p -5050 -i ~/.ssh/automation-key3.pem ubuntu@%s mkdir data" % str(dns) )
		net_Conn.upload("./upload/2012-03-17.tar.gz","~/data/upload.tar.gz")
		print "Upload finished at %s" % time.time()
	
	#time.sleep(10)
	
	if terminate:
		running_instances = s3_Conn.findAllRunningInstances()
		s3_Conn.terminateInstances( running_instances )
	
	
	print "ran successfully\n"
	
	return 0

if __name__ == '__main__':
	main()

