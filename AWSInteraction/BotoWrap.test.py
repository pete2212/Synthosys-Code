#!/usr/bin/python

import BotoWrap
import unittest
import os

class TestBotoWrap(unittest.TestCase):

    def setUp(self):
        self.aws = BotoWrap.BotoWrap(bucket="smetrics_test")
        os.system("touch file.test")
        os.system("mkdir tempDIRtemp")
        os.system("touch tempDIRtemp/file1.test")
        os.system("touch tempDIRtemp/file2.test")
        os.system("mkdir tempDIRtemp/DIR")
        os.system("touch tempDIRtemp/DIR/file3.test")

    def tearDown(self):
        os.system("rm file.test")
        os.system("rm tempDIRtemp/file1.test")
        os.system("rm tempDIRtemp/file2.test")
        os.system("rm tempDIRtemp/DIR/file3.test")
        os.system("rmdir tempDIRtemp/DIR")
        os.system("rmdir tempDIRtemp")

    def s3KeyCheck(self, key, bucket=None, remove=True, acl=None):
        #easy test to see if a certain file exists
        if not bucket:
            bucket = self.aws.bucket
        b = self.aws.s3.create_bucket(bucket)
        k = b.get_key(key)
        if not k:
            return False
        if not k.exists():
            return False
        # TODO (ron): how do we return this in a meaningufl way?
        #if acl:
        #    print k.get_acl()
        if remove:
            k.delete()
        return True

    def test_getS3key(self):
        self.aws.uploadS3("file.test")
        key = self.aws.getS3key("file.test")
        # make sure key is being returned
        self.assertEqual(str(type(key)), "<class 'boto.s3.key.Key'>")
        # check metadata
        self.assertEqual(key.get_metadata("size"), "0")
        self.assertEqual(key.get_metadata("time"), 
                         str(os.path.getmtime("file.test")))
        # remove the key
        key.delete()

    def test_uploadS3(self):
        # default settings
        self.aws.uploadS3("file.test")
        self.assertTrue(self.s3KeyCheck("file.test"))
        # change the default key
        self.aws.uploadS3("file.test", key="file.test2")
        self.assertTrue(self.s3KeyCheck("file.test2"))
        # change the default bucket
        self.aws.uploadS3("file.test", bucket="smetrics_test2")
        self.assertTrue(self.s3KeyCheck("file.test", 
                                        bucket="smetrics_test2"))
        self.aws.s3.delete_bucket("smetrics_test2")
        # change the default path
        self.aws.uploadS3("file.test", path="smetrics_test")
        self.assertTrue(self.s3KeyCheck("smetrics_test/file.test"))
        # few key + path combos
        self.aws.uploadS3("file.test", path="smetrics_test", key="f.test")
        self.assertTrue(self.s3KeyCheck("smetrics_test/f.test"))
        self.aws.uploadS3("file.test", path="smetrics_test/test", 
                                       key="file.test")
        self.assertTrue(self.s3KeyCheck("smetrics_test/test/file.test"))
        self.aws.uploadS3("file.test", key="smetrics_test/file.test")
        self.assertTrue(self.s3KeyCheck("smetrics_test/file.test"))
        # change of permission
        # TODO (ron): test for change of permission
        #self.aws.uploadS3("file.test", permission="private")
        #self.assertTrue(self.s3KeyCheck("file.test", acl="private"))

    def test_uploadS3_path(self):
        # test generic file load
        self.aws.uploadS3_path("tempDIRtemp")

        # test if from default path
        os.chdir("tempDIRtemp")
        self.aws.uploadS3_path()
        os.chdir("..")

if __name__ == '__main__':
    unittest.main()

