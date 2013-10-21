#!/usr/bin/python

import commands
import math
import re
import sys

from collections import defaultdict

class CDF:
    '''Class to define CDFs.  Easy access to percentiles, among other things'''

    def __init__(self):
        self.data = defaultdict(int)

    def add_datapoint(self, dp):
        '''Add a datapoint'''
        self.data[dp] += 1

    def subsample(self, sample_rate):
        new_data = defaultdict(int)
        n = 0
        for key in self.data:
            n += self.data[key]
            while n >= sample_rate:
                new_data[key] += 1
                n -= sample_rate
        self.data = new_data

    def write_to_file(self, filename):
        f = open(filename, "w")
        total_so_far = 0
        total = sum(self.data.values())

        for value in sorted(self.data.keys()):
            count = self.data[value]
            total_so_far += count
            f.write("%s %f\n" % (str(value), float(total_so_far)/total))
        f.close()

def temporal_tput_graphs(files):

    # Read the data in
    data = defaultdict(list)
    for filename in files:
        f = open(filename, "r")
        instance_type = f.readline().split("=")[-1].rstrip()
        for line in f:
            src, dst, timestamp, tput = line.rstrip().split()
            data[(src, dst)].append((float(timestamp), float(tput)))
        f.close()

    # 1, 5, 10, 30 minutes
    taus = [i * 60 for i in [1, 5, 10, 30]]
    prediction_errors = defaultdict(CDF)

    # The graph in the paper used both xlarge and medium instances.
    # Removing the extra large instances, we actually see an even more
    # stable network.
    for pair in data:

        tputs = [e[1] for e in data[pair]]
        times = [e[0] for e in data[pair]]

        for i in range(len(times)):
            target_time = times[i]
            target_tput = tputs[i]

            for j in range(i):
                prediction_time = times[j]
                predicted_tput = tputs[j]

                delta = target_time - prediction_time

                for tau in taus:
                    # Make sure delta is roughly equal to tau (it won't be perfect)
                    if .95*tau <= delta and 1.05*tau >= delta:
                        error = math.fabs((target_tput - predicted_tput))/float(target_tput)
                        prediction_errors[tau].add_datapoint(error)

    for tau in taus:
        # The graph takes *forever* to draw if we don't subsample
        prediction_errors[tau].subsample(100)
        prediction_errors[tau].write_to_file("tau-%d.cdf" % tau)

directory = "ec2/"
files = commands.getoutput("find %s -maxdepth 1 -name \"temporal*.dat\"" % directory).split("\n")
temporal_tput_graphs(files)

g = open("tmp.gp", "w")
g.write("set terminal postscript eps enhanced color \"Helvetica\" 20\n")
g.write("set output \"tau.eps\"\n")
g.write("set grid\n")
g.write("set ylabel \"CDF\"\n")
g.write("set xlabel \"Percent Error\"\n")
g.write("set yrange[0:]\n")
g.write("set xrange[:10]\n")
g.write("set key bottom right samplen 1\n")
g.write("set style line 1 lt 1 lw 8 lc rgb \"#7608AA\"\n")
g.write("set style line 2 lt 2 lw 8 lc rgb \"#028E9B\"\n")
g.write("set style line 3 lt 3 lw 8 lc rgb \"#FF7800\"\n")
g.write("set style line 4 lt 7 lw 8 lc rgb \"#000000\"\n")
g.write("plot 'tau-60.cdf' u ($1*100):2 w l ls 1 t \"1min\",\\\n")
g.write("'tau-300.cdf' u ($1*100):2 w l ls 2 t \"5min\",\\\n")
g.write("'tau-600.cdf' u ($1*100):2 w l ls 3 t \"10min\",\\\n")
g.write(" 'tau-1800.cdf' u ($1*100):2 w l ls 4 t \"30min\"\n")
g.close()

commands.getoutput("gnuplot tmp.gp")
commands.getoutput("rm tmp.gp")
commands.getoutput("rm tau-60.cdf rm tau-300.cdf rm tau-600.cdf rm tau-1800.cdf")
commands.getoutput("epstopdf tau.eps")
