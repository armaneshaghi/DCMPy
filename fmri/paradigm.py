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
   
   def __substringIndex__(self, stringList, subString):
       for i, s in enumerate(stringList):
           if subString in s:
               return i
       return -1

   def __experimentStart__(self, logContent):
       startLineIndex = self.__substringIndex__(logContent, 'Key\t33\tDOWN\tat')
       nextStartLineIndex = startLineIndex + 1 
       startLine = logContent[startLineIndex]
       nextStartLine = logContent[nextStartLineIndex]
       experiment_start = re.search('(\d{3,})\s+\\r\\n$', startLine)
       experiment_start = experiment_start.group(1)
       experiment_start_next = re.search('(\d{3,})\s+\\r\\n$', nextStartLine)
       experiment_start_next = experiment_start_next.group(1)
       if experiment_start != experiment_start_next:
           raise Exception('ill-posed log file')
       return double(experiment_start) 
        
       
       
       
   
   def 
       log = self.log
       res = self.res
       log_content = self.__content_read__(log)
       res_content = self.__content_read__(res)
       #setting start of the experiment
       exOnset = self.__experimentStart__(log_content)

       

