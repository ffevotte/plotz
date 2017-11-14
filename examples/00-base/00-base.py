from plotz import *
from math import sin, pi

with Plot("00-base") as p:
    p.title = r"My first \texttt{PlotZ} plot"
    p.x.label = "$x$"
    p.y.label = "$y$"
    p.y.label_rotate = True

    p.plot(Function(sin, samples=50, range=(0, pi)),
           title=r"$\sin(\pi \, x)$")

    p.legend("north east")
