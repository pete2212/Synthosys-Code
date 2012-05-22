#!/usr/bin/python

import AWSWrapper
import os

s3 = AWSWrapper.AWSInteraction()
for x in os.listdir("."):
    s3.uploadS3(file=x, path="peter", debug=True)
