from nipype.interfaces.base import BaseInterface, \
        BaseInterfaceInputSpec, traits, File, TraitedSpec, \
        isdefined, OutputMultiPath, DynamicTraitedSpec, \
        Undefined, Directory
from nipype.utils.filemanip import split_filename 
import nibabel as nb
import numpy as np 
import os
import glob
import re
import shutil


class IOcogpyInputSpec(BaseInterfaceInputSpec):

    base_directory = Directory(exists = True, 
            desc = 'base directory for seach')
    raise_on_empty = traits.Bool(True, usedefault = True, 
            desc = 'raise exception if empty for any given \
                    field')
    #template arguments are a list of strings to \
    # to replace placeholders in template
    #example template = [['flair', 't1'], 'regex_%s_%s', 'tp1_gA_P1']
    modalities = traits.List(mandatory = True, 
            desc='modalities to extract')
    template = traits.Str(mandatory = True, 
            desc = 'template of placeholders (path)')
    subject_id = traits.Str(mandatory=True, 
            desc = 'string of eg: tp1_gA_P1')
    #template is a regex matching string
    #that accepts placeholder along the way
    #it gets placeholders from 
    #template arguments
        
class IOcogpyOutputSpec(TraitedSpec):

    outputs = traits.List(desc = 'outputs of list of strings')

class IOcogpy(BaseInterface):

    input_spec = IOcogpyInputSpec
    output_spec = IOcogpyOutputSpec

    def _run_interface(self, runtime):
        #note modalities is a list
        modalities = self.inputs.modalities
        self._modalities = modalities
        path_template = self.inputs.template
        #tp1_gA_P22 is an example of this
        subject_id = self.inputs.subject_id
        tp, group, id = subject_id.split('_') 
        
        for modality in modalities:
            
            path = path_template %(tp, group, modality, id,
                modality, tp, id)
            path = os.path.join(base_directory, path)
            self.outputs.modality = path

    def _list_outputs(self):
        outputs = self.output_spec().get()
        for modality in self._modalities():
            outputs[modality] = self.outputs.modality
        return outputs

