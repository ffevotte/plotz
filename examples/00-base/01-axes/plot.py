from math import exp
from plotz import *
from plotz.utils import ppfloat

with Plot("plot") as p:
    p.title = "Iterations count as a function of the scattering ratio"

    p.x.scale = Axis.logarithmic
    p.x.label = r"$\varepsilon = 1-c$"

    # range
    p.x.max = p.x.scale(0.6)
    # range

    # ticks: step
    p.x.ticks = 1
    # ticks: step

    # log scale
    p.y.scale = Axis.logarithmic
    # log scale

    # label
    p.y.label = r"\# iter"
    # label

    # label rotate
    p.y.label_rotate = True
    # label rotate

    # label shift
    p.y.label_shift *= 0.8
    # label shift

    # ticks: list
    p.y.ticks = [1, 2, 3]
    # ticks: list

    # ticks format
    p.y.tick_format = lambda x: ppfloat(10**x)
    # ticks format

    p.plot(DataFile("iter.dat"), title="SI")
    p.plot(DataFile("iter.dat"), col=(0,2), title="DSA")
    p.plot(DataFile("iter.dat"), col=(0,3), title="PDSA(3)")
    p.plot(DataFile("iter.dat"), col=(0,4), title="PDSA(4)")
