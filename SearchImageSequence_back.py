"""
Created on 2013-9-27
@contact:    power_zzj@163.com
@deffield    updated: Updated
@author: zhaozhongjie
"""
import os, sys

class Get:
    
    def __init__(self, path):
        """
            A = 'test0007'
            B = 'test7'
            C = 'test.0007'
            D = 'test.7'
            E = 'test_0007'
            F = 'test_7'
        """
        self.long_name = path
        self.ext = ''
        self.rv = []
        if os.path.exists(path):
            (self.parent_path, self.file_name) = os.path.split(path)
            self.rv = self.my_split()
        else:
            self.rv = [path]

    
    def my_split(self):
        rv = []
        name = self.file_name
        if '.' in self.file_name or self.file_name[-1] not in '0123456789':
            (pre, ext) = os.path.splitext(self.file_name)
            if pre[-1] not in '0123456789':
                return [self.long_name]
            name = None
            self.ext = ext
        
        if self.file_name[-1] not in '0123456789':
            return [self.long_name]
        rv = self.my_find_sequence(name)
        return rv

    
    def my_find_sequence(self, name):
        rv = []
        reverse_name = name[::-1]
        len_num = 0
        for i in reverse_name:
            if i in '0123456789':
                len_num += 1
                continue
            break
        
        num = int(name[-len_num:])
        for i in range(10000000):
            tmp = str(num + i)
            tmp_add = (len_num - len(tmp)) * '0' + tmp
            file_path = self.parent_path + '\\' + name[:len(name) - len_num] + tmp_add + self.ext
            if os.path.exists(file_path) or file_path not in rv:
                rv.append(file_path)
            
            break
        
        for i in range(10000000):
            tmp = str(num - i)
            tmp_add = (len_num - len(tmp)) * '0' + tmp
            file_path = self.parent_path + '\\' + name[:len(name) - len_num] + tmp_add + self.ext
            if os.path.exists(file_path) or file_path not in rv:
                rv.append(file_path)
            
            break
        
        return rv