# This script parses a netlist in Cadnetix format and generates .xdc pinlist information
import copy

thisFileName = 'netlistToXdc'

infilename = 'FPGA_Bank115.NET'
targetRefDes = 'U2'

# set_property -dict {PACKAGE_PIN V5 } [get_ports [list SFP_ACCLK_N]]

# LVCMOS18, LVCMOS25, LVCMOS33, ''
defaultIoStandard = ''

# LVDS, LVDS_25
if(defaultIoStandard == 'LVCMOS18'):
    diffpairIoStandard = 'LVDS'
elif( (defaultIoStandard == 'LVCMOS25') or (defaultIoStandard == 'LVCMOS33') ):
    diffpairIoStandard = 'LVDS_25'
else: 
    diffpairIoStandard = ''

if defaultIoStandard != '':
    ioStandardMarker = ' IOSTANDARD '
else:
    ioStandardMarker = ''
    
outfilename = infilename[:-4] + '_out.xdc'

startKey = 'NODENAME '
startKeyLen = len(startKey)
inhandle = open(infilename)

mytext = inhandle.readlines()
inhandle.close()

nlines = len(mytext)

print(thisFileName + ': read ', nlines, ' lines from file ', infilename, '\n')

line = 0
numnodes = 0
noderecords = list()
localstore = list()

def findNextNonWhiteChar (astr, currentIdx):
    try:
        iter(astr)
    except:
        raise
    
    idx = copy.deepcopy(currentIdx)
    while idx < len(astr) and (astr[idx] == ' ' or astr[idx] == '\t'):
        idx += 1
    
    if astr[idx]==' ' or astr[idx]=='\t':
        return False
    return idx


def findNextWhiteChar (astr, startIdx):
    try:
        iter(astr)
    except:
        raise 
    
    idx = copy.deepcopy(startIdx)
    while idx < len(astr) and astr[idx] != ' ' and astr[idx] != '\t' and astr[idx] != '\n':
        idx += 1
    
    return idx

def getNextWord (astr, startIdx):
    try:
        iter(astr)
    except:
        raise
    
    first = findNextNonWhiteChar (astr, startIdx)
    last = findNextWhiteChar(astr, first)

    return astr[first:last], (last)

def findMatchingSublist (alist, sublistIdx, thingToMatch):
    idx = 0
    while idx<len(alist) and alist[idx][sublistIdx] != thingToMatch:
        idx += 1
    
    if idx <= len(alist):
        return idx
    
    return False

while (line < nlines):
    if mytext[line].startswith(startKey):
        thisline = mytext[line]
        thisnode = thisline[startKeyLen:(thisline.find('$', startKeyLen))]
        thisnode = thisnode.rstrip()
        noderecord = list()
        noderecord.append(thisnode)
        noderecord.append(0)
        noderecords.append(noderecord)
        line += 1
        thisline = mytext[line]

        #get list of reference designators and pin numbers in this line
        refs = list()
        charidx = 0
        while charidx < len(thisline):
            pair = list()

            # get ref des
            word, charidx = getNextWord(thisline, charidx)
            if (word != ''):
                pair.append (word)

                # get pin number
                word, charidx = getNextWord(thisline, charidx)
                if(word != ''):
                    pair.append(word)
            else:
                charidx += 1

            refs.append(pair)

        if any(targetRefDes in s for s in refs):
            numnodes += 1

            for sublist in refs:
                if len(sublist) > 0:
                    if sublist[0] == targetRefDes:
                        pin = sublist[1]
                        nodeidx = findMatchingSublist(noderecords, 0, thisnode)
                        if nodeidx != False:
                            noderecords[nodeidx][1] += 1
                        else:
                            print('all nodes have been read.')

                        if thisnode.endswith('_N') or thisnode.endswith('_P'):
                            ioStandard = diffpairIoStandard
                        else:
                            ioStandard = defaultIoStandard

                        outline = ['set_property -dict {PACKAGE_PIN ', pin, ioStandardMarker, ioStandard, '} [get_ports [list ', thisnode, ']]']
                        localstore.append(outline)

    line += 1    

print('\n', thisFileName + ': found ', numnodes, ' numnodes')

#sort by differential IOSTANDARD
localstore.sort(key=lambda localstore: localstore[3])
ofh = open(outfilename, "w")

#write constraints
for i in range(0, len(localstore)):
    outline = ''.join(localstore[i]) + '\n'
    ofh.write(outline)

#write comments with pins per node
outline = '\n# pins per node, target refdes (' + targetRefDes + ') only\n'
ofh.write(outline)
for sublist in noderecords:
    if sublist[1] > 0:
        outline = '# node: ' + sublist[0] + ' num pins this node: ' + str(sublist[1]) + '\n'
        ofh.write(outline)

ofh.close()