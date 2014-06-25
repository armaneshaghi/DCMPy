from matplotlib import figure
import matplotlib.pyplot as plt
import numpy as np
import warnings
import nibabel as nb
import subprocess
import os

class FS(object):
 
    def __init__(self, subject_name, slices):
        """
        subject_name: string indicating subject name as seen in 
        Freesurfer subjects directory (shell $SUBJECTS_DIR variable)
        slices: numpy array of size n by 3 indicating n slices in axial,
        sagittal and coronal sections
        """

        self.slices = slices
        self.subject_name = subject_name

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
            plt.imshow(img_data[:, :, slice],
                    cmap = plt.cm.gray,  aspect = 'auto', 
                    interpolation = 'nearest')
            plt.axis('on')
            plt.title('slice %d' %(slice))
        return self

    def _surfaceMask(self, volume, surface_file): 
        volImg = nb.load(volume)
        #RAS to voxel affine transformation
        vox2ras = np.zeros((4,4))
        #using FS mri_info from shell
        FSHome = os.environ['FREESURFER_HOME']
        #first one was vox2ras
        #WARNING: Freesurefer surface files are in RAS coordinates
        #and are different from Freesurfer volume coordinates
        #RAS coordinate is centered around 
        response = subprocess.check_output(["%s/bin/mri_info" %(FSHome),
                                            "--vox2ras-tkr", volume],
                                            stderr=subprocess.STDOUT, 
                                            shell=False)
        response = response.split()
        for i in range(0, 4):
            for j in range(0, 4):
                vox2ras[i, j] = float(response[4*i+j])
        vox2ras = np.matrix(vox2ras) 
        invT1orig = np.linalg.inv(vox2ras)

        volArr = volImg.get_data()
        newVol = np.zeros(volArr.shape)
        coords, faces = nb.freesurfer.read_geometry(surface_file) 
        volArr = volImg.get_data()
        newVol = np.zeros(volArr.shape)
        coords, faces = nb.freesurfer.read_geometry(surface_file)
        for i in range(0, coords.shape[0]):
            coordinates = coords[i,:]
            R = coordinates[0]
            A = coordinates[1]
            S = coordinates[2]
            RASmatrix = np.matrix([R, A, S, 1])
            RASmatrixT = np.transpose(RASmatrix)
            VoxCRS = invT1orig * RASmatrixT
            #surface coordinates are float numbers while volume
            #coordinates are intergers,thus omitting decimal points
            #by rounding
            xVol = VoxCRS[0,0]
            yVol = VoxCRS[1,0]
            zVol = VoxCRS[2,0]
            xR = int(np.around(xVol))
            yR = int(np.around(yVol))
            zR = int(np.around(zVol))
            newVol[xR, yR, zR]  = 1
        return newVol

    def _coronalShow(self, data, slice, overlay = False,
            surface = None):
        
        """
        function to plot T1 volume and pial/WM surfaces
        data: nibabel loaded numpy array
        slice: integer indicating number of the desired slice
        overlay: boolean indicating whether the data is an overlay or not
        surface: string indicating what kind of surface is overlay (wm or pial)

        """

        if not overlay:
            plt.imshow(np.rot90(data[:, :, slice], k=3),
                        cmap = plt.cm.gray ,  aspect = 'auto', 
                        interpolation = 'nearest')
        if overlay:
            overlayD = np.ma.masked_array(data, data == 0)
            if surface =='wm':
                plt.imshow(np.rot90(overlayD[:,:, slice], k=3),
                           cmap = plt.cm.Reds, vmax = 1.2, vmin = 0,
                           aspect = 'auto', 
                           interpolation = 'nearest')
            if surface == 'pial':
                plt.imshow(np.rot90(overlayD[:, :, slice], k=3),
                           cmap = plt.cm.hot, vmax = 1.2, vmin = 0,
                           aspect = 'auto', 
                           interpolation = 'nearest')
        return None

    def _axialShow(self, data, slice, overlay = False,
            surface = None):
        """
        similar to _coronalshow
        """
        if not overlay:
            plt.imshow(np.rot90(data[:, slice, :], k=1),
                        cmap = plt.cm.gray ,  aspect = 'auto', 
                        interpolation = 'nearest')

        if overlay: 
            overlayD = np.ma.masked_array(data, data == 0)
            if surface =='wm':
                plt.imshow(np.rot90(overlayD[:, slice, :], k=1),
                           cmap = plt.cm.Reds, vmax = 1.2, vmin = 0,
                           aspect = 'auto', 
                           interpolation = 'nearest')

            if surface == 'pial':
                plt.imshow(np.rot90(overlayD[:, slice, :], k=1),
                           cmap = plt.cm.hot, vmax = 1.2, vmin = 0,
                           aspect = 'auto', 
                           interpolation = 'nearest')


        return None

    def _sagitalShow(self, data, slice, overlay = False,
            surface = None):
        """
        similar to _coronalshow
        """
        if not overlay:
            plt.imshow(np.rot90(data[slice, :, :], k=0),
                        cmap = plt.cm.gray ,  aspect = 'auto', 
                        interpolation = 'nearest')
        if overlay: 
            overlayD = np.ma.masked_array(data, data == 0)                      
            if surface =='wm':
                plt.imshow(np.rot90(overlayD[slice,:, :], k=0),
                           cmap = plt.cm.Reds, vmax = 1.2, vmin = 0,
                           aspect = 'auto', 
                           interpolation = 'nearest')

            if surface == 'pial':
                plt.imshow(np.rot90(overlayD[slice,:, :], k=0),
                           cmap = plt.cm.hot, vmax = 1.2, vmin = 0,         
                           aspect = 'auto',                                 
                           interpolation = 'nearest')                       
                 
        return None

    def superimpose(self):
        """
        main function to loop aroung all slices and plot images
        """

        slices = self.slices
        subId = self.subject_name
        subDir = os.environ['SUBJECTS_DIR']
        orig = os.path.join(subDir, subId, 'mri/orig.mgz') 
        lhPial = os.path.join(subDir, subId, 'surf/lh.pial')
        rhPial = os.path.join(subDir, subId, 'surf/rh.pial')
        lhWm = os.path.join(subDir, subId, 'surf/lh.white')
        rhWm = os.path.join(subDir, subId, 'surf/rh.white')
        #projecting surface to volume
        lhPialD = self._surfaceMask(volume = orig, surface_file = lhPial)
        rhPialD = self._surfaceMask(volume = orig, surface_file = rhPial)
        lhWmD = self._surfaceMask(volume = orig, surface_file = lhWm)
        rhWmD = self._surfaceMask(volume = orig, surface_file = rhWm)
        orig_data = nb.load(orig).get_data()
        totSlices = slices.shape[0] + slices.shape[1]
        rows = np.round(totSlices/2)
        columns  = totSlices - rows
        #getting slice numbers for each view
        axialSlices =  slices[:, 0]
        sagitalSlices = slices[:, 1]
        coronalSlices = slices[:, 2]
       
        #starting from axial
        figNo = 0
        width = columns * 20
        height = rows * 20
        fig = plt.figure(figsize = (width, height))
        print '%s\n' % (subId)
        for slice in axialSlices:
            figNo += 1
            f =  fig.add_subplot(rows, columns, figNo)
            #drawing main volume
            self._axialShow(data = orig_data, slice = slice)
            #drawing overlays: lh
            self._axialShow(data = lhPialD, slice = slice, overlay = True,
                    surface = 'pial')
            self._axialShow(data = lhWmD, slice = slice, overlay = True, 
                    surface = 'wm')
            #drawing overlays: rh
            self._axialShow(data = rhPialD, slice = slice, overlay = True,
                    surface = 'pial')
            self._axialShow(data = rhWmD, slice = slice, overlay = True, 
                    surface = 'wm')
        for slice in coronalSlices:
            figNo += 1
            f =  fig.add_subplot(rows, columns, figNo)
            #drawing main volume
            self._coronalShow(data = orig_data, slice = slice)
            #drawing overlays: lh
            self._coronalShow(data = lhPialD, slice = slice, overlay = True,
                    surface = 'pial')
            self._coronalShow(data = lhWmD, slice = slice, overlay = True, 
                    surface = 'wm')
            #drawing overlays: rh
            self._coronalShow(data = rhPialD, slice = slice, overlay = True,
                    surface = 'pial')
            self._coronalShow(data = rhWmD, slice = slice, overlay = True, 
                    surface = 'wm')


        for slice in sagitalSlices:
            figNo += 1
            f =  fig.add_subplot(rows, columns, figNo)
            #drawing main volume
            self._sagitalShow(data = orig_data, slice = slice)
            #drawing overlays: lh
            self._sagitalShow(data = lhPialD, slice = slice, overlay = True,
                     surface = 'pial')
            self._sagitalShow(data = lhWmD, slice = slice, overlay = True, 
                     surface = 'wm')
            #drawing overlays: rh
            self._sagitalShow(data = rhPialD, slice = slice, overlay = True,
                     surface = 'pial')
            self._sagitalShow(data = rhWmD, slice = slice, overlay = True, 
                     surface = 'wm')
        return self
