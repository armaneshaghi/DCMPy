from matplotlib import figure
import matplotlib.pyplot as plt
import numpy as np
import warnings
import nibabel as nb


class image(object):

    def show(self, path, slice_number = 170):
        img = nb.load(path)
        img_data = img.get_data()
        fig = plt.figure(figsize = (12, 15))
        base_slice = slice_number - 30
        for i in range(6):
            f =  fig.add_subplot(3, 3, i + 1)
            slice = base_slice + i * 10 
            plt.imshow(np.rot90(img_data[:, :, slice]),
                    cmap = plt.cm.gray,  aspect = 'auto', 
                    interpolation = 'nearest')
            plt.axis('off')
            plt.title('slice %d' %(slice))
