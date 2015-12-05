#coding:utf-8
'''
Created on 2015年12月5日 上午11:41:54

@author: TianD

@E-mail: tiandao_dunjian@sina.cn

@Q    Q: 298081132
'''

# import fileinput
# 
# for line in fileinput.input("C:\\Users\\huiguoyu\\Desktop\\test.txt", inplace=True):
#     print line.replace("2014", "2013")


import codecs

file = "C:\\Users\\huiguoyu\\AppData\\Local\\Thinkbox\\Deadline7\\temp\\maya_job_info.job"
with codecs.open(file, 'r', encoding='utf-16') as f:
    for l in f.readlines():
        print l