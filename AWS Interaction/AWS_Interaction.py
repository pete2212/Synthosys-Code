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

import time
import boto
import boto.ec2


class AWSInteraction:
	def uploadAWS(self, ifname = "", ofname = "", foldername = "", permissions = "private" ):
		if foldername == "":
			curTime = time.time()
			foldername = "s3_connect_" + str(curTime) #add current time in seconds to end of string for unique bucketname
		
		if ofname == "":
			ofname = "default/default_file"
		
		if ifname == "":
			ifname = "/home/ptr/Documents/default_file.txt"
		
					
		s3 = boto.connect_s3()	
		bucket = s3.create_bucket(foldername)     
		key = bucket.new_key( str( ofname ) )
		key.set_contents_from_filename( str( ifname) )
		key.set_acl('private')
		print "Setup s3 connection, created new bucket with name" 
		print foldername
		print "\n"
		
		return
	
	def checkKeyPair(self, keypair_name, public_key_file):
		fp = open(public_key_file)
		material = fp.read()
		fp.close()
	
		for region in boto.ec2.regions():
			ec2 = region.connect()
		
			try:
				key = ec2.get_all_key_pairs(keynames=[keypair_name])[0]
				print 'Keypair(%s) already exists in %s' % (keypair_name,
                                                        region.name)
			except ec2.ResponseError, e:
				if e.code == 'InvalidKeyPair.NotFound':
					print 'Importing keypair(%s) to %s' % (keypair_name,
                                                       region.name)
                ec2.import_key_pair(keypair_name, material)
			
		
	def startEC2Instance(self, 
						 ami="ami-305b8759", 
						 key_name="automation-key2",
						 instance_type="t1.micro",
						 group_name = "open5",
						 key_extension=".pem",
	                     key_dir="~/.ssh", 
	                     ssh_port=22, 
	                     solr_port=8983,
	                     http_port=80,
	                     tag="instance test",
	                     cidr = "0.0.0.0/0",
	                     user_data="None",
	                     login_usr="ubuntu"):
							 
		ec2 = boto.connect_ec2()
		
		#try:
#		file_name = str(key_dir) + "/" + str(key_name) + str(key_extension)
		try:
			key = ec2.get_all_key_pairs(keynames=[key_name])[0]
		except ec2.ResponseError, e:
			if e.code == 'InvalidKeyPair.NotFound':
				print 'Creating keypair: %s' % key_name

				key = ec2.create_key_pair(key_name)
				
				key.save(key_dir)
				
		try:
			group = ec2.get_all_security_groups( groupnames=[group_name])[0]
		except ec2.ResponseError, e:
			if e.code == "InvalidGroup.NotFound" :
				print "Creating Security Group: %s" % group_name
				group = ec2.create_security_group(group_name, "A group that allows ssh access")
				group.authorize("tcp", ssh_port, ssh_port, cidr)
				group.authorize("tcp", solr_port, solr_port, cidr)
				group.authorize("tcp", http_port, http_port, cidr)
			else:
				raise
				
		
		reservation = ec2.run_instances(ami,
                                    key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    user_data=user_data)
                                    
		instance = reservation.instances[0]
		
		print 'waiting for instance to start'
		
		while instance.state != 'running':
			print "Instance state =" + str(instance.state)
			time.sleep(5)
			instance.update()
		print "done"
		
		print "DNS = " + str(instance.public_dns_name)
		
		instance.add_tag( tag )	
		
		return instance.public_dns_name
	
	#def uploadToEC2( self, fname, dns_name )
		
		
	#from cookbook
	def printRunningInstances(self, running_instances):
		print 'The following running instances were found'
		for account_name in running_instances:
			print '\tAccount: %s' % account_name
			d = running_instances[account_name]
			for region_name in d:
				print '\t\tRegion: %s' % region_name
				for instance in d[region_name]:
					print '\t\t\tAn %s instance: %s' % (instance.instance_type,
														instance.id)
					print '\t\t\t\tTags=%s' % instance.tags	
			
	#account_name[array]->Region[array]->instance/tag		
	def findAllRunningInstances(self, accounts=None, quiet=False):
		"""
		Will find all running instances across all EC2 regions for all of the
		accounts supplied.

		:type accounts: dict
		:param accounts: A dictionary contain account information.  The key is
						 a string identifying the account (e.g. "dev") and the
						 value is a tuple or list containing the access key
						 and secret key, in that order.
						 If this value is None, the credentials in the boto
						 config will be used.
		"""
		if not accounts:
			creds = (boto.config.get('Credentials', 'aws_access_key_id'),
					 boto.config.get('Credentials', 'aws_secret_access_key'))
			accounts = {'main' : creds}
			print creds
		running_instances = {}
		for account_name in accounts:
			running_instances[account_name] = {}
			ak, sk = accounts[account_name]
			for region in boto.ec2.regions():
				conn = region.connect(aws_access_key_id=ak,
									  aws_secret_access_key=sk)
				filters={'instance-state-name' : 'running'}
				instances = []
				reservations = conn.get_all_instances(filters=filters)
				for r in reservations:
					instances += r.instances
				if instances:
					running_instances[account_name][region.name] = instances
		if not quiet:
			self.printRunningInstances(running_instances)
		return running_instances

	def terminateInstances(self, instanceId):
		ec2 = boto.connect_ec2()
		for account_name in instanceId:
			print '\tAccount: %s' % account_name
			d = instanceId[account_name]
			for region_name in d:
				print '\t\tRegion: %s' % region_name
				for instance in d[region_name]:
					print '\t\t\tAn %s instance: %s' % (instance.instance_type,
														instance.id)
					print '\t\t\t\tTags=%s' % instance.tags	
					print '\nTerminating instance "%s"' % instance.id
					ret = ec2.terminate_instances( str(instance.id) )
					print "Terminated instance %s" % ret
		
