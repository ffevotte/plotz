from plotz import *
from math import sin, pi

with Plot("plot") as p:
    p.title = r"Plotting data from files"

    p.x.min = 0
    p.x.max = 20.3
    p.x.ticks = 2
    p.x.label = r"$\omega$"

    p.y.min = 0
    p.y.max = 1
    p.y.ticks = 0.2
    p.y.tick_format = lambda y: "%.1f" % y
    p.y.label = r"$\displaystyle\frac{\Vert\phi_1\Vert_2}{\Vert\phi_0\Vert_2}$"

    for i in range(2):
        p.style.thickness[i] = "ultra thick"

    #line1
    p.plot(DataFile("mydata.dat"),
           title=r"Source Iterations")
    #line1

    #line2
    p.plot(DataFile("mydata.dat"), col=(0,2),
           title=r"DSA")
    #line2

    #line3
    p.plot(DataFile("mydata.csv", sep=";", comment="#"), col=(0,3),
           title=r"PDSA(6)")
    #line3
