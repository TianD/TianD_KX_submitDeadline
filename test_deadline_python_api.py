#coding:utf-8
'''
Created on 2015年12月5日 上午11:41:54

@author: TianD

@E-mail: tiandao_dunjian@sina.cn

@Q    Q: 298081132
'''

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    

tree = ET.ElementTree(file = "E:\\maya\\SENBA\\106\\004\\cache\\nCache\\fluid\\SB_106_004_004_ef_c001\\fluidShape1.xml")

type = list(tree.iter('cacheType'))[0].attrib['Format']

time = list(tree.iter('time'))[0].attrib['Range']

perFrame = list(tree.iter('cacheTimePerFrame'))[0].attrib['TimePerFrame']

startFrame, endFrame = time.split('-')

print type, time, perFrame