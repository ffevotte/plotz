from plotz import *
from math import sin, pi

with Plot("plot") as p:
    p.title = r"Plotting functions"
    p.x.label = "$x$"
    p.y.label = "$y$"
    p.y.label_rotate = True

    #line1
    p.plot(Function(sin, samples=50, range=(0, pi)),
           title=r"$\sin(x)$")
    #line1

    #line2
    p.plot(Function(lambda x: sin(2*x), range=(0, pi)),
           title=r"$\sin(2\,x)$")
    #line2

    #line3
    p.plot(Function(lambda x: sin(3*x)),
           title=r"$\sin(3\,x)$")
    #line3

    p.legend("south west")
