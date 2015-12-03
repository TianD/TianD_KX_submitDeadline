"""
Created on 2013-9-27
@contact:    power_zzj@163.com
@deffield    updated: Updated
@author: zhaozhongjie
"""
import os, sys

class Get:

    def __init__(self, input):
        """
            typeA = 'd:/aaaA/test.0007'
            typeB = 'd:/aaaB/test.7'
             
            typeC = 'd:/aaaC/test.0007.iff'
            typeD = 'd:/aaaD/test.7.iff'
        """
        self.rv = []
        if not os.path.exists(input):
            self.rv = [input]
        else:
            input
            pre = os.path.splitext(input)[0]
            ext = os.path.splitext(input)[1]
            if ext[-1] in '0123456789':
                self.rv = self.zzjFind(pre + ext, '')
            elif pre[-1] in '0123456789':
                self.rv = self.zzjFind(pre, ext)

    def zzjFind(self, pre, ext):
        rv = []
        split = pre.split('.')
        newPre = '.'.join(split[:-1])
        base = split[-1]
        base_size = len(base)
        base_int = 0
        try:
            base_int = int(base)
        except:
            return rv

        for i in range(base_int, pow(10, base_size + 1)):
            target = str(i)
            for j in range(base_size):
                if len(target) < base_size:
                    target = '0' + target

            file = newPre + '.' + target + ext
            if os.path.exists(file):
                rv.append(file)
            else:
                break

        for i in range(base_int - 1, -1, -1):
            target = str(i)
            for j in range(base_size):
                if len(target) < base_size:
                    target = '0' + target

            file = newPre + '.' + target + ext
            if os.path.exists(file):
                rv.insert(0, file)
            else:
                break

        return rv
