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

    def __call__(self):
        logfile = self.log
        resfile = self.res
        #extracting each file's content
        logContent = self.__content_read__(logfile)
        resContent = self.__content_read__(resfile)
        #extracting blocks
        all_stimuli, task_order = __blockResult__(resContent)
        #getting hits and reaction times for 1 and 2 back only
        #performance result is a 30x5 numpy array that shows the
        #performance measures are only calculated for 1 and 2 back
        #thus measures for 0-back blocks are only zeros (see below). 
        performance_result = list()
        all_stimuli
        for block_number, stimuli in enumerate(all_stimuli):
            n_back_type = int(task_order[block_number])
            if n_back_type == 1:
                hits = self.__oneBack__(stimuli)
                TP, TN, FN, FP, RT = self.__sensReactAnalyzer__(stimuli, 
                            hits, logContent)
            elif n_back_type == 2:
                hits = self.__twoBack__(stimuli)
                TP, TN, FN, FP, RT = self.__sensReactAnalyzer__(stimuli, 
                            hits, logContent)
            elif n_back_type == 0:
                TP, TN, FN, FP, RT = 0, 0, 0, 0, [0]
            
            performance_result.append([TP, TN, FN, FP, RT])
        scan_start = self.__scanStart__(logContent)
        normalised_all_stimuli = normalised_all_stimuli(all_stimuli, scan_start) 
        rest_start_stop = self.__restBlockAnalyzer__(normalised_all_stimuli)
        fsfast = self.__fsfastCondition__(normalised_all_stimuli,
                task_order, rest_start_stop)
        #creating a new paradigm file with .par extension
        path = self.path
        paradigm_file = os.path.join(path, 'fsfast.par')
        with open(paradigm_file, 'w') as text:
            for row in fsfast:
                block_onset = row[0]
                numeric_id  = row[1]
                duration = row[2]
                weight = row[3]
                name_of_condition = row[4]
                text.write('%d %d %d %d %s\n' %(block_number, numeric_id, 
                        duration, weight, name_of_condition))
            text.close()
        

        #normalising all times with respect to time of acquisition of
        #the first scan and then calculate times for rest block

    #TP, TN, FN, FP, RT
    def __fsfastWriter__(self, normalised_all_stimuli, task_order,\
            rest_start_stop):
 
        '''
        FSFAST paradigm file requires at least 3 columns:
        1. onset of condition
        2. numeric ID that codes the condition (0-back = 1, 1-back = 2, 
        2-back = 3, fixation = 0)
        3. Stimulus duration
        we will also include the following columns for the sake of completeness:
        4. Weight for parametric modulation (1 for 0-back, 2 for 1-back,
        3 for 2-back and 0 for rest (fixation) 
        5. name of condition (0-back, 1-back, 2-back and rest)
        '''
        fsfast=list()
        isi = 1400               
        stimulus_duration = 1000
        for block_number, block in enumerate(normalised_all_stimuli):
            n_back_type = task_order[block_number]
            weight, numeric_id, name_of_condition = self.__fsfastCondition__(n_back_type)
            #block duration is the difference between last and first stimuli added to 
            #the time that last stimuli is still on the screen (stimulus duration and isi)
            first_stimulus_onset = block[0,1]
            #for the sake of readability
            block_onset = first_stimulus_onset
            last_stimulus_onset = block[9, 1]
            #block duration as explained above
            duration = last_stimulus_onset - first_stimulus_onset + stimulus_duration + isi
            row = [block_onset, numeric_id, duration, weight, name_of_condition]
            row_temporary = row[:]
            fsfast.append(row_temporary)
            last_index = len(normalised_all_stimuli) - 1
            #adding rest block, the very last block does not come with a rest, hence '!='
            if block_number != last_index:
                block_onset = rest_start_stop[block_number, 0]
                block_end = rest_start_stop[block_number, 1]
                duration = block_end - block_onset
                numeric_id = 0
                weight = 0
                name_of_condition = 'NULL'
                row = [block_onset, numeric_id, duration, weight, name_of_condition]
                row_temporary = row[:]
                fsfast.append(row_temporary)
        return fsfast
    def __fsfastCondition__(self, n_back_type):
        if n_back_type == 0:
            weight = 1
            numeric_id = 1
            name_of_condition = '0-back'
        elif n_back_type == 1:
            weight = 2
            numeric_id = 2
            name_of_condition = '1-back'
        elif n_back_type == 2:
            weight = 3
            numeric_id = 3
            name_of_condition = '2-back'
        return weight, numeric_id, name_of_condition
 
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
        #finds the line at which subString exists
        for i, s in enumerate(stringList):
            if subString in s:
                return i
        return -1

    def __scanStart__(self, logContent):
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
        return int(experiment_start)
 
 
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
    
    def __normalisedTime__(self, all_stimuli, scan_start):
        #normaly all times are calculated from the start of 
        #cogent, here we calculate times since the very first 
        #scan time (acquired from __scanStart__from log file
        new_all_stimuli = list()
        for array_number, array in enumerate(all_stimuli):
            rows = array.shape[0]
            for row_number in range(0, rows):
                time = array[row_number, 1]
                new_time = time - scan_start
                array[row_number, 1] = new_time
            temp_array = np.copy(array)
            new_all_stimuli.append(temp_array)
        return new_all_stimuli
    
    def __sensReactAnalyzer__(self, stimuli, hits, logContent):
 
        TP = 0
        TN = 0
        FP = 0
        FN = 0
        firstHit = hits[0]
        secondHit = hits[1]
        reaction_time_list = list()
        for i in range(0, 10): 
            subHit = sitmuli[i, 2]
            #it is a true hit
            if i == firstHit or i == secondHit:
                #subject presses button
                if subHit == 1:
                    TP += 1
                    #true positive needs reaction time calculation
                    #second column from each block of stimuli numpy array 
                    #represents the stimuli onset
                    stimulus_onset = stimuli[i, 1]
                    reaction_time = self.__reactionTimer__(logContent, stimulus_onset)
                    reaction_time_list.append(reaction_time)
                #subject does not press the button
                if subHit != 1:
                     FN += 1
            #if it is not a hit see what subject is doing:
            #it is not a hit and subject doesn't do anything
            elif subHit == 0:
                 TN += 1
            #it is not a hit and subject hits the button
            elif subHit == 1:
                 FP += 1
        return TP, TN, FN, FP, reaction_time
    
    def __restBlockAnalyzer__(self, normalised_all_stimuli):
        #Will return a numpy array with 29x2 size that shows rest block start at the
        #first column and the end of rest block as the second column
        
        #units in milisecond from /data/about.txt file
        isi = 1400
        stimulus_duration = 1000
        instructions = 6000
        number_of_rest_blocks = len(normalised_all_stimuli) - 1
        rest_start_stop = np.zeros((29, 2))
        for i in range(0, number_of_rest_blocks): 
            current_block = normalised_all_stimuli[i]
            next_block = normalised_all_stimuli[i + 1]
            last_stimuli_current_block = current_block[9, 1]
            first_stimuli_next_block = next_block[0, 1]
            end_of_current_block = last_stimuli_current_block + stimulus_duration + isi
            rest_start = end_of_current_block
            start_of_next_block = first_stimuli_next_block - instructions
            rest_stop = start_of_next_block
            #first colum is start of the rest block
            rest_start_stop[i, 0] = rest_start
            #second column is end of the rest block
            rest_start_stop[i, 1] = rest_stop
        return rest_start_stop
            
 
    def __reactionTimer__(self, log_content, stimulus_onset):
        #SO: stimulus onset extracted from res files
        reg_ex_pat = ".*presented at time %d\\r\\n" %(stimulus_onset)
        reg_ex_pat = re.compile(reg_ex_pat)
        #first we find the stimulus presentation in log file
        #using stimulus onset time extracted from res file
        for line_number, line in enumerate(log_content):
            stimulus_pres_log = reg_ex_pat.search(line)
            if stimulus_pres_log is not None:
                presentation_line = line_number
                break
        #now that we have line number, starting from stimulus presentation
        #time, we search for the time subject hit the button
        subject_response_pat = ".*\\tKey\\t28\\tDOWN\\tat\\t(\d*)\s*\\r\\n"
        subject_response_pat = re.compile(subject_response_pat)
        for line in log_content[presentation_line:]:
            search_result = subject_response_pat.search(line)
            if search_result is not None:
                subject_response_time = int(search_result.group(1))
                break
        reaction_time = subject_response_time - stimulus_onset
        return reaction_time

def plotter(performance_result, task_order):

