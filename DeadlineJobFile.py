#coding:utf-8
'''
Created on 2015年12月4日 上午10:55:50

@author: TianD

@E-mail: tiandao_dunjian@sina.cn

@Q    Q: 298081132
'''

import re
import codecs

class JobInfo(object):
     
    def __init__(self, file):
        super(JobInfo, self).__init__()
        self.file = file
        self.defaultJobfile = None
         
    def create(self, key = [], value = [], file = None):
        if file :
            file = file
        else :
            file = self.file
        with codecs.open(file, 'w', encoding= 'utf-16') as f:
            for k, v in zip(key, value):
                text = '{key}={value}\r\n'.format(key = k, value = v)
                f.writelines(text)
        f.close()
        return self.file
     
    def write(self, key, value, file = None):
        if file :
            file = file
        else :
            file = self.file
        result = self.read(file = file)

        allK = [r[0] for r in result]
        num = len(result)
        for k, v in zip(key, value):
            if k in allK:
                index = allK.index(k)
                result[index][1] = v
            else :
                result.append([k, v, num])
                num += 1

        return self.create(key = [r[0] for r in result], value = [r[1] for r in result])
           
    def read(self, key = None, file = None):
        if file :
            file = file
        else :
            file = self.file
        result = []
        lineNUM = 0
        with codecs.open(file, 'r', encoding= 'utf-16') as f:
            for l in f.readlines():
                currentK, currentV = self.parse(l)
                if key and currentK not in key:
                    pass
                else :
                    result.append([currentK, currentV, lineNUM])
                lineNUM += 1
        f.close()
        return result 
    
    def parse(self, text):
        splitLabel = '='
        match = re.match('(?P<key>\w*){0}(?P<value>[\w\W]*)\r'.format(splitLabel), text)
        if match:
            key = match.group('key')
            value = match.group('value')
        else :
            key = None
            value = None
        return key, value
        
    def delete(self, file = None):
        if file :
            file = file
        else :
            file = self.file
        pass

if __name__ == "__main__":
    defaultFile = "Z:\\Resouce\\Support\\KX\\maya2014\\modules\\TianD_KX_TOOL\\scripts\\MayaSubmit2Deadline\\default_maya_job_info.job"
    file = "E:\\testjobfile.job"
    jobinfo = JobInfo(file)
    jobinfoLst = jobinfo.read(file = defaultFile)
    jobinfo.create(key = [i[0] for i in jobinfoLst], value = [i[1] for i in jobinfoLst])
    jobinfo.write(key = ['Name', 'Priority', 'Frames', 'OutputDirectory0'], value = ["a", 100, "1-10", "e:/"])
            