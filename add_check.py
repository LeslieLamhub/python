#!/usr/bin/env python
# encoding: utf-8

import os

def ListFilesToTxt(dir,file,wildcard,recursion):
    exts = wildcard.split(" ")
    files = os.listdir(dir)
    for name in files:
        fullname=os.path.join(dir,name)
        if(os.path.isdir(fullname) & recursion):
            ListFilesToTxt(fullname,file,wildcard,recursion)
        else:
            for ext in exts:
                if(name.endswith(ext)):
                    file.write(name + ".check" + "\n")
                    break

def Test():
  dir="/home/duizhang/wld/load"     #文件路径
  outfile="/home/duizhang/wld/load/check.txt"                     #写入的txt文件名
  wildcard = ".tar.gz"      #要读取的文件类型；
  file = open(outfile,"w")
  if not file:
    print ("cannot open the file %s for writing" % outfile)
  ListFilesToTxt(dir,file,wildcard, 1)
  file.close()
Test()

def Touch(file_name):
    if file_name in os.listdir('/home/duizhang/wld/load'):
              print("file exist!")
    else:
              print("creating %s" %file_name)
              fid = open(file_name,'w')
              fid.close()

f = open("/home/duizhang/wld/load/check.txt","r")
data = f.readlines()
#print(data)

for eacn_file in data:
    eacn_file=eacn_file.strip('\n')
    Touch(eacn_file)
