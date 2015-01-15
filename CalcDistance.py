# coding: utf-8

######################################################################################
# 2015.01.13 By Heewon Park
# SWCファイルのタイプが7（Synapse Region）の場合、コンパートメント間の距離を計算する
# 計算した距離をソートし、ランダムでシナプスの候補を抽出するプログラム
#
######################################################################################

from neuron import h
import neuron as nrn
import os.path
import numpy as np
import csv
import operator
import random

import swc
nrn.load_mechanisms("./mod")
h.load_file("CellSwc_Ver2.hoc")

def CalcDistance(cmpt1, cmpt2):
    #cmpt means compartment
    cmpt1.push()
    sr1 = h.SectionRef(sec=cmpt1)
    x1 = h.x3d(0.5)
    y1 = h.y3d(0.5)
    z1 = h.z3d(0.5)
    h.pop_section()

    cmpt2.push()
    sr2 = h.SectionRef(sec=cmpt2)
    x2 = h.x3d(0.5)
    y2 = h.y3d(0.5)
    z2 = h.z3d(0.5)
    h.pop_section()

    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2
    distance = dx*dx + dy*dy + dz*dz
    
    #if(distance < 100.0):
    #    print "pos %f %f %f %f %f %f dist %f"%(x1, y1, z1, x2, y2, z2,distance)
    return distance

def writeDistance(cell1, srlist1, cell2, srlist2, filename):
    f = open(filename, 'w')
    cnt = 0
    tmpdist = 0
    for sr1 in srlist1:
        cell1n = h.secname(sec=cell1.Dend[sr1])
        #print cell1.Type[sr1]
        for sr2 in srlist2:
            #print cell2.Type[sr2]
            cell2n = h.secname(sec=cell2.Dend[sr2])
            #            print cell1n, cell2n
            dist = CalcDistance(cell1.Dend[sr1], cell2.Dend[sr2])
            s = "%s,%s,%f\n"%(cell1n, cell2n, dist)
            f.write(s)
    f.close()

#----------------------------------                                                                     
# def : sort csv                                                                                        
# 
# sort 'data.csv' from h.getcandidate()
#'data.csv' = (secname, secname, distance)            
# write 'sorted.csv'                def sortCsv(csvfile):
def sortCsv(csvfile):    
    list = []
    fh = open(csvfile, 'rb')
    sortedfile = csvfile.replace("dist","sorted")
    fw = open(sortedfile, 'wb')
    reader = csv.reader(fh)
    writer = csv.writer(fw)
    for row in reader:
        list.append(row)
    #list.sort(key = operator.itemgetter(2))
    list.sort(cmp = lambda x,y: cmp(float(x[2]),float(y[2])))
    for elem in list:
        writer.writerow(elem)
    fh.close()
    fw.close()
    return sortedfile

#---------------------------------------
#　重複の無いランダム数列を生成する関数
def makeRandintList(min, max, cnt):
    list = []
    i = 0
    if(max-min)<cnt:
        print "Wrong Value"
        return list

    while cnt !=i:
        r = random.randint(min,max-1)
        print r
        try :
            list.index(r)
        except ValueError, e:
            list.append(r)
            i = i+1
    return list


#-------------------------------------
# Number of Population = 200
# Number of sample = 10
# ソートして上位200個の中で10個のサンプルを抽出する
def RandomSamplingCSV(sortedfile,NumPop = 200, NumSample = 10):
    list = []
    print NumPop, NumSample
    fh = open(sortedfile, 'rb')
    randfile = sortedfile.replace("sorted","randomize")
    tmp_ = randfile[:10]
    tmp = randfile[10:].split('_')
    tmp2 = tmp[1]
    tmp[1] = tmp[0]
    tmp[0] = tmp2
    randfile2 = "%s%s_%s_%s"%(tmp_,tmp[0],tmp[1],tmp[2])
    print randfile, randfile2
    fw = open(randfile, 'wb')
    fw2 = open(randfile2, 'wb')
    reader = csv.reader(fh)
    writer = csv.writer(fw)
    writer2 = csv.writer(fw2)
    #rand = np.random.randint(NumPop, size=NumSample)
    #rand2 = np.random.randint(NumPop, size=NumSample)
    rand = makeRandintList(0,NumPop,NumSample)
    rand2 = makeRandintList(0,NumPop,NumSample)

    print rand, rand2
    for row in reader:
        list.append(row)

    for i in range(NumSample):
        writer.writerow(list[rand[i]])
    
    for j in range(NumSample):
        print list[rand2[j]]
        tp = list[rand2[j]][0]
        list[rand2[j]][0] = list[rand2[j]][1]
        list[rand2[j]][1] = tp
        print list[rand2[j]]
        writer2.writerow(list[rand2[j]])

    fh.close()
    fw.close()
    fw2.close()

def readNeuronList(filename):
    f = open(filename,'r')
    lines = f.readlines()
    comments = []
    CellName = []
    CellPath = []
    
    cnt = 0
    for line in lines:
        if(len(line)==0):
            continue
        elif line.startswith("#"):
            comments.append(line)
            print line
            if (cnt==0):
                tmp = line[:-1].rsplit(' ',1)
                print tmp
                NumCells = int(tmp[1])
                print tmp[1], NumCells
                cnt +=1
            elif(cnt==1) :
                tmp = line[:-1].rsplit(' ',1)
                print tmp
                NumPNs = int(tmp[1])
                print tmp[1], NumPNs
                cnt +=1
            elif(cnt==2):
                tmp = line[:-1].rsplit(' ',1)
                print tmp
                NumLNs = int(tmp[1])
                print tmp[1], NumLNs
                cnt +=1
            else:
                print "file reading error"
            continue
        data = line[:-1].split(' ')
        CellName.append(data[0])
        CellPath.append(data[1])
    num = [NumCells, NumPNs, NumLNs]
    CellInfo = [num, CellName, CellPath]
    f.close()
    return CellInfo

def main():
    NList = './List/NeuronList.dat'
    cellinfo = readNeuronList(NList)
    print "Read NeuronList\n"
    Num = cellinfo[0]
    NumCells = Num[0]
    NumPNs = Num[1]
    NumLNs = Num[2]
    cellname = cellinfo[1]
    cellpath = cellinfo[2]
    print cellname
    print cellpath
    print NumPNs, NumLNs, NumCells
    cells = [None for _ in range(NumCells)]
    SRList = [[] for _ in range(NumCells)] 
    CSVlist = []
    #Synapse Region List. append dendirte number which is Synapse Region Type
    SortedFile = []
    for i in range(NumCells):
        cells[i] = h.CellSwc(cellpath[i])
        swc.findSynapseRegion(cells[i], SRList[i])

    print "Calculate Distance\n"
    
    for i in range(NumCells):
        for j in range(NumCells):
            if(i == j):
                continue
            elif(i>j):
                continue
            print i, j
            if(os.path.exists("synlist") == False):
                os.mkdir("synlist")
            fn = './synlist/%s_%s_dist.csv'%(cellname[i],cellname[j])
            writeDistance(cells[i],SRList[i],cells[j],SRList[j], fn)
            CSVlist.append(fn)
        
    #CSVlist =["./synlist/LN[0]_LN[1]_dist.csv","./synlist/PN[0]_LN[0]_dist.csv","./synlist/PN[0]_LN[1]_dist.csv"]
    for csv in CSVlist:
        fn = sortCsv(csv)
        SortedFile.append(fn)
    
    for s in SortedFile:
        RandomSamplingCSV(s)
    
#main()

"""
print "sorting..."
sortCsv("./synlist/sampledist.csv")
"""


sortedlist =["./synlist/LN[0]_LN[1]_sorted.csv","./synlist/PN[0]_LN[0]_sorted.csv","./synlist/PN[0]_LN[1]_sorted.csv"]
for s in sortedlist:
    RandomSamplingCSV(s)

