from neuron import h
from itertools import chain

h.load_file("nrngui.hoc")

h.load_file("CellSwc.hoc")

pn_filename = "./SWC/PN/toroid/050622_4_sn.swc"
rn_filename = "./SWC/070224_SN-23-R.swc"

pc = h.ParallelContext()
pc.runworker()

NUMRN = 50 #number of recepter neurons
recepters = []
projection = None

def mkNetwork(NumRN):
    mkcells(NumRN)
    connectcells(NumRN)

def mkcells(NumRN):
    nil = h.Section()
    if pc.id()==0:
        projection = h.CellSwc(pn_filename)
        pc.set_gid2node(0,pc.id())
        nc = connect2target(projection,nil)
        pc.cell(0,nc)
    else:
        i=pc.id()
        while i <= NumRN:
            rn = make_RN()
            recepters.append(rn)
            pc.set_gid2node(i,pc.id())
            nc = connect2target(rn, nil)
            pc.cell(i,nc)
            i+=pc.nhost()
#---------------------------------------------
#Make recepter neuron
#---------------------------------------------
def mk_RN():
    rn = h.Section()
    rn.nseg = 10
    rn.diam = 10
    rn.L = 150
    rn.insert('hh')
    for seg in chain(rn):
        seg.hh.gnabar = 0.0001
        seg.hh.gkbar  = 0.01
    return rn

def connect2target(source, target):
    nc = h.NetCon(source(0.5)._ref_v,target,sec = source)
    nc.threshold = 10
    return nc

def connectcells(NumRN):
    nclist = []
    for i in range(NumRN):
        targid = 0
        gidexists = pc.gid_exists(targid)
        print "pc.gid_exists "+str(gidexists)+" "+str(i)
        if(gidexists==0):
            print "continue"
            continue
        target = pc.gid2cell(targid)
        syn = target.synlist[0]
        nc = pc.gid_connect(i,syn)
        nc.delay = 0.1
        nc.weight = 0.01
        print "done?"

print "mkNetwork"
mkNetwork(NUMRN)

def mkstim(target):
    if pc.gid_exists(target)!=0:
        stim = h.NetStim()
        stim.number = 1
        stim.start = 0
        ncstim = h.NetCon(stim, pc.gid2cell(target))
        ncstim.delay = 0
        ncstim.weight = 0.01
        
for i in range(NUMRN):
    mkstim(i+1)

print "mkNetwork done"
tstop = 10
pc.set_maxstep(10)
stdinit()
pc.psolve(tstop)
print "runworker"
pc.runworker()
pc.done()
quit()
