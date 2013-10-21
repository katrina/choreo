
#!/usr/bin/python

import commands
import re
import sys

def get_tputs(files):
    data = []
    for filename in files:
        f = open(filename, "r")
        for line in f:
            src, dst, length, tput = line.split()
            data.append(float(tput))
        f.close()
    return data

data_dir = "./"
topologies = ["us-east-1a","us-east-1b","us-east-1c","us-east-1d"]

for t in topologies:
    filenames = commands.getoutput("find %s%s -name \"*.dat\"" % (data_dir, t)).split("\n")
    cdf_data = sorted(get_tputs(filenames))
    g = open("tmp-%s.dat" % t, "w")
    for i in range(len(cdf_data)):
        g.write("%f %f\n" % (cdf_data[i], float(i)/len(cdf_data)))
    g.close()

g = open("tmp.gp", "w")
g.write("set terminal postscript eps enhanced color \"Helvetica\" 24\n")
g.write("set output \"rate_cdf.eps\"\n")
g.write("set grid\n")
g.write("set yrange[0:1]\n")
g.write("set xrange[0:1000]\n")
g.write("set ylabel \"CDF\"\n")
g.write("set xlabel \"Throughput (Mbit/s)\"\n")
g.write("set key top left\n")
g.write("plot \"tmp-%s.dat\" u 1:2 w l lc 0 lt 1 lw 8 t \"%s\",\\\n" % (topologies[0], topologies[0]))
g.write("     \"tmp-%s.dat\" u 1:2 w l lc rgb \"#AAAAAA\" lt 1 lw 8 t \"%s\",\\\n" % (topologies[1], topologies[1]))
g.write("     \"tmp-%s.dat\" u 1:2 w l lc 0 lt 2 lw 8 t \"%s\",\\\n" % (topologies[2], topologies[2]))
g.write("     \"tmp-%s.dat\" u 1:2 w l lc rgb \"#888888\" lt 4 lw 8 t \"%s\"\n" % (topologies[3], topologies[3]))
g.close()

commands.getoutput("gnuplot tmp.gp")
commands.getoutput("rm tmp.gp")
for t in topologies:
    commands.getoutput("rm tmp-%s.dat" % t)
commands.getoutput("epstopdf rate_cdf.eps")
