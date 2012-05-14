#!/usr/bin/python

import AWSWrapper
import unittest
import os

class TestAWSWrapper(unittest.TestCase):

    def setUp(self):
        self.aws = AWSWrapper.AWSInteraction()
        os.system("touch file.test")

    def tearDown(self):
        os.system("rm file.test")

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

    def test_uploadS3(self):
        # first make sure you can detect file
        self.assertTrue(os.path.isfile("file.test"))

        # default settings
        k = self.aws.uploadS3("file.test")
          # make sure key is being returned
        self.assertEqual(str(type(k)), "<class 'boto.s3.key.Key'>")
          # check metadata
        self.assertEqual(k.get_metadata("size"), "0")
        self.assertEqual(k.get_metadata("time"), 
                         str(os.path.getmtime("file.test")))
        self.assertTrue(self.s3KeyCheck("file.test"))
        # change the default key
        self.aws.uploadS3("file.test", key="file.test2")
        self.assertTrue(self.s3KeyCheck("file.test2"))
        # change the default bucket
        self.aws.uploadS3("file.test", bucket="smetrics_test")
        self.assertTrue(self.s3KeyCheck("file.test", 
                                        bucket="smetrics_test"))
        self.aws.s3.delete_bucket("smetrics_test")
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

if __name__ == '__main__':
    unittest.main()

