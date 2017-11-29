from plotz import *
from math import sin, pi

with Plot("plot") as p:
    p.title = r"My first \texttt{PlotZ} plot"
    p.x.label = "$x$"
    p.y.label = "$y$"

    p.plot(Function(sin, samples=50, range=(0, pi)),
           title=r"$\sin(x)$")

    p.legend("north east")
