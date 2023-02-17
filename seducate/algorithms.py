#==================================

#Author Bjorn Burr Nyberg / Sigrid Næsheim
#University of Bergen
#Contact bjorn.nyberg@uib.no
#Copyright 2021

#==================================

'''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import *
import numpy as np
import pandas as pd
import os, random
from numpy import random as rnd
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image 
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage
from matplotlib.offsetbox import AnnotationBbox as abb

def plot_grainsize(startvalue, minvalue, maxvalue, thickness, start_y, sorting='',contact='',structures='',nBeds=3,nSedS=5):
    y = [0] * (((nBeds + 2) * 2))  # Number of values plus start and end value, times two
    y[0] = start_y
    x = [startvalue, startvalue]
    for i in range(nBeds):
        # Append value times nBeds to result list to get blocky look on graph
        value = rnd.randint(minvalue, maxvalue + 1)  # Could have uniform here, to pick float
        x.extend([value] * nBeds)
    if sorting == 'CU':  # = coarsening upwards
        x.extend([maxvalue, maxvalue])
        x.sort()
    elif sorting == 'FU':  # fining upwards
        x.extend([minvalue, minvalue])
        x.sort()
        x.reverse()
    else:
        x.extend([minvalue, minvalue])

    # Add lines
    x, y = add_lines(x, start_y,thickness)

    # Add structures
    curS = place_structures(x, y, structures,nSedS)

    #Add paleocurrent based on sedimentary structures
    curP = paleocurrent(curS)

    l_dict = lithology(x, y)
    # Add erosion
    if contact.lower() == 'erosional':
        x, y = erosion(x, y,maxvalue)

    end_of_y = y[-1]

    return x, y, end_of_y,curS, curP,l_dict


# ## Function to add lines
# Adds horizontal lines when there is a change in grain size. The function generates new values for x and y, based on input x values and the first y value.
#
# #### input
#
# x = a list with x values generated from plot_grainsize
#
# start_y = the first value in y values generated from plot_grainsize
#
# #### Output
# X and y values


def add_lines(x, start_y,thickness):
    res_x = []
    for i in range(len(x) - 1):

        if x[i] == x[i + 1]:
            res_x.append(x[i])
            res_x.append(x[i + 1])

        else:
            res_x.append(0)

    res_y = [start_y]

    for i in range(len(res_x) - 1):
        if res_x[i] == 0:
            res_y.append(res_y[i])


        elif res_x[i] == res_x[i + 1]:
            res_y.append(res_y[i] + thickness)

        else:
            res_y.append(res_y[i])

    return res_x, res_y


# ## Function to add erosion to base
# Adds erosion to base of channels
#
# #### Input
#
# x = x values
#
# y = y values
#
# m (optional) = decides where to place the erosive base
#
# #### Output
# X and y values


def erosion(x, y, m):  # base is the x-value

    # locate grain size at max value in x
    i = x.index(m)

    truncated_x = x[:i + 1]  # truncate log based on erosion
    truncated_y = y[:i + 1]

    rest_x = x[i:]
    rest_y = y[i:]

    wave = [n for n in np.arange(0, 100, 0.1)][::-1]  # create a sin wave
    s = [(v / 8.0) + truncated_y[-1] for v in np.sin(wave)][::-1]
    wave = [(n * truncated_x[-1]) / max(wave) for n in wave]

    truncated_x.extend(wave)
    truncated_y.extend(s)
    truncated_x.extend(wave[::-1])
    truncated_y.extend(s[::-1])

    return truncated_x + rest_x, truncated_y + rest_y


# ## Function to place sedimentary structures
# This function generates a dictionary with evenly spaced and random y values for placement in the log and which structure to place there based on the x value in the grain size graph and the current env.
#
#
# #### Input
#
# x = x values
#
# y = y values
#
# s = sedimentary structures dictionary
#
# #### Output
#
# Returns a dictionary with y value as key and structure as value


def place_structures(x, y, s, nS):

    res_dict = {}


    # Check if env have erosive base
    # if env == 'fluvial' or 'alluvial' or 'deepmarine' or 'turbidite':
    #     ytmp = []
    #     xtmp = []
    #     # Remove floats from sine wave
    #     for i in range(len(y)):
    #         if type(y[i]) == int:
    #             ytmp.append(y[i])
    #             xtmp.append(x[i])

    #     # number of structures
    #     num = round(len(ytmp) / 3)

    #     # Get random, evenly distributed indexes
    #     ind = np.round(np.linspace(0, len(ytmp) - 1, num)).astype(int)

    #     # Get values from y from indexes
    #     y_values = []

    #     for i in ind:
    #         # if type(y[i])==int:
    #         y_values.append(ytmp[i])
    #     # Remove duplicates to avoid overlapping structures
    #     y_values = list(set(y_values))

    #     # Get corresponding x values, used in choice of structure
    #     x_values = []
    #     for i in ind:
    #         x_values.append(xtmp[i])
    # else:
    # Number of structures
    num = nS#round(len(y) / 3)

    # Get num numbers of evenly spaced indexes from y
    ind = np.round(np.linspace(0, len(y) - 1, num)).astype(int)

    # Get values from y from indexes
    y_values = []
    for i in ind:
        # if type(y[i])==int:
        y_values.append(y[i])

    # Get corresponding x values, used in choice of structure
    x_values = []
    for i in ind:
        x_values.append(x[i])

    # zip together x and y values
    d = dict(zip(y_values, x_values))

    for i, j in d.items():
        if type(j) == int:
            structures = s[j].split(',')
            c = rnd.choice(structures)
            res_dict[i + 1] = str(c)

    # removing duplictate lag and flute structures since they normally just appear at the bottom of a layer
    res_dict1 = {}

    for key, value in res_dict.items():
        if value == 'lag' and value not in res_dict1.values():
            res_dict1[key] = value
        elif value == 'flute' and value not in res_dict1.values():
            res_dict1[key] = value
        if value in ['lag','flute','no']:
            continue
        else:
            res_dict1[key] = value

    return res_dict1


# ## Function to place lithology


def lithology(x, y):

    lith_dict = {0:'none', 1: 'clay', 2: 'silt', 3: 'sand', 4: 'sand', 5: 'sand', 6: 'sand', 7: 'sand',8:'cong',9:'cong',10:'cong'}

    res_dict = {}
    # Get only unique y-values
    y_values = set(y)

    for i in y_values:
        x_value = x[y.index(i)]
        res_dict[i] = lith_dict[x_value]

    return res_dict


def paleocurrent(s_dict):
    '''
    Dictionary containing the different types of paleocurrent images (e.g. directional or bidirectional).
    Only allow paleocurrent measurements based on specific sedimentary structures.
    '''
    paleo_dict = {
        'crosslamination': 'directional',
        'currentripples': 'directional',
        'mud drapes':'bidirectional'
                  }

    res_dict = {}

    for k,v in s_dict.items():
        if v in paleo_dict:
            res_dict[k] = paleo_dict[v]

    # Changing the first key from 0 to 2 so the arrow wont overlap the bottom border of the plot.
    res_dict = {2 if k < 3 else k: v for k, v in res_dict.items()}

    return res_dict


# ## Plotting function
# Function to generate the actual log and plot everything.
#
# #### Input
#
# x = x values to plot grain size graph
#
# y = y values to plot grain size graph
#
# envs = to use as input in place_structures to get a dict with structures


def plotting(x, y, angle, pc_dict, s_dict, l_dict, outPath,dname):

    fig = plt.figure(figsize=(8, 10))
    gs = fig.add_gridspec(5, 5, wspace=0)
    ax1 = fig.add_subplot(gs[:, 0:1])  # [row,column]
    ax2 = fig.add_subplot(gs[:, 1:4])
    ax3 = fig.add_subplot(gs[:, -1])
    ax2.plot(x, y, color='black')

    labels = ['', 'Clay', 'Si', 'Vf', 'F', 'M', 'C', 'Vc','Gran','Peb','Cob','']
    plt.setp([ax1, ax2, ax3], yticks=[], xticks=[0, 1, 2, 3, 4, 5, 6, 7, 8,9,10,11], xticklabels=labels)
    ax1.set(xticks=[])
    ax3.set(xticks=[])
    ax3.title.set_text('Structures')
    ax2.title.set_text('Grain Size')
    ax1.title.set_text('Lithology')

    ax3.set_ylim(-1, max(y) + 3)
    ax2.set_ylim(-1, max(y) + 3)
    ax1.set_ylim(-1, max(y) + 3)
    fig.suptitle('Log #{l}'.format(l=os.path.basename(outPath)[:-4]), fontsize=20)

    for i, j in s_dict.items():
        if j != '':
            image = mpimg.imread(os.path.join(dname,'structures', str(j) + '.jpg'))
        else:
            image = mpimg.imread(os.path.join(dname, 'structures','no.jpg'))
        imagebox = OffsetImage(image, zoom=0.5)
        ab = abb(imagebox, (5.5, i), frameon=False)  # Placing the figure
        ax3.add_artist(ab)

    for i, j in l_dict.items():
        try:
            image = mpimg.imread(os.path.join(dname,'lithology', str(j) + '.jpg'))
            imagebox = OffsetImage(image, zoom=0.082)
            ab = abb(imagebox, (5.5, i), frameon=False)  # Placing the figure
            ax1.add_artist(ab)
        except Exception:
            continue

    if angle:
        for i, j in pc_dict.items():
            if random.random() > 0.5: #Plot 50% of paleocurrents
                image = Image.open(os.path.join(dname, 'paleocurrent', str(j) + '.jpg'))
                value = angle - random.randint(-25, 25)
                if value > 360:
                    value =- 360
                rotated = image.rotate(-value, expand=True, fillcolor='white')
                imagebox = OffsetImage(rotated, zoom=0.03, )
                ab = abb(imagebox, (10.3, i), frameon=False)  # Placing the figure
                ax2.add_artist(ab)
    if '.svg' in outPath:
        plt.savefig(outPath, format='svg')
    else:
        plt.savefig(outPath,format='jpg')