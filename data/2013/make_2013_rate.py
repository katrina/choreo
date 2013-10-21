#!/usr/bin/python

import commands
import math
import re
import sys

def create_cdfs(files):
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
            data.append(float(tput))
        f.close()
    return data

directory = "ec2/"
files = commands.getoutput("find %s -maxdepth 1 -name \"topo-*.dat\"" % directory).split("\n")
data = sorted(create_cdfs(files))

# Create the CDF
g = open("netperf-c1.medium.cdf", "w")
for i in range(len(data)):
    g.write("%f %f\n" % (data[i], float(i)/len(data)))
g.close()

# Create the graph
g = open("tmp.gp", "w")
g.write("set terminal postscript eps enhanced color \"Helvetica\" 20\n")
g.write("set output \"tput.eps\"\n")
g.write("set grid\n")
g.write("set ylabel \"CDF\"\n")
g.write("set xlabel \"Bandwidth (Mbit/s)\"\n")
g.write("set yrange[0:]\n")
g.write("set xrange[:1200]\n")
g.write("set key bottom right samplen 1\n")
g.write("set style line 1 lt 1 lw 8 lc rgb \"#000000\"\n")
g.write("plot 'netperf-c1.medium.cdf' u 1:2 w l ls 1 t \"\"\n")
g.close()

commands.getoutput("gnuplot tmp.gp")
commands.getoutput("rm tmp.gp")
commands.getoutput("rm netperf-c1.medium.cdf")
commands.getoutput("epstopdf tput.eps")
