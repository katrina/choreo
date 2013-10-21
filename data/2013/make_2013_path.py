#!/usr/bin/python

import commands
import math
import re
import sys

def get_data(files):
    data = []
    for filename in files:
        f = open(filename)
        instance_type = f.readline().split("=")[-1].rstrip()
        # For the paper, we only reported medium instances
        if (instance_type != "c1.medium"):
            f.close()
            continue
        for line in f:
            src, dst, length, tput = line.split()
            data.append((int(length), float(tput)))
        f.close()
    return data

directory = "ec2/"
files = commands.getoutput("find %s -maxdepth 1 -name \"topo-*.dat\"" % directory).split("\n")
data = sorted(get_data(files))

# Create the CDF
g = open("tr-c1.medium.scatter", "w")
for (length, tput) in data:
    g.write("%d %f\n" % (length, tput))
g.close()

# Create the graph
g = open("tmp.gp", "w")
g.write("set terminal postscript eps enhanced color \"Helvetica\" 20\n")
g.write("set output \"path-length.eps\"\n")
g.write("set grid\n")
g.write("set ylabel \"Bandwidth (Mbit/s)\"\n")
g.write("set xlabel \"Path Length (Number of Hops)\"\n")
g.write("set xrange[0:9]\n")
g.write("set xtics (1, 2, 4, 6, 8)\n")
g.write("set style line 1 lt 1 lw 8 lc rgb \"#000000\"\n")
g.write("plot 'tr-c1.medium.scatter' u 1:2 w p ls 1 title \"\"\n")
g.close()

x =commands.getoutput("gnuplot tmp.gp")
commands.getoutput("rm tmp.gp")
commands.getoutput("rm tr-c1.medium.scatter")
commands.getoutput("epstopdf path-length.eps")


