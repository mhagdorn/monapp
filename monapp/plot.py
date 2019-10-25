from matplotlib import pyplot
import numpy
import math
import argparse

DTYPES = {
    'time' : float,
    'CPU' : float,
    'nThreads' : int,
    'RSS' : int,
    'VMS' : int,
    'percentFree' : float
    }

UNIT = ['KB','MB','GB','TB']

def loadData(fname):
    data = {}
    with open(fname,'r') as infile:
        h = infile.readline()
        data['header'] = h.split()[-1]
        h = infile.readline()
        data['cmd'] = ' '.join(h.split()[1:])
        h = infile.readline()[1:]
        cols = h.split()
        for c in cols:
            data[c] = []
        for line in infile.readlines():
            line = line.split()
            for i in range(len(line)):
                c = cols[i]
                if c in DTYPES:
                    data[c].append(DTYPES[c](line[i]))
                else:
                    data[c].append(line[i])
        for c in cols:
            data[c] = numpy.array(data[c])
    return data

def plot(data,fname=None):

    fig, (ax0, ax1, ax2) = pyplot.subplots(nrows=3, sharex=True)

    ax2.plot(data['time'],data['nThreads'])
    ax2.set_ylabel('nThreads')
    ax2.set_xlabel('time [s]')

    ax1.plot(data['time'],data['CPU'])
    ax1.plot(data['time'],100-data['percentFree'])
    ax1.set_ylabel('percentage')
    
    # sort out memory units
    m = max(numpy.max(data['RSS']),
            numpy.max(data['VMS']))
    rlog = math.log(m)/math.log(2)//10.
    mfactor = 2**(-rlog*10)
    munit = UNIT[int(rlog)-1]

    ax0.plot(data['time'],data['RSS'][:]*mfactor)
    ax0.plot(data['time'],data['VMS'][:]*mfactor)
    ax0.set_ylabel('memory usage [%s]'%munit)

    if fname is None:
        pyplot.show()
    else:
        pyplot.savefig(fname)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data",help="name of the data file to read")
    parser.add_argument("-o","--output",help="save output plot")
    args = parser.parse_args()
    
    data = loadData(args.data)
    plot(data,args.output)
    
if __name__ == '__main__':
    main()
