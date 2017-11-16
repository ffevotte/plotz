from plotz import *
from math import sin, pi

with Plot("plot") as p:
    p.title = r"Plotting data from files"

    p.x.min = 0
    p.x.max = 20.3
    p.x.tick = 2
    p.x.label = r"$\omega$"

    p.y.min = 0
    p.y.tick = 0.2
    p.y.tick_format = lambda y: "%.1f" % y
    p.y.label = r"$\displaystyle\frac{\Vert\phi_1\Vert_2}{\Vert\phi_0\Vert_2}$"

    p.line_style(1, "ultra thick")
    p.line_style(2, "ultra thick")
    for line in range(3,8):
        p.line_style(line, "thick")

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

    p.legend("north east")
