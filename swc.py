#! /usr/bin/python
# coding: utf-8
# swc.py

import numpy as np
class swc(object):
    n = 0    #Sample Number
    T = 0    #Structure Identifier
    x = 0.0  #x position
    y = 0.0  #y position
    z = 0.0  #z position
    R = 0.0  #Radius
    P = 0    #Parent Sample Number

def read(filename):
    swcFile = open(filename, 'r')
    Lines = swcFile.readlines()
    Header = [None for _ in range(15)]
 
    i = 0
    while (Lines[0][0] == '#') or (Lines[0][0] == "\n"):
        Header[i] = Lines[0] 
        i+=1
        del Lines[0]
    #print swchead
    #print swcdata
    #seclist is section list
    seclist = [swc() for _ in range(len(Lines))]

    #print len(Lines)
    for i in range(len(Lines)):
        line = Lines[i].split()
        seclist[i].n = int(line[0])
        seclist[i].T = int(line[1])
        seclist[i].x = np.float64(line[2])
        seclist[i].y = np.float64(line[3])
        seclist[i].z = np.float64(line[4])
        seclist[i].R = np.float64(line[5])
        seclist[i].P = int(line[6].rstrip('\n'))
        #print "%d %d %f %f %f %f %d"%(seclist[i].n,seclist[i].T,seclist[i].x,seclist[i].y,seclist[i].z,seclist[i].R,seclist[i].P)
    swcData =[Header, seclist] 
    swcFile.close()
    return swcData

def write(filename, swc, header):
    swcFile = open(filename, 'w')
    swcFile.writelines(header)
    for i in range(len(swc)):
        swcdata_ = "%d %d %f %f %f %f %d\n" % (swc[i].n, swc[i].T, swc[i].x, swc[i].y, swc[i].z, swc[i].R, swc[i].P)
        swcFile.writelines(swcdata_)
    swcFile.close()

# Find Synase Region from swc file
# append dendrite number which is Synapse Region type in SynapseRegionList
def findSynapseRegion(cell, srlist):
    #srlist means Synapse Region List. シナプス領域のコンパートメント番号を入れる
    counter = 0
    for i in range(int(cell.SectionNum)):
        parentID = int(cell.pID.x[i])
	parentType = int(cell.Type.x[parentID])
        cellType = int(cell.Type.x[i])
        if((cellType == 7) and (parentType == 7)):
            #print parentID, parentType, cellType
            srlist.append(i)
            counter +=1
    print counter
