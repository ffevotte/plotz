from math import sin, pi
from plotz import Plot, Function, DataFile
from plotz.utils import Markers

with Plot("plot") as p:
    p.title = "Line patterns"
    p.x.label = "$x$"
    p.y.label = "$y$"

    # dashed
    p.style.dashed()
    p.style.colormap("monochrome")
    # dashed

    N = 8
    fun = [lambda x, j=i: sin(2*pi*x)+(N+1)-N/(N-1.)*j for i in range(N)]

    for i in range(N):
        p.plot(Function(fun[i], samples=40, range=(0, 1)), title=r"pattern %d" % i)

    p.legend("east", "west")
    p.legend.margin = 1


with Plot("monochrome") as p:
    p.title = r"Monochrome plot"

    p.x.min = 0
    p.x.max = 20.3
    p.x.ticks = 2
    p.x.label = r"$\omega$"

    p.y.min = 0
    p.y.max = 1
    p.y.ticks = 0.2
    p.y.tick_format = lambda y: "%.1f" % y
    p.y.label = r"$\displaystyle\frac{\Vert\phi_1\Vert_2}{\Vert\phi_0\Vert_2}$"

    p.style.dashed()
    p.style.colormap("monochrome")

    # line thickness
    p.style.thickness[0] = "ultra thick"
    p.style.thickness[1] = "ultra thick"
    p.style.thickness[2] = "very thick"
    # line thickness

    p.plot(DataFile("mydata.dat"), title=r"Source Iterations")

    p.plot(DataFile("mydata.dat"), col=(0,2), title=r"DSA")

    # explicit dashed pattern
    p.plot(DataFile("mydata.dat"), col=(0,3), title=r"PDSA(6)").style({
        "pattern": 3,
    })
    # explicit dashed pattern
