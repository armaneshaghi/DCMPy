from matplotlib import figure
import matplotlib.pyplot as plt
import numpy as np
import warnings
import nibabel as nb


class image(object):
 
    def __init__(self, path, slice_number=170,volume_file, surface_file):

        self.path = path
        self.surface =  surface_file
        return self

    def volShow(self):
 
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
        coords, faces = nb.freesurfer.read_geometry(surface_file)
        for coordinates in coords.shape[0]:
            x = coordinates[0]
            y = coordinates[1]
            z = coordinates[2]


