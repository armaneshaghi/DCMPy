import os
import glob
import re
import numpy as np

class read(object):
    def __init__(self, path):
        self.path = path
        log = glob.glob(os.path.join(self.path, '*.log'))
        if len(log) != 1:
            print '%s more than one log or log non-existent' %(path)
            raise RuntimeError
        res = glob.glob(os.path.join(self.path, '*.res'))
        if len(res) != 1:
            print '%s more than one res or res non-existent' %(self.path)

        self.log = log
        self.res = res
        return None
    
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
        else:
            raise Exception('invalid block name')
        return block_type
   
    def __substringIndex__(self, stringList, subString):
        for i, s in enumerate(stringList):
            if subString in s:
                return i
        return -1

    def __scantStart__(self, logContent):
        #giving the time at which the very first scan 
        #has been acquired, TR = 2.0 
        #first real scan = 7
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
 
 
    def __oneBack__(self, stimuli):
        #stimuli with 3 columns
        #finding hits and returning a
        #list of two integers that are
        #INDICES of hits
        hits = [None] * 2 #1 is hit, zero not hit
 
        for i in range(0, 10):
            current_stimuli = stimuli[i, 0]
            if i == 0:
                continue
            prev_stimulus = stimuli[i-1, 0]
            if prev_stimulus == current_stimuli:
                if hits[0] is None:
                    hits[0] = i
                else:
                    hits[1] = i
        return hits
 
    def __twoBack__(self, stimuli):
         #returing a list of two integers
         #each corresponding to a 
         #hit index
         #stimuli with 3 columns
         hits = [None] * 2 
                                                   
         for i in range(0, 10):
             current_stimuli = stimuli[i, 0]
             if i == 0:
                 continue
             if i == 2:
                 continue
             prev2_stimulus = stimuli[i-2, 0]
             if prev2_stimulus == current_stimuli:
                 if hits[0] is None:
                     hits[0] = i
                 else:
                     hits[1] = i
         return hits
 
    def __blockResult__(self, resContent):
        #order of presented blocks, e.g: 0-back
        #1-back and 2-back
        #
        task_order = np.zeros((30, 1), dtype=np.int)
        #stimuli with 10 rows for each presented
        #stimuli and 3 columns for: 1) presented 
        #stimuli, 2) time of presentation 3) whether
        #the subject hit the button (1 = Hit)
        stimuli = np.zeros((10, 3), dtype=np.int)
 
        n_backPat = re.compile("'(\d)-back'\s*.*")
        stimulus_pat = re.compile("'{0,1}(\d)'{0,1}\\t(\d{3,})\\t(\d{1,2})\\t-{0,1}\d*\\t\\n")
        #all_stimuli will contain list of 10x3 numpy array corresponding to 
        #each active block
        all_stimuli = list() 
        for i in range(0, 30):
            blockContent = resContent[0 + (i * 12) : 12 + (i * 12)]
            for j, s in enumerate(blockContent):
                #first finding out what N back we are dealing with
                if j == 0:
                    n_back_search = n_backPat.search(s)
                    if n_back_search is not None:
                        n_back_type = int(n_back_search.group(1)) 
                        task_order[i] = n_back_type
 
                    else:
                        raise Exception("cannot understand block"
                                " result's first line")
                if j >= 2:
                    stimulus_search = stimulus_pat.search(s)
                    if stimulus_search is not None:
                        #minus 2 is because the first two lines are not stimuli
                        #columns: 1 = presented 2 = time of presentation
                        #3 = subject reponse (0 or 1)
                        row = j - 2
                        stimuli[row, 0] = int(stimulus_search.group(1))
                        stimuli[row, 1] = int(stimulus_search.group(2))
                        stimuli[row, 2] = int(stimulus_search.group(3))
                        if stimuli[row, 2] == 28.:
                            stimuli[row, 2] = 1
                        else:
                            stimuli[row, 2] = 0
            temp_stimuli = np.copy(stimuli)
            all_stimuli.append(temp_stimuli)
        
        return all_stimuli, task_order
 
 
 
    ''' 
    def __blockAnalyse__(self, logContent):
        #pattern of first stimulus of each block, group 1 = n-back load, 2 = time of onset
        pat_firstStimOnset = re.compile('start of (\d-back) run number \d{1,2} at\
                slice number \d{1,3} at time (\d{3,})')
        #pattern of the last stimulus in log, group 1
        pat_lastStimulus = re.compile('start of \d-back run number [0-9]{1,2} trial\
                number 10 at slice number \d{1,3} at time (\d{3,})')
        
        for i, line in enumerate(logContent):
            
            
            
 
        startLineIndex = self.__substringIndex__(logContent)
 
 
 
    def  testing():
        log = self.log
        res = self.res
        log_content = self.__content_read__(log)
        res_content = self.__content_read__(res)
        #setting start of the experiment
        exOnset = self.__scanStart__(log_content)
        return None
        
 
        
''' 
