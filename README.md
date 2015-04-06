# monapp
This is a simple python wrapper script that runs a program in a subprocess and
monitors its system resources:
 * user and system CPU time
 * rss, vms, sharred, text, lib, data and dirty memory
 * read_count, write_count, read_bytes and write_bytes I/O counters

Statistics are written periodically to a file.

