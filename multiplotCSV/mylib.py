#!/usr/bin/python
# -*- coding:utf-8 -*-
# TROUBLE SHOOTING: 
#  if you get an error like "ValueError: unknown locale: UTF-8"
#  then first type in the terminal: "export LC_ALL=en_US.UTF-8"

# nicolas.bredeche(at)upmc.fr
# Last revision: 2017-01-30 14h48

import os
import sys
import datetime
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pl

try:
    import seaborn as sns
except ImportError:
    print "[Warning]: seaborn package not available"
else:
    sns.set() #Charge la conf de seaborn
    sns.set_palette('colorblind')  # évidemment

## agg backend is used to create plot as a .png file
#mpl.use('agg')   # removed (caused: "UserWarning:  This call to matplotlib.use() has no effect")

debug = False


def getContentFromFile( filename ):
    fichier = open(filename)
    lines = fichier.readlines()
    fichier.close()
    return lines

def getLinesWithPrefix( lines, prefix, removePrefix = False):
    retLines = []
    for l in lines:
        if l[0:len(prefix)] == prefix:
            if removePrefix == True:
                retLines.append(l[len(prefix):].replace("\n",""))
            else:
                retLines.append(l).replace("\n","")
    return retLines

def parseLinesToArrayOfValues ( rawlines ):
    lines = []
    for l in rawlines:
        if len(l) != 0 and l[0] != "#":
            l = l.split(",")
            l = map(float, l)
            lines.append(l)
    return lines

def getTimestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M")

def getMaximumLength ( myList ): # return the length of maximally lengthy sub-element (list or string)
    return max( len(l) for l in myList )   # or: max(map(len, myList))

# ###
# display data with matplotlib (+ write PDF)
# many examples: http://matplotlib.org/gallery.html#
# code below adapted from: http://blog.bharatbhole.com/creating-boxplots-with-matplotlib/
# ###
def traceData( x, y, type="single", title="", xLabel="", yLabel="", xlimMin=-1, xlimMax=-1, ylimMin=-1, ylimMax=-1, legendLabel="", locLegend='upper right', autoscaling=False, outputFilename="empty"):
    
    #pl.gca().set_color_cycle(['red', 'green', 'blue', 'orange', 'violet', 'darkblue', 'black','purple','cyan','brown']) # force cycle through specified colors

    # Create a figure instance
    fig = pl.figure(1, figsize=(9, 6))

    # Create an axes instance
    ax = fig.add_subplot(111)

    # plot data
    if type == "single":
        ax.plot(x, y)
    elif type == "multi":
        ax.boxplot(y)
        ax.set_xticklabels(x)
    
    # Remove top axes and right axes ticks
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_autoscale_on(autoscaling)

    # Add labels and legend
    pl.xlabel(xLabel)
    pl.ylabel(yLabel)

    if title == "":
        pl.title(getTimestamp())
    else:
        pl.title(title)
        if legendLabel != "":
            pl.legend(legendLabel, loc=locLegend)

    if xlimMin != -1 and xlimMax != -1:
        pl.xlim(xlimMin, xlimMax)
    if ylimMin != -1 and ylimMax != -1:
        pl.ylim(ylimMin, ylimMax)

    # Save the figure
    
    if outputFilename == "empty":
        outputFilename = "graph_"+getTimestamp()+".pdf"
    
    fig.savefig(outputFilename, format="pdf", bbox_inches='tight')
    
    # Display
    pl.show() # mandatory: call after savefig(.)

