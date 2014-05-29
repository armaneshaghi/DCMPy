from nose.tools import *
from cogpy.lesion import lesion_filling 






def test_lesion_filling():
    
    t1 = '/data/notebook/cogpy/test/t1.nii.gz'
    lesion_map = '/data/notebook/cogpy/test/lesion_map_binary.nii.gz'
    wmp = '/data/notebook/cogpy/test/wmp.nii.gz'
    lesion_filled = '/data/notebook/cogpy/test/t1_lesion_filled.nii.gz'

    import nipype.pipeline.engine as pe
    
    lesion_filler = pe.Node(interface = lesion_filling.LesionFill(),
            name = 'filler')
    lesion_filler.inputs.T1 = t1
    lesion_filler.inputs.lesion_map = lesion_map
    lesion_filler.inputs.wmp_map = wmp
    lesion_filler.run()

