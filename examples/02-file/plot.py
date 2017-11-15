from plotz import *
from math import sin, pi

# with open("mydata.dat", "w") as gnuplot, open("mydata.csv", "w") as csv:
#     N = 100
#
#     gnuplot.write("# x       \t sin(pi x) \t sin(2 pi x)\n")
#     csv.write("# x         ; sin(3 pi x) ; sin(4 pi x)\n")
#     for i in xrange(N+1):
#         x = float(i)/N
#         gnuplot.write(" \t ".join(["%.7f" % v for v in [x, sin(pi*x), sin(2*pi*x)]]) + "\n")
#         csv.write("   ; ".join(["%.7f" % v for v in [x, sin(3*pi*x), sin(4*pi*x)]]) + "\n")

with Plot("plot") as p:
    p.title = r"Plotting data from files"
    p.x.label = "$x$"
    p.y.label = "$y$"
    p.y.label_rotate = True

    #line1
    p.plot(DataFile("mydata.dat"),
           title=r"$\sin(\pi\,x)$")
    #line1

    #line2
    p.plot(DataFile("mydata.dat"), col=(0,2),
           title=r"$\sin(2\,\pi\,x)$")
    #line2

    #line3
    p.plot(DataFile("mydata.csv", sep=";", comment="#"),
           title=r"$\sin(3\,\pi\,x)$")
    #line3

    p.legend("south west")
