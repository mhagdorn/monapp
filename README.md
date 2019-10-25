# monapp
The monapp python module can be used to monitor memory and CPU usage of a
process.

You can instantiate a monitor using
```python
monitor = monapp.getMonitor(pid,output)
```
where `pid` is the PID of the process to be monitored and `output` the name of
the output file. If the PID is not specified the PID of the current process is
used. No data is written if the output file is not specified.

Once a monitor is instantiated you can get the current resource usage
```python
resources = monitor.current()
```
or the peak usage
Once a monitor is instantiated you can get the current resource usage
```python
resources = monitor.peak()
```
where the dictionary `resources` contains the percentage CPU and memory usage.

You can specify additional output files using
```python
resources = monitor.output(fname)
```

The package also includes two programs. Use
* `monapp 'some command' ` to monitor launch and monitor an application
* `plotMonapp` to plot the output
