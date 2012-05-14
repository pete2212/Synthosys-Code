#!/usr/bin/python
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

import time
import boto
import boto.ec2
import re
import os


class AWSInteraction:

    def __init__(self, bucket=None):
        """ 
        Args: 
            bucket: if bucket exists w/o permission, raises boto error.
                "new" means create new folder (smetrics_x) | x=time
                default: smetrics_default

        Returns: No current return.
        Raises: No current Error handling.
        """
        if not bucket: self.bucket = "smetrics_default"
        elif bucket == "new": self.bucket = "smetrics_" + str(time.time())
        else: self.bucket = bucket        
        self.s3 = boto.connect_s3()	

    # TODO(peter): Add testing components.  Remove unnecessary stuff.
    def uploadS3(self, file, key=None, bucket=None, path=None,
                 permission="authenticated-read", debug=False, override=False):
        """Upload a file from the local server to AWS

        Args:
            file: the file to be transferred
            key: the location of the file on S3.  
                default: to be the same as file.
            bucket: specified bucket name.
                default: smetrics_default
            path: a location outside of the root directory
            permission: sets the ACL
                default: authenticated-read
                other options: public-read, public-read-write, private
            override: allow files to be overwritten?  
                otherwise check size/time before overwritting happens

        Returns: key associated with upload
        Raises: No current Error handling.
        """
        if not key: key = file
        if not bucket: bucket = self.bucket
        if path: 
            key = "{path}/{file}".format(path=path, file=key)

        if debug: print "S3:", bucket, file, key,
        if os.path.isfile(file):
            b = self.s3.create_bucket(bucket)
            # must get file to get its attributes
            k = b.get_key(key)     
            # if size or time parameters change or key doesn't exist
            if override or not k or not k.exists() or \
               str(os.path.getsize(file)) != k.get_metadata("size") or \
               str(os.path.getmtime(file)) > k.get_metadata("time"):
                k = b.new_key(key)
                k.set_metadata("size", str(os.path.getsize(file)))
                k.set_metadata("time", str(os.path.getmtime(file)))
                k.set_contents_from_filename(file)
                k.set_acl(permission)
                if debug: print "[uploaded]",
        if debug: print ""
        return k

    def uploadS3_path(self, dir, recursive=True, **kwargs):
        """Uploads a path (and its contents) to S3

        Args:
            dir: the directory to be inspected
            recursive: allows recursive searching of directory
        Returns: No current return.
        Raises: No current Error handling.
        """
        for x in os.listdir(dir):
            obj = "{dir}/{file}".format(dir=dir, file=x)
            if os.path.isfile(obj):
                self.uploadS3(file=obj, **kwargs)
            elif recursive:
                self.uploadS3_path(dir=obj, recursive=recursive, **kwargs)

    def checkSysStatus(self, instance):
        time.sleep(120)
        out = instance.get_console_output()
        m = re.search('([0-9a-f][0-9a-f]:){15}[0-9a-f][0-9a-f]', 
                      str(out.output))
        os.popen("ssh-keyscan %s 2>/dev/null > host.key" % 
                 instance.public_dns_name)
        os.popen("ssh-keygen -q -R %s" % instance.public_dns_name)
        os.popen("ssh-keygen -q -H -f host.key")
        os.popen("cat host.key >> ~/.ssh/known_hosts")
        #ignore for now, checking validity of host key
        #os.popen("ssh-keygen -lf host.key > host.fingerprint")
        #os.popen("read len ACTUAL_FINGERPRINTS host rsa < host.fingerprint")
        #os.popen('echo "Actual fingerprints are $ACTUAL_FINGERPRINTS"')
        #print "Actual fingerprints are $ACTUAL_FINGERPRINTS"

    def checkKeyPair(self, keypair_name, public_key_file):
        fp = open(public_key_file)
        material = fp.read()
        fp.close()
        for region in boto.ec2.regions():
            ec2 = region.connect()
            try:
                key = ec2.get_all_key_pairs(keynames=[keypair_name])[0]
                print 'Keypair(%s) already exists in %s' % \
                       (keypair_name, region.name)
            except ec2.ResponseError, e:
                if e.code == 'InvalidKeyPair.NotFound':
                    print 'Importing keypair(%s) to %s' % \
                          (keypair_name, region.name)
            ec2.import_key_pair(keypair_name, material)

    def startEC2Instance(self, 
                         ami="ami-2727f84e", key_name="automation-key3", 
                         instance_type="t1.micro", group_name = "open5",
                         key_extension=".pem", key_dir="~/.ssh", 
                         ssh_port=22, solr_port=8983, http_port=80,
                         tag="instance test", cidr = "0.0.0.0/0", 
                         user_data="None", login_usr="ubuntu"):
        ec2 = boto.connect_ec2()
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

        reservation = ec2.run_instances(ami, key_name=key_name, 
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
        #instance.use_ip("23.21.137.252")
        instance.add_tag( tag )	
        time.sleep(10)
        self.checkSysStatus(instance)
        return instance.public_dns_name

    #from cookbook
    def printRunningInstances(self, running_instances):
        print 'The following running instances were found'
        for account_name in running_instances:
            print '\tAccount: %s' % account_name
            d = running_instances[account_name]
            for region_name in d:
                print '\t\tRegion: %s' % region_name
                for instance in d[region_name]:
                    print '\t\t\tAn %s instance: %s' % \
                          (instance.instance_type, instance.id)
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
                    print '\t\t\tAn %s instance: %s' % \
                          (instance.instance_type, instance.id)
                    print '\t\t\t\tTags=%s' % instance.tags	
                    print '\nTerminating instance "%s"' % instance.id
                    ret = ec2.terminate_instances(str(instance.id))
                    print "Terminated instance %s" % ret
		
