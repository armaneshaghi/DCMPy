from matplotlib import figure
import matplotlib.pyplot as plt
import numpy as np
import warnings
import nibabel as nb
import subprocess
import os

class FS(object):
 
    def __init__(self, volume_file, surface_file, slice_number=170):
        self.volume_file = volume_file
        self.surface_file = surface_file

    def volShow(self): 
        path = self.volume_file
        img = nb.load(path)
        img_data = img.get_data()
        img_shape = img_data.shape
        z_slices = img_shape[2]
        middle_slice = np.divide(z_slices, 2)
        middleToEndRange = z_slices - middle_slice

        interval = np.divide(middleToEndRange, 3)
        lowest_slice = middle_slice - 2 * interval
        fig = plt.figure(figsize = (12, 15))
        for i in range(6):
            f =  fig.add_subplot(3, 3, i + 1)
            slice = lowest_slice + i * interval 
            print slice
            plt.imshow(img_data[:, :, slice],
                    cmap = plt.cm.gray,  aspect = 'auto', 
                    interpolation = 'nearest')
            plt.axis('on')
            plt.title('slice %d' %(slice))
        return self

    def surfaceMask(self): 
        volume = self.volume_file
        surface_file = self.surface_file
        volImg = nb.load(volume)
        #RAS to voxel affine transformation
        vox2ras = np.zeros((4,4))
        #using FS mri_info from shell
        FSHome = os.environ['FREESURFER_HOME']
        #first one was vox2ras
        #WARNING: Freesurefer surface files are in RAS coordinates
        #and are different from Freesurfer volume coordinates
        #RAS coordinate is centered around 
        #www.grahamwideman.com/gw/brain/fs/coords/fscoords.htm
        response = subprocess.check_output(["%s/bin/mri_info" %(FSHome),
                                            "--vox2ras", volume],
                                            stderr=subprocess.STDOUT, 
                                            shell=False)
        response = response.split()
        for i in range(0, 4):
            for j in range(0, 4):
                vox2ras[i, j] = float(response[4*i+j])
        
        volArr = volImg.get_data()
        newVol = np.zeros(volArr.shape)
        coords, faces = nb.freesurfer.read_geometry(surface_file)
        #second getting ras2vox
        ras2vox = np.zeros((4,4))
        response = subprocess.check_output(["%s/bin/mri_info" %(FSHome),
                                            "--ras2vox", volume],
                                            stderr=subprocess.STDOUT, 
                                            shell=False)
        response = response.split()
        for i in range(0, 4):
            for j in range(0, 4):
                ras2vox[i, j] = float(response[4*i+j])
        ### 
        volArr = volImg.get_data()
        newVol = np.zeros(volArr.shape)
        coords, faces = nb.freesurfer.read_geometry(surface_file)
        #applying affine transformation (RAS to voxel)
        #and reconstructing surface on volume 
        
        for i in range(0, coords.shape[0]):
            coordinates = coords[i,:]
            xRAS = coordinates[0]
            yRAS = coordinates[1]
            zRAS = coordinates[2]
 
            coordTranf = np.zeros((4,1))
            coordTranf[0,0] = xRAS
            coordTranf[1,0] = yRAS
            coordTranf[2,0] = zRAS
            coordTranf[3,0] = 1.
            coordTranf = np.dot(ras2vox, coordTranf)
            #surface coordinates are float numbers while volume
            #coordinates are intergers,thus omitting decimal points to 
            #by rounding
            newX = coordTranf[0] 
            newY = coordTranf[1] 
            newZ = coordTranf[2]
            
            xR = int(np.around(newX))
            yR = int(np.around(newY))
            zR = int(np.around(newZ))
            newVol[xR, yR, zR]  = 1
        return newVol



