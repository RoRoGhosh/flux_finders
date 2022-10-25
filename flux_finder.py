#Ok this is for finding the fluxes of all found objects in all fits images in a given directory
#Values may have to be adjusted  to find all objects in an image
#This will also output all objects found so you can check if its working correctly
#Written by Rohit Ghosh 10/2022

from turtle import color
import numpy as np
import os
import sep
import fitsio
import matplotlib.pyplot as plt
from matplotlib import rcParams
from pathlib import Path
from matplotlib.patches import Ellipse

rcParams['figure.figsize'] = [10., 8.]

#user to input directory to be searched for .h5 files and convert
print("Enter directory to be analysed:")
directory_name = input()

#list of .fits paths
paths = Path(directory_name).glob('**/*.fits',)

#Find all .h5 files in the directory and its subdirectories
for path in paths:
    #create name of converted file using original file name for identification purposes
    name = os.path.splitext(path)[0] + "_objects_identified" + ".png"
    
    # read image into standard 2-d numpy array
    data = fitsio.read(path)

    # measure a spatially varying background on the image
    bkg = sep.Background(data)

    # subtract the background
    data_sub = data - bkg

    # extract the objects
    objects = sep.extract(data_sub, 1.5, err=bkg.globalrms)

    # plot background-subtracted image
    fig, ax = plt.subplots()
    m, s = np.mean(data_sub), np.std(data_sub)
    im = ax.imshow(data_sub, interpolation='nearest', cmap='gray',
                vmin=m-s, vmax=m+s, origin='lower')

    # plot an ellipse for each object
    for i in range(len(objects)):
        e = Ellipse(xy=(objects['x'][i], objects['y'][i]),
                    width=4*objects['a'][i],
                    height=4*objects['b'][i],
                    angle=objects['theta'][i] * 180. / np.pi)
        e.set_facecolor('none')
        e.set_edgecolor('red')
        ax.add_artist(e)
        plt.text(objects['x'][i], objects['y'][i], "{:d}".format(i), color = 'red')
    
    # save the image with objects identified
    plt.savefig(name)
    
    # get flux data
    flux, fluxerr, flag = sep.sum_circle(data_sub, objects['x'], objects['y'],
                                     3.0, err=bkg.globalrms, gain=1.0)

    # save flux data in a txt file
    text_name = os.path.splitext(path)[0] + "_flux_data" + ".txt"
    with open(text_name, "w") as text_file:
        for i in range(len(objects)):
           print("object {:d}: flux = {:f} +/- {:f}".format(i, flux[i], fluxerr[i]), file = text_file)
