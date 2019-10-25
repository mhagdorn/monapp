__all__ = ['getMonitor']

import os
import psutil
import subprocess
import multiprocessing
import platform
import time
from queue import Empty

# list of currently active monitors
monitors = {}

class PercentMemoryFree:
    def __init__(self):
        self._uid = os.getuid()

        # attempt to get total memory
        p = subprocess.Popen('ulimit -v',shell=True,stdout=subprocess.PIPE)
        m = p.stdout.read().strip()
        try:
            self._total = float(m.strip())*1024
        except:
            self._total = float(psutil.virtual_memory().total)

    @property
    def uid(self):
        """the uid of the process"""
        return self._uid
    @property
    def total(self):
        """the total amount of available virtual memory"""
        return self._total

    def __call__(self):
        """get the current total percentage of memory used"""
        used = 0
        for p in psutil.process_iter():
            try:
                if p.uids().effective == self.uid:
                    used+=p.memory_info().rss
            except:
                pass
        return 100.*(self.total-used)/self.total

percentMemoryFree = PercentMemoryFree()

class MonitorWorker(multiprocessing.Process):
    """monitor worker process"""
    def __init__(self,pid,tQ,rQ):
        """
        parameters
        ----------
        pid - pid of program to monitor
        tQ - task queue
        rQ - result queue
        """
        super().__init__()
        
        self.tQ = tQ
        self.rQ = rQ
        self.p = psutil.Process(pid)
        self.info = ' '.join(self.p.cmdline())
        
        self.pRSS = 0
        self.pVMS = 0
        self.pCPU = 0
        self.pFree = 100.

        self.outputs = {}

        self.daemon = True

    def run(self):
        ts = time.time()
        tstart = ts
        while True:
            time.sleep(0.1)
            m = None
            cpu = None
            pFree = None
            if self.p.is_running():
                with self.p.oneshot():
                    m = self.p.memory_info()
                    cpu = self.p.cpu_percent()
                    nThreads = self.p.num_threads()
                    pFree = percentMemoryFree()
                    self.pRSS = max(self.pRSS,m.rss)
                    self.pVMS = max(self.pVMS,m.vms)
                    self.pCPU = max(self.pCPU,cpu)                
                    self.pFree = min(self.pFree,pFree)
                
            t = time.time()
            if t-ts>1:
                for o in self.outputs:
                    self.outputs[o].write("%.2f %.2f %d %d %d %.2f\n"%(t-tstart,cpu,nThreads,m.rss,m.vms,pFree))
                    self.outputs[o].flush()
                ts = t

            task = None
            try:
                task,arg = self.tQ.get(False)
            except Empty:
                continue
            
            if task == 'stop':
                for o in self.outputs:
                    self.outputs[o].close()
                return
            elif task == 'current':
                results = {}
                results['pFree'] = pFree
                if m is not None and cpu is not None:
                    results['cpu'] = cpu
                    results['rss'] = m.rss
                    results['vms'] = m.vms
                else:
                    results['cpu'] = None
                    results['rss'] = None
                    results['vms'] = None
                self.rQ.put(results)
            elif task == 'peak':
                results = {}
                results['cpu'] = self.pCPU
                results['rss'] = self.pRSS
                results['vms'] = self.pVMS
                results['pFree'] = self.pFree
                self.rQ.put(results)
            elif task == 'output':
                if arg not in self.outputs:
                    o = open(arg,'w')
                    o.write("#host: %s\n"%platform.node())
                    o.write("#cmdline: %s\n"%self.info)
                    o.write("#time CPU nThreads RSS VMS percentFree\n")
                    self.outputs[arg] = o
                
                

class MonitorProcess:
    """monitor a process"""
    def __init__(self,pid=None):
        """
        Parameters
        ----------
        pid - pid of process to monitor, if set to None use own pid
        """
        
        self.tQ = multiprocessing.Queue()
        self.rQ = multiprocessing.Queue()

        if pid is None:
            p = os.getpid()
        else:
            p = pid

        self.worker = MonitorWorker(p,self.tQ,self.rQ)
        self.worker.start()

    def __del__(self):
        self.tQ.put(('stop',None))

    def current(self):
        """get a dictionary containing current resource usage
        pFree: percentage memory free
        rss: rss memory
        vms: vms memory
        cpu: percentage CPU"""
        self.tQ.put(('current',None))
        return self.rQ.get()

    def peak(self):
        """get a dictionary containing peak resource usage
        pFree: percentage memory free
        rss: rss memory
        vms: vms memory
        cpu: percentage CPU"""
        self.tQ.put(('peak',None))
        return self.rQ.get()

    def output(self,fname):
        """write monitor info to file fname"""
        if fname is not None:
            self.tQ.put(('output',fname))

def getMonitor(pid=None,out=None):
    """
    get a resource monitor

    use existing monitor if monitor for pid does not exist already

    Parameters
    ----------
    pid - pid of process to monitor, if set to None use own pid
    out - if not None, write monitor data to file out
    """
    if pid is None:
        p = os.getpid()
    else:
        p = pid

    if pid not in monitors:
        monitors[pid] = MonitorProcess(pid=pid)
    if out is not None:
        monitors[pid].output(out)

    return monitors[pid]
    
                
if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        pid = int(sys.argv[1])
    else:
        pid = None
    m = getMonitor(pid,"monitor.data")
    m2 = getMonitor(pid)
    print (m.current())
    for i in range(10):
        print (m.current(),m.peak())
        print (m2.current(),m2.peak())
        print ()
        time.sleep(1)
    print (m.peak())
