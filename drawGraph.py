#! /usr/bin/python
import matplotlib.pyplot as plt
from matplotlib import pylab
import sys
import os.path

def drawGraph(filename, show):
    datafile = open(filename,'r')
    data = datafile.readlines()
    nDatas, nColumns = data[0].split(' ')
    nDatas = int(nDatas)
    nColumns = int(nColumns)
    print nDatas, nColumns
    vec = [[0 for i in range(nDatas)] for j in range(nColumns)]
    dummy = []
    for i in range(0,nDatas):
        #print i
        #print data[i].split('\t')
        dummy = data[i+1].split('\t')
        for j in range(nColumns):
            #print j, dummy[j]
            vec[j][i]=float(dummy[j])

    flg = pylab.figure()
    for j in range(1,nColumns):
        pylab.plot(vec[0], vec[j])
    pylab.ylim(-80, 80)

    tmp = filename.rsplit('.',1)
    imgFilename = "%s.png"%tmp[0]
    #print imgFilename, tmp
    pylab.savefig(imgFilename)
    if(show==True):
        pylab.show()
    

if len(sys.argv) is 1:
    print "NO FILENAME"
elif len(sys.argv) is 2:
    if(os.path.isfile(sys.argv[1])):
        drawGraph(sys.argv[1],1)
    elif(os.path.isdir(sys.argv[1])):
        target_dir = os.path.normpath(sys.argv[1])
        for fname in os.listdir(target_dir):
            full_dir = os.path.join(target_dir,fname)
            if(os.path.isfile(full_dir)):
                ext = os.path.splitext(full_dir)
                if(ext[1] == '.txt'):
                    print full_dir                    
                    drawGraph(full_dir,0)
    else:
        print "Wrong directory or filename"
else:
    print "Wrong input"

"""
elif len(sys.argv) is 2:
    Filename = sys.argv[1]
    drawGraph(Filename)
elif len(sys.argv) is 3:
    target_dir = os.path.normpath(sys.argv[2])
    if((sys.argv[1] = '-r')&os.path.exists(target_dir):
"""    
       
        
