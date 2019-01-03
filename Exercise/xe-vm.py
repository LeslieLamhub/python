#!/usr/bin/python
import os
import sys

if os.system('xe vm-export vm=platform-bigdata-03-8.114 filename=/var/run/sr-mount/7c470c77-76b7-10ee-5998-0388a6834936/platform-bigdata-03-8.114.xva') ==0:
    os.system('xe vm-export vm=platform-bigdata-04-8.115 filename=/var/run/sr-mount/7c470c77-76b7-10ee-5998-0388a6834936/platform-bigdata-04-8.115.xva')
else:
    print 'This is a bad command'