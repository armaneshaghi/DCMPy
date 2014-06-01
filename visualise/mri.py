from matplotlib import figure
import matplotlib.pyplot as plt
import numpy as np
import warnings
import nibabel as nb


class image(object):

    def show(self, path, slice_number = 170):
        img = nb.load(path)
        img_data = img.get_data()
        fig = plt.figure()
        for i in range(6):
            f =  fig.add_subplot(1, 2, i + 1)
            plt.imshow(np.rot90(img_data[:, :, slice_number]),
                    cmap = plt.cm.gray, 
                    interpolation = 'nearest')
            plt.axis('off')
            plt.title('Image')
