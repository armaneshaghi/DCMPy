"""
Arman Eshaghi, May 2014, MSRC
Tehran, Iran 
License: Creative Commons 3.0 

This modules fills hypointense lesions on 
T1-weighted images and fills them with median
intensity of normal appearing white matter

Before initiating the functions, lesion maps should 
be coregistered with T1 images. 

"""

from nipype.interfaces.base import BaseInterface, \
        BaseInterfaceInputSpec, traits, File, TraitedSpec
from nipype.utils.filemanip import split_filename
import nibabel as nb
import numpy as np 
import os


"""
assuming T1 and lesion map are in
the same space and co-registered
this functions fills lesions with
median intensity of the normal appearing
white matter
***
T1 = t1 image
wmp_map = white matter probability map
resulting from priliminary segmentation
without lesion filling
lm = lesion map
"""



class FillLesionInputSpec(BaseInterfaceInputSpec):
    T1 = File(exists = True, desc = 't1 volume which is \
            already bias field corrected', mandatory = True)
    lesion_map = File(exists = True, desc = 'lesion mask of \
            flair or T2 scans', mandatory = True)
    wmp_map = File(exists = True, desc = 'white matter probability map', 
            mandatory = True)

class FillLesionOutputSpec(TraitedSpec):
    filled_t1 = File(exists = True, desc = 'lesion \
            filled t1 volume')

class LesionFill(BaseInterface):
    input_spec = FillLesionInputSpec 
    output_spec = FillLesionOutputSpec

    def _run_interface(self, runtime):
        t1_fname = self.inputs.T1
        lm_fname = self.inputs.lesion_map
        wmp_fname = self.inputs.wmp_map
        #getting image and data via nibabel
        t1_img = nb.load(t1_fname)
        lm_img = nb.load(lm_fname)
        wm_img = nb.load(wmp_fname)
        #converting to matrix 
        t1_mx = t1_img.get_data()
        lm_mx = lm_img.get_data()
        wm_mx = wm_img.get_data()
        #creating a binary wm map
        wm_bn = wm_mx[:]
        #binarising at a threshold of 0.4 
        wm_bn[wm_mx > 0.4] = 1
        wm_bn[wm_mx <= 0.4] = 0
        #making sure wm lesion map is in fact binary
        #(only 0 and 1)
        lm_unique_arr = np.unique(lm_mx)
        for i in lm_unique_arr:
            if int(i) != 0 | int(i) !=1:
                print "lesion map is not binary please recheck"
                break
        #nawm is the difference between wm probability
        #and lesion map (remember lesion map and wm 
        #probability map are in the same space
        #first making a binary 
        nawm_bn =  wm_bn - lm_mx
        
        #extracting median intenstiy of nawm
        median_nawm = np.median(t1_mx[nawm_bn == 1])
        #fill lesions 
        lesion_fill = t1_mx[:]
        lesion_fill[lm_mx == 1] = median_nawm
        
        #merging filled lesions with nawm
        img = nb.Nifti1Image(lesion_fill, t1_img.get_affine(),
                t1_img.get_header())
        _, base, _ = split_filename(t1_fname)
 
        path_list = t1_fname.split('/')[0:-1]
        path = '/'
        for i in path_list:
           path = os.path.join(path, i)
        nb.save(img, os.path.join(path, base + '_filled.nii.gz'))
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        t1_fname = self.inputs.T1
        path_list = t1_fname.split('/')[0:-1] 
        path = '/'
        for i in path_list:
            path = os.path.join(path, i)
        _, base, _ = split_filename(t1_fname)
        outputs["filled_t1"] = os.path.join(path, base + '_filled.nii.gz')
        return outputs
