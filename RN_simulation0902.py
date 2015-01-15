from neuron import h
import os
import neuron
import stfio
import numpy as np
import matplotlib.pyplot as plt
from time import localtime, strftime
h = neuron.hoc.HocObject()

h('load_file("CellSwc.hoc")')
h('load_file("nrngui.hoc")')
h('load_file("stdlib.hoc")')

h('objref cell')
h('cell = new CellSwc("./SWC/070224_SN-23-R.swc")')
#h('forall insert hh')
h('forall insert GPeA')
#h.cell.insert('GPea')

"""
sh = h.PlotShape(1)
sh.scale(0,0)
sh.size(-140,140,-140,140)
sh.exec_menu("Shape Plot")
"""

STIM_POINT = 187
STOPTIME   = 100
TIMESTEP   = 0.025
LENGTH     = 0.75
AMPLITUDE  = 3
FREQUENCY  = 300
L_RATIO    = 2.0 # ratio of length (pre+post)/pre
A_RATIO    = 1.0 # ratio of amplitude
POLAR_T    = 0.0


volt_time  = h.Vector()
RN1        = h.Vector()
RN2        = h.Vector()
RN3        = h.Vector()
vec_i      = h.Vector()

ic         = h.IClamp(0.5, sec=h.cell.Dend[STIM_POINT])

def setVoltageRecord():
    volt_time.record(h._ref_t)
    RN1.record(h.cell.Dend[STIM_POINT](0.5)._ref_v)
    RN2.record(h.cell.Dend[0](0.5)._ref_v)
    RN3.record(h.cell.Dend[343](0.5)._ref_v)
    vec_i.record(ic._ref_i)
    
def writeVoltage():
    h('objref mt,outfile')
    h('mt = new Matrix()')
    h('outfile = new File()')
        
    h.mt.resize(volt_time.size(), 3)
    h.mt.setcol(0,volt_time)
    h.mt.setcol(1,RN1)
    h.mt.setcol(2,vec_i)

    h.mt.printf("%5.5f  \t")
    h.outfile.wopen("iclamp.txt")
    #h('mt.fprint(outfile,"5.5f  ")')
    h.outfile.close()

span       = STOPTIME/TIMESTEP
time_vec   = h.Vector(span)
stim_vec   = h.Vector(span)

def SetIClamp(length,amp,freq): #freq -> frequency
    ic.delay = 0
    ic.dur   = 1e9
    stim_flg = []

    for i in range(int(span)):
        time_vec.x[i] = TIMESTEP * i
        stim_flg = [0]*int(span)

    if freq > 0:
        step = (1000.0/freq)/TIMESTEP
        step = int(round(step,0))
        for i in range(int(span)):
           if i%step == 0:
               stim_flg[i] = True
 #              print i , time_vec.x[i]
    
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
  
    stim_vec.play(ic._ref_amp, time_vec,1)
    #   stim_vec.printf("%5.5f\n")
    return stim_vec

time_lt  = [] #list of time
rn1_lt   = [] #list of voltage
rn2_lt   = [] 
rn3_lt   = []
stim_lt  = [] #list of stimulation

def CopyVector_to_List(vector, List):
    size = int(vector.size())
    for i in range(size):
        List.append(vector.get(i))

h.tstop = STOPTIME
h.dt    = TIMESTEP

stim_vec2 = SetIClamp(LENGTH,AMPLITUDE,FREQUENCY)
stim_vec2.play(ic._ref_amp, time_vec, 1)
#SetIClamp(1,10)
#SetIClamp_hoc(h.stim, 1, 10)
setVoltageRecord()
h.run()
writeVoltage()

CopyVector_to_List(volt_time, time_lt)
CopyVector_to_List(RN1, rn1_lt)
CopyVector_to_List(RN2, rn2_lt)
CopyVector_to_List(RN3, rn3_lt)

CopyVector_to_List(vec_i, stim_lt)

flg = plt.figure()
plt.plot(time_lt, rn1_lt)
#plt.plot(time_lt, rn2_lt)
plt.plot(time_lt, rn3_lt)
plt.xlabel("time[ms]")
plt.ylabel("voltage[mV]")
twin = plt.twinx()
twin.plot(time_lt, stim_lt,'y')
twin.set_ylabel("iclamp[nA]")
twin.set_ylim(-100, 100)
TEXT = 'GPea\n'+'LENGTH = '+str(LENGTH)+' AMPLITUDE = '+str(AMPLITUDE)+' FREQUENCY = '+str(FREQUENCY)+'\nL_RATIO = ' + str(L_RATIO) + ' A_RATIO = '+str(A_RATIO)+' POLAR_T = '+str(POLAR_T)
ymin, ymax = plt.ylim()
plt.text(2,ymin+5, TEXT, fontsize = 10)
timestr = strftime("%m%d%H%M%S",localtime())
plt_filename = './graph/output'+timestr+'.png'
print plt_filename
plt.savefig(plt_filename)
plt.show()
h.psection()
"""
nframe = 0
h.cell.translation(30, 0, 0)
"""

"""
def step():
    for i in range(nstep_steprun):
        advance()

    sh.rotate(60,0,0,0,rotationPerStep,0)
    Plot()

    if 0:
        sh.printfile("temp.ps")
        os.system("pstopnm -xsize 1024 -ysize 1024 -portrait -xborder 0 -yborder 0 temp.ps")

        os.system("ppmtoyuvsplit temp temp*.ppm")
        command = "mv temp*.ppm frames/LAL-VPC_model_"+nframe+".ppm"
        os.system(command)
        nframe = nframe +1

"""
