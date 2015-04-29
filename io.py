import glob
import string
import os
import os.path as op
import shutil
import re
import tempfile
from warnings import warn

import sqlite3
from nipype.utils.misc import human_order_sorted

try:
    import pyxnat
except:
    pass

from nipype.interfaces.base import (TraitedSpec, traits, File, Directory,
                                    BaseInterface, InputMultiPath, isdefined,
                                    OutputMultiPath, DynamicTraitedSpec,
                                    Undefined, BaseInterfaceInputSpec)
from nipype.utils.filemanip import (copyfile, list_to_filename,
                                    filename_to_list)


def add_traits(base, names, trait_type=None):
    """ Add traits to a traited class.

    All traits are set to Undefined by default
    """
    if trait_type is None:
        trait_type = traits.Any
    undefined_traits = {}
    for key in names:
        base.add_trait(key, trait_type)
        undefined_traits[key] = Undefined
    base.trait_set(trait_change_notify=False, **undefined_traits)
    # access each trait
    for key in names:
        _ = getattr(base, key)
    return base
class IOBase(BaseInterface):

    def _run_interface(self, runtime):
        return runtime

    def _list_outputs(self):
        raise NotImplementedError

    def _outputs(self):
        return self._add_output_traits(super(IOBase, self)._outputs())

    def _add_output_traits(self, base):
        return base


class IOcogpyInputSpec(DynamicTraitedSpec, BaseInterfaceInputSpec):

    base_directory = Directory(exists = True, 
            desc = 'base directory for seach')
    #template arguments are a list of strings to \
    # to replace placeholders in template
    #example inputs: template = '%s/%s/%s/%s'
    #infield is the modalities that we are going to produce
    template = traits.Str(mandatory = True, 
            desc = 'template of placeholders (path)')
    subject_id = traits.Str(mandatory = True, 
            desc = 'format tp1_gA_P44')
    #template is a regex matching string
    #that accepts placeholder along the way
    #it gets placeholders from 
    #template arguments
    sort_filelist = traits.Bool(mandatory=True,
            desc='Sort the filelist that matches the template') 
    template_args = traits.Dict(key_trait=traits.Str,
                                value_trait=traits.List(traits.List),
                                desc='Information to plug into template')
    raise_on_empty = traits.Bool(True, usedefault=True, 
            desc='Generate exception if list is empty for a given field')
class IOcogpy(IOBase):

    input_spec = IOcogpyInputSpec
    output_spec = DynamicTraitedSpec
    _always_run = True

    def __init__(self, infields=None, outfields=None, **kwargs):
        """
        Parameters
        ----------
        infields : list of str
            Indicates the input fields to be dynamically created

        outfields: list of str
            Indicates output fields to be dynamically created

        See class examples for usage

        """
        if not outfields:
            outfields = ['outfiles']
        super(IOcogpy, self).__init__(**kwargs)
        undefined_traits = {}
        # used for mandatory inputs check
        self._infields = infields
        self._outfields = outfields
        if infields:
            for key in infields:
                self.inputs.add_trait(key, traits.Any)
                undefined_traits[key] = Undefined
        # add ability to insert field specific templates
        self.inputs.add_trait('field_template',
                              traits.Dict(traits.Enum(outfields),
                                          desc="arguments that fit into template"))
        undefined_traits['field_template'] = Undefined
        if not isdefined(self.inputs.template_args):
            self.inputs.template_args = {}
        for key in outfields:
            if not key in self.inputs.template_args:
                if infields:
                    self.inputs.template_args[key] = [infields]
                else:
                    self.inputs.template_args[key] = []

        self.inputs.trait_set(trait_change_notify=False, **undefined_traits)
     
     



    def _add_output_traits(self, base):
        """
        add the dynamic output field
        """

        return add_traits(base, self.inputs.template_args.keys())
    
    def _list_outputs(self):
        # infields are mandatory, however I could not figure out how to set 'mandatory' flag dynamically
        # hence manual check
        if self._infields:
            for key in self._infields:
                value = getattr(self.inputs, key)
                if not isdefined(value):
                    msg = "%s requires a value for input '%s' because it was listed in 'infields'" % \
                        (self.__class__.__name__, key)

        outputs = {}
        subject_id = self.inputs.subject_id
        tp, group, pid = subject_id.split('_')

        for key, args in self.inputs.template_args.items():
            outputs[key] = []
            template = self.inputs.template
            if hasattr(self.inputs, 'field_template') and \
                    isdefined(self.inputs.field_template) and \
                    key in self.inputs.field_template:
                template = self.inputs.field_template[key]
            if isdefined(self.inputs.base_directory):
                template = os.path.join(
                    os.path.abspath(self.inputs.base_directory), template)
            else:
                template = os.path.abspath(template)
            
            if (('concatenated_fmri.nii.gz' not in template) and ('filled_t1' not in template)):
                template  = template % (tp, group, key, pid,
                          key, tp, pid)
            elif 'concatenated_fmri.nii.gz' in template:
                template = template % (tp, group, key, pid)
            elif 'filled_t1' in template:
                template = template  %( tp, group, pid, tp, 
                        group, pid, tp, pid)
            filelist = glob.glob(template)
            if len(filelist) == 0:
                msg = 'output key: %s template: %s returned no files' % (
                        key, template)
                if self.inputs.raise_on_empty:
                    raise IOError(msg)
                else:
                    warn(msg)
            else:
                if self.inputs.sort_filelist:
                    filelist = human_order_sorted(filelist)
                outputs[key] = list_to_filename(filelist)
            if any([val is None for val in outputs[key]]):
                outputs[key] = []
            if len(outputs[key]) == 0:
                outputs[key] = None
            elif len(outputs[key]) == 1:
                outputs[key] = outputs[key][0]
        return outputs

class transListInputSpec(BaseInterfaceInputSpec):
    affine = File(exists = True, desc = 'affine')
    warp = File(exists = True,  desc = 'warp')
    

class transListOutputSpec(TraitedSpec):
    transformation_list = traits.List(mandatory = True, 
                                        desc = 'transformation list')

class transList(BaseInterface): 
    output_spec = transListOutputSpec
    input_spec = transListInputSpec

    def _gen_outlist(self):
        affine = self.inputs.affine
        warp = self.inputs.warp
        transformation_list = [affine, warp]
        return transformation_list

    def _run_interface(self, runtime):
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['transformation_list'] = self._gen_outlist()
        return outputs
