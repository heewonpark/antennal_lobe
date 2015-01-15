import matplotlib.pyplot as plt
from matplotlib import pylab
import sys

def drawGraph(filename):
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
    pylab.show()


if len(sys.argv) is 1:
    print "NO FILENAME"
else:
    Filename = sys.argv[1]
    drawGraph(Filename)
