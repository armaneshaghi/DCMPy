import os
import glob
import re
import numpy as np

class read(self,path, *args, **kwargs):
    def __init__(self):
        log = glob.glob(os.path.join(path, '*.log'))
        if log != 1:
            print '%s more than one log or log non-existent' %(path)
            raise RuntimeError
        res = glob.glob(os.path.join(path, '*.res'))
        if res != 1:
            print '%s more than one res or res non-existent' %(path)

        self.log = log
        self.res = res
        return self
    
    def __content_read__(self, textfile):    
        with open(textfile) as text:
            content = text.readlines()
            return content
    
    def __block_def__(self, block):
        if '0-back' in block[0]:
            block_type = 'zero'
        elif '1-back' in block[0]:
            block_type = 'one'
        elif '2-back' in block[0]:
            block_type  = 'two'
        else
            raise Exception('invalid block name')
        return block_type

   def __startFind__(self, block):
       
   
   def 
       log = self.log
       res = self.res
       log_content = self.__content_read__(log)
       res_content = self.__content_read__(res)
       #setting start of the experiment
       block_type = 

