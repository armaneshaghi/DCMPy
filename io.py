from nipype.interfaces.base import BaseInterface, \
        BaseInterfaceInputSpec, traits, File, TraitedSpec, \
        isdefined, OutputMultiPath, DynamicTraitedSpec, \
        Undefined
from nipype.utils.filemanip import split_filename, 
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
                    field)
    template_args = traits.Dict(key_trait=traits.Str, 
        value_trait=traits.List(traits.List
