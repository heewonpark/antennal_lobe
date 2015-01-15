import matplotlib.pyplot as plt
from matplotlib import pylab

def drawGraph(filename):
    datafile = open(filename,'r')
    data = datafile.readlines()
    nDatas, nColumns = data[0].split(' ')
    nDatas = int(nDatas)
    nColumns = int(nColumns)
    print nDatas, nColumns
    tvec = [0 for i in range(nDatas)]
    vec = [0 for i in range(nDatas)]
    vec2 = [0 for i in range(nDatas)]
    stim_vec =[0 for i in range(nDatas)]
    for i in range(1,nDatas+1):
        #print i
        #print data[i].split('\t')
        tvec[i-1], vec[i-1],vec2[i-1],stim_vec[i-1],dummy = data[i].split('\t')
        tvec[i-1] = float(tvec[i-1])
        vec[i-1] = float(vec[i-1])
        vec2[i-1] = float(vec2[i-1])
        stim_vec[i-1] = float(stim_vec[i-1])
    flg = pylab.figure()
    pylab.plot(tvec, vec,'r')
    pylab.plot(tvec, vec2,'b')
    pylab.plot(tvec, stim_vec)
    #pylab.xlim(200,300)
    pylab.savefig('receptertestrecord.png')
    pylab.show()

drawGraph('receptertestrecord.txt')
