from neuron import h
import neuron as nrn
import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain
hoc = nrn.hoc.HocObject()

h.load_file("nrngui.hoc")
h.load_file("CellSwc.hoc")
h.load_file("stdlib.hoc")

pn_filename = "./SWC/PN/toroid/050622_4_sn.swc"
rn_filename = "./SWC/070224_SN-23-R.swc"
PNcells = h.CellSwc(pn_filename)

for sec in h.allsec():
    sec.insert('hh')

STOPTIME = 8000
TIMESTEP = 0.025
"""
sh = h.PlotShape(1)
sh.scale(0,0)
sh.size(-140,140,-140,140)
"""
#parent, child -> get from neuron pointprocess
#parent+2, child+2 ->swcfile numbering

class swc(object):
    ID = 0
    Type = 0
    x = 0.0
    y = 0.0
    z = 0.0
    diam = 0.0
    parentID = 0


def make_synapse(cellswc):
    num_dend = len(cellswc.Dend)
    #print "num_dend = %d"%(num_dend)
    random = np.random.randint(num_dend,size = 350)
    print random

def readSWCfile(filename):
    swcFile = open(filename, 'r')
    swcdata = swcFile.readlines()
    
    while swcdata[0][0] == '#':
        del swcdata[0]
    #del swcdata[0] #comment out 2014.12.09
    #print swcdata

    #seclist is section list
    seclist = [swc() for _ in range(len(swcdata))]

    for i in range(len(swcdata)):
        seclist_ = swcdata[i].split()
        seclist[i].ID       = int(seclist_[0])
        seclist[i].Type     = int(seclist_[1])
        seclist[i].x        = float(seclist_[2])
        seclist[i].y        = float(seclist_[3])
        seclist[i].z        = float(seclist_[4])
        seclist[i].diam     = float(seclist_[5])
        seclist[i].parentID = int(seclist_[6].rstrip('\n'))
        #print "%d %d %f %f %f %f %d"%(seclist[i].ID,seclist[i].Type,seclist[i].x,seclist[i].y,seclist[i].z,seclist[i].diam,seclist[i].parentID)
    return seclist


def forward_tracing(child, seclist, dendlist):
    if (child) == len(seclist):
        return
    for i in range(child,len(seclist)):
        if seclist[child].ID == seclist[i].parentID:
            dendlist.append(seclist[i].ID-2)
          #  print i, seclist[i].ID
            forward_tracing(i, seclist, dendlist)

def reverse_tracing(child, seclist, dendlist):
    if child == 0:
        return
    for i in range(child,0,-1):
        if seclist[child].parentID == seclist[i].ID:
            dendlist.append(seclist[i].ID-2)
            #print i, seclist[i].ID
            reverse_tracing(i, seclist, dendlist)

def findChildren(parent, child, filename, dendlist):
    seclist = readSWCfile(filename)
    #    print child, seclist[child].ID,seclist[child].parentID, parent, seclist[parent].ID,seclist[parent].parentID
    if seclist[child].parentID == seclist[parent].ID:
        print 'forward\n'
        forward_tracing(child, seclist, dendlist)
    elif seclist[parent].parentID == seclist[child].ID:
        print 'reverse\n'
        reverse_tracing(child, seclist, dendlist)
    else:
        print 'error\n'

#calculate section axial resistance(internal resistance)
def Calc_SRi(cell, num_sec):
    sri = cell.Dend[num_sec].Ra /((np.pi)*(cell.Dend[num_sec].diam/2)**2) * np.power(10,8)
    #print cell.Dend[num_sec].Ra, cell.Dend[num_sec].diam
    return sri

#calcuate section membrane resistance
def Calc_SRm(cell, num_sec):
    srm = 1/(cell.Dend[num_sec].gl_hh * cell.Dend[num_sec].L) * 10000
    return srm

def Calc_LengthConstant(cell, num_sec):
    Ri = Calc_SRi(cell, num_sec)
    Rm = Calc_SRm(cell, num_sec)
    lc  = np.sqrt(Rm/Ri)
    return lc


#h('diam_shape()')

#-------------------------------------
#Find Childrens
#-------------------------------------
DENDLIST = []
findChildren(207+1, 208+1, pn_filename, DENDLIST)
findChildren(336+1, 369+1, pn_filename, DENDLIST)
print DENDLIST
print len(DENDLIST)

for sec in h.allsec():
    for i in range(int(h.n3d())):
        pass
        #    print i, h.x3d(i), h.y3d(i), h.z3d(i), h.diam3d(i)
   # print h.psection()

normalized_length_sum = []
def Calc_SumOfNormalizedLength(cell, dendlist, sum_list):
    sum_ = 0;
    for i in range(len(dendlist)):
        #normalized_length = cell.Dend[i].L / Calc_LengthConstant(cell, dendlist[i])
        normalized_length = cell.Dend[dendlist[i]].L / Calc_LengthConstant(cell, dendlist[i])
        #fixed 2015.01.08
        sum_ = sum_ + normalized_length
        sum_list.append(sum_)
    return sum_

#-----------------------------------
#Normalizing Length
#----------------------------------
sum_nl = Calc_SumOfNormalizedLength(PNcells, DENDLIST, normalized_length_sum)
print "sum_nl:%d"%(sum_nl)

#NUMBEROFSYNAPSE = 350
NUMBEROFSYNAPSE = 50
def matching_RandomNumbers_and_NormalizedLengthSum(cell, dendlist, sum_list, sumofnl, numberofsynapse):
    synapse_list = []
    rnd = sumofnl * np.random.random(numberofsynapse)
    print "len(rnd):%d"%(len(rnd))
    print "len(sum_list):%d"%(len(sum_list))
    print sum_list
    k=0
    for i in range(len(rnd)):
        for j in range(len(sum_list)):
            if j==0:
                if(sum_list[j]>=rnd[i]):
                    synapse_list.append(dendlist[j])
            if j>0:
                if(sum_list[j-1]<rnd[i])&(sum_list[j]>=rnd[i]):
                    synapse_list.append(dendlist[j])
                    if(k!=i):
                        print "ERROR %d, %d"%((k-i),rnd[k])
                    k+=1
                    print dendlist[j], sum_list[j], rnd[i],i,j
    return synapse_list

#-----------------------------------
#make synapse
#-----------------------------------
SYNLIST = matching_RandomNumbers_and_NormalizedLengthSum(PNcells, DENDLIST, normalized_length_sum, sum_nl, NUMBEROFSYNAPSE)
print SYNLIST

def write_Synlist(synlist):
    f = open('SynapseList.dat','w')
    f.write(repr(len(synlist))+'\n')
    for i in range(len(synlist)):
        data = "%d\n"%synlist[i]
        f.write(data)
    f.close()
#write_Synlist(SYNLIST)

#SYNLIST = [1115,770,1005,1012,485,330,898,1083,954,215]
#to find synapse with "Shape View" in NEURON
#for i in range(len(SYNLIST)):
#    PNcells.Dend[SYNLIST[i]].diam = 20

def make_ExpSyn(cell, synlist):
    syn = [None for _ in range(len(synlist))]
    print "len(synlist):%d"%(len(synlist))
    for i in range(len(synlist)):
        syn[i] = h.ExpSyn(0.5, sec = cell.Dend[synlist[i]])
        #print i, synlist[i]
    return syn

def make_Sections(num_rn):
    rn = [None for _ in range(num_rn)]
    for i in range(num_rn):
        rn[i] = h.Section()
        rn[i].nseg = 10
        rn[i].diam = 10
        rn[i].L = 150
        rn[i].insert('hh')
        for seg in chain(rn[i]):
            seg.hh.gnabar = 0.0001
            seg.hh.gkbar  = 0.01
    return rn

RNperSyn = 5
RN = make_Sections(NUMBEROFSYNAPSE*RNperSyn)
Syn = make_ExpSyn(PNcells, SYNLIST)

def make_NetCon(rn, syn,weight,rnpersyn):
    nc = [None for _ in range(len(rn))]
    j=0
    for i in range(len(rn)):
        if (i!=0)&((i%rnpersyn)==0):
            j+=1
        print len(rn), i,j
        nc[i] = h.NetCon(rn[i](0.05)._ref_v, syn[j],sec = rn[i])
        nc[i].weight[0] = weight
    return nc
WEIGHT = 10/float(NUMBEROFSYNAPSE)
NCLIST = make_NetCon(RN, Syn,WEIGHT,RNperSyn)

span = STOPTIME/TIMESTEP
#time_vec   = h.Vector(span)
#STIM_VEC   = h.Vector(span)

def SetIClamp_fromDATA(length,amp,filename, stim_vec, time_vec, ic): #freq -> frequency
    ic.delay = 0
    ic.dur   = 1e9
    stim_flg = []

    for i in range(int(span)):
        time_vec.x[i] = TIMESTEP * i

    stim_flg = [False for _ in range(int(span))]

    readspikedat = open(filename,'r')
    spiketiming = readspikedat.readlines()
    num_spike = int(spiketiming[len(spiketiming)-1])
    spT = [None for _ in range(num_spike)]
    for i in range(num_spike):
        spT[i] = spiketiming[i].rstrip('\n')
        spT[i] = float(spT[i])-6.0

    j = 0
    for i in range(int(span)):
#        print i, spT[j], time_vec.get(i)
        if j<num_spike-1:
            if ((spT[j]*1000)<=time_vec.get(i))&((spT[j+1]*1000)>time_vec.get(i)):
                stim_flg[i] = True
                j +=1
          
    flg = 0
    stim_on = False
    for i in range(int(span)):
        if(stim_flg[i] == True):
            stim_on = True
        if(stim_on == True):
            if(flg == 0):
                start_time = time_vec.x[i]
                flg = 1
               
            if(time_vec.get(i)==start_time):
                stim_vec.x[i] = 0
            elif((time_vec.get(i)-start_time)<=POLAR_T):
                stim_vec.x[i] = -amp
            elif((time_vec.get(i)-start_time)<=length+POLAR_T):
                stim_vec.x[i] = amp
            elif((time_vec.get(i)-start_time)<=L_RATIO*length+POLAR_T):
                stim_vec.x[i] = -amp * A_RATIO
            else:
                stim_vec.x[i] = 0
                stim_on = False
                flg = 0
        #print "%f  \t%f"%(time_vec.x[i],stim_vec.x[i])
  
    #stim_vec.play(ic._ref_amp, time_vec,1)
    #   stim_vec.printf("%5.5f\n")
    return stim_vec


Time_vec   = h.Vector(span)
for i in range(int(span)):
    Time_vec.x[i] = TIMESTEP * i
    
STIM_VEC   = [h.Vector(span) for _ in range(len(RN))]
IC         = [h.IClamp(0.95, sec=RN[i]) for i in range(len(RN))]


LENGTH     = 0.5
AMPLITUDE  = 15
L_RATIO    = 2.0 # ratio of length (pre+post)/pre
A_RATIO    = 0.3 # ratio of amplitude
POLAR_T    = 0.0

stnum = np.random.randint(100, size=NUMBEROFSYNAPSE)
for i in range(len(RN)):
    fname = "./spiketiming/spiketiming"+str(stnum[i])+".dat"
    print fname
    STIM_VEC[i] = SetIClamp_fromDATA(LENGTH,AMPLITUDE,fname,STIM_VEC[i],Time_vec, IC[i])
    STIM_VEC[i].play(IC[i]._ref_amp, Time_vec, 1)

volt_time  = h.Vector()
rn1        = h.Vector()
rn2        = h.Vector()
pn1        = h.Vector()
vec_i      = h.Vector()
rn_rec = [h.Vector() for _ in range(len(RN))]
def setVoltageRecord():
    volt_time.record(h._ref_t)
    for i in range(len(RN)):
        rn_rec[i].record(RN[i](0.05)._ref_v)
    pn1.record(PNcells.Dend[990](0.5)._ref_v)
    vec_i.record(IC[0]._ref_i)

setVoltageRecord()


h.tstop = STOPTIME
h.dt    = TIMESTEP

h.run()


def CopyVector_to_List(vector, List):
    size = int(vector.size())
    for i in range(size):
        List.append(vector.get(i))
time_lt = []
rn11 = []
rn22 = []
pn11 = []
stim_lt = []
rn_list = [[] for i in range(len(RN))]
CopyVector_to_List(volt_time, time_lt)
for i in range(len(RN)):
    CopyVector_to_List(rn_rec[i],rn_list[i])
CopyVector_to_List(pn1, pn11)
CopyVector_to_List(vec_i, stim_lt)

resultf = open("PNsimulationResult.dat",'w')
resultf.writelines('#Synapse number '+str(SYNLIST)+'\n')
resultf.writelines('#spiketiming file number '+ str(stnum)+'\n')
for i in range(len(time_lt)):
    resultf.writelines(str(time_lt[i])+'\t'+str(pn11[i])+'\n')
resultf.close()

flg = plt.figure()
for i in range(1):
    plt.plot(time_lt, rn_list[i])
plt.plot(time_lt, pn11)
twin = plt.twinx()
twin.plot(time_lt,stim_lt,'y')
twin.set_ylim(-100,100)
plt.savefig("mkPNsynapse.png")


