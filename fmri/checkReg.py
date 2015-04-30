import nibabel as nb
import numpy as np
import os
import matplotlib.pyplot as plt
import subprocess

def fsfastCheck(subject, average = 'fsaverage',
            fsfastDir, volume_path, register_path,
            slices):
   """
   Quality assurance of each subject's functional
   MRI time series to the average template. Usually is run
   after preprocessing with preproc-sess in Freesurfer to check 
   whether registration between fmri volume and surfaces are correct.
    
   Options:
    
   average = the average template (subject) one uses
   for registartion, default is fsaverage. You need to 
   change this value if you have used mri_make_average
   to make a customized average subject out of freesurfer 
   routine.
   
   subject = a  string value for subject name used during recon-all
   and fsfast pre processing analysis (recon-all and preproc-sess)
   
   fsfastDir = directory for fsfast, whcih contains preprocessed 
   data with preproc-sess.
   
   volume_path = FMRI volume on which surfaces will be projected for 
   visualization (string). Usually from fsfast directory.
   
   register_path = register.dat file produced by tkregister during
   within subject intermodality registration (6dof in fsfast)
   
   slices = numpy array of n by 3 slices in 3 directions of axial
   sagital and coronal.
   """ 
   
   FSHome = os.environ["FREESURFER_HOME"]
   response = subprocess.check_output(["{FSHome}/bin/mri_info".format{home = FSHome},
                                         "--vox2ras-tkr", volume_path],
                                         stderr=subprocess.STDOUT,
                                         shell=False)

   response = response.split()
   vox2ras = np.zeros((4,4))

   for i in range(0, 4):
       for j in range(0, 4):
           vox2ras[i, j] = float(response[4*i+j])
   vox2ras = np.matrix(vox2ras)
   invvox2ras = np.linalg.inv(vox2ras)
   reg = np.zeros((4,4))
   #read linear transformation matrix
   with open(register_path) as registerdat:
       lines = registerdat.readlines()
       lines = lines[4:8]
       #remove extra characters such as \n
       for number, line in enumerate(lines):
           lines[number] = line.strip()

       for i in range(0, 4):
           splitted = lines[i].split()
           for j in range(0, 4):
               reg[i, j] = float(splitted[j])
   #converting from numpy array to numpy matrix 
   #for subsequent linear algebra analysis

   regMatrix = np.matrix(reg)
   subjects_dir = os.environ["SUBJECTS_DIR"]
   #subjects_dir and subject_dir are different!
   subject_dir = '{subjects_dir}/{subject}/surf/'.format(
           subjects_dir = subjects_dir, subject = subject)

   rhPial = os.path.join(subject_dir, 'rh.pial')
   lhPial = os.path.join(subject_dir, 'lh.pial')
   rhWm = os.path.join(subject_dir, 'rh.white')
   lhWm = os.path.join(subject_dir, 'lh.white')

   #projecting surface to volume
   lhPialD = surface_mask_fsfast(volume = volume_path,
           surface = lhPial,
           regMatrix = regMatrix)

   rhPialD = surface_mask_fsfast(volume = volume_path,
           surface = rhPial,
           regMatrix = regMatrix)

   lhWmD = surface_mask_fsfast(volume = volume_path,
           surface = lhWm,
           regMatrix = regMatrix)

   rhWmD =  surface_mask_fsfast(volume = volume_path,
           surface = rhWm,
           regMatrix = regMatrix)

   totSlices = slices.shape[0] + slices.shape[1]
   rows = np.round(totSlices/2)
   columns  = totSlices - rows
   #getting slice numbers for each view
   axialSlices =  slices[:, 0]
   sagitalSlices = slices[:, 1]
   coronalSlices = slices[:, 2]
   
   #plotting surface vertices on the mean volume
   figNo = 0
   width = columns * 20
   height = rows * 20
   fig = plt.figure(figsize = (width, height))
   #we need images in form of data from nibabel
   volumeData = nb.load(volume_path)
   volumeData = volumeData.get_data()

   for slice in axialSlices:
       figNo += 1
       f =  fig.add_subplot(rows, columns, figNo)
       fig.suptitle('%s' %(subject_name), fontsize=35, fontweight='bold')
       #drawing main volume
       _axialShow(data = orig_data, slice = slice)
       #drawing overlays: lh
       _axialShow(data = lhPialD, slice = slice, overlay = True,
               surface = 'pial')
       _axialShow(data = lhWmD, slice = slice, overlay = True, 
               surface = 'wm')
       #drawing overlays: rh
       _axialShow(data = rhPialD, slice = slice, overlay = True,
               surface = 'pial')
       _axialShow(data = rhWmD, slice = slice, overlay = True, 
               surface = 'wm')
   for slice in coronalSlices:
       figNo += 1
       f =  fig.add_subplot(rows, columns, figNo)
       #drawing main volume
       _coronalShow(data = orig_data, slice = slice)
       #drawing overlays: lh
       _coronalShow(data = lhPialD, slice = slice, overlay = True,
               surface = 'pial')
       _coronalShow(data = lhWmD, slice = slice, overlay = True, 
               surface = 'wm')
       #drawing overlays: rh
       _coronalShow(data = rhPialD, slice = slice, overlay = True,
               surface = 'pial')
       _coronalShow(data = rhWmD, slice = slice, overlay = True, 
               surface = 'wm')


   for slice in sagitalSlices:
       figNo += 1
       f =  fig.add_subplot(rows, columns, figNo)
       #drawing main volume
       _sagitalShow(data = orig_data, slice = slice)
       #drawing overlays: lh
       _sagitalShow(data = lhPialD, slice = slice, overlay = True,
                surface = 'pial')
       _sagitalShow(data = lhWmD, slice = slice, overlay = True,
                surface = 'wm')
       #drawing overlays: rh
       _sagitalShow(data = rhPialD, slice = slice, overlay = True,
                surface = 'pial')
       
   plt.close()
   plt.clf()
   plt.cla()
   return None

def surface_mask_fsfast(surface, volume,
        regMatrix, invvox2ras ):
   """
   Returns projected surface on as a mask (binary, values of 
   only 0 and 1), volume.
  
   Options:

   surface = path to surface file (pial, wm for example).
  
   volume = path to volume (fmri volume for fsfast)

   regMatrix = affine tranformation matrix produced as part of
   fsfast or independently via tkregister. 
   
   invvox2ras = Inverse matrix of mri_info -vox2ras-tkr output
   """

   volume = nb.load(volume_path)
   volumeData = volume.get_data()
   volumeMean = np.mean(volumeData, axis = 3)
   newVol = np.zeros(volumeMean.shape)

   coords, faces = nb.freesurfer.read_geometry(surface)
   for i in range(0, coords.shape[0]):
       coordinates = coords[i,:]
       R = coordinates[0]
       A = coordinates[1]
       S = coordinates[2]
       RASmatrix = np.matrix([R, A, S, 1])
       RASmatrixT = np.transpose(RASmatrix)
       CRS = invvox2ras * regMatrix * RASmatrixT
       #by rounding
       xVol = CRS[0,0]
       yVol = CRS[1,0]
       zVol = CRS[2,0]
       xR = int(np.around(xVol))
       yR = int(np.around(yVol))
       zR = int(np.around(zVol))
       newVol[xR, yR, zR]  = 1
   return newVol

