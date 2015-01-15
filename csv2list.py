# coding : utf-8

#-----------------------
# 2015.01.14
# Heewon Park
#-----------------------

# CSV file to Hoc list
import csv
import re
import os

def csv2list(synlistname):
    i = 0
    fh = open(synlistname,'rb')
    outfile = synlistname.replace("csv", "txt")
    fw = open(outfile,'wb')
    reader = csv.reader(fh)
    
    pattern = re.compile(r'CellSwc\[(\d+)\]\.Dend\[(\d+)\]')
    for row in reader:
        if (i == 0):
            fprintrow(row, pattern, fw, 1)
        else:
            fprintrow(row, pattern, fw, 0)
        i += 1
        
    fh.close()
    fw.close()

def fprintrow(row, pattern, fw, first = 0):
    tmplist = []

    tmpstr = row[0]
    result = pattern.search(tmpstr)
    tmpsearch = result.groups()
    tmplist.append(tmpsearch[1])
    pre = tmpsearch[0]

    tmpstr = row[1]
    result = pattern.search(tmpstr)
    tmpsearch = result.groups()
    tmplist.append(tmpsearch[1])
    post = tmpsearch[0]    

    if(first):
        fw.write('CellSwc[' + str(pre) + '] ')
        fw.write('CellSwc[' + str(post) + ']\n')
        fw.write('----------\n')

    for elem in tmplist:
        fw.write(elem)
        fw.write(' ')
    fw.write('\n')
   
def mklists():
    dirlist = os.listdir("./synlist/")
    i = 0
    for elem in dirlist:
        if('randomize.csv' in elem):
            print elem
            i += 1
            inputname = ('synlist/'+ elem)
            csv2list(inputname)

mklists()
