from math import sin, pi
from plotz import *
from plotz.utils import Markers

with Plot("plot") as p:
    p.title = "markers"
    p.x.label = "$x$"
    p.y.label = "$y$"

    p.style.colormap("dark")

    N = 6
    fun = [lambda x, j=i: sin(2*pi*x)+(N+1)-N/(N-1.)*j for i in range(N)]

    # markers
    p.plot(Function(fun[0], samples=20, range=(0, 1)), title=r"line 0").style({
        "markers": True,
    })
    # markers

    # oneInN
    p.plot(Function(fun[1], samples=20, range=(0, 1)), title=r"line 1").style({
        "markers": True,
        "markers_filter": Markers.oneInN(2),
    })
    # oneInN

    # oneInN start
    p.plot(Function(fun[2], samples=20, range=(0, 1)), title=r"line 2").style({
        "markers": True,
        "markers_filter": Markers.oneInN(2, 1),
    })
    # oneInN start

    # equallySpaced
    p.plot(Function(fun[3], samples=100, range=(0, 1)), title=r"line 3").style({
        "markers": True,
        "markers_filter": Markers.equallySpaced(0.15),
    })
    # equallySpaced

    p.plot(Function(fun[4], samples=100, range=(0, 1)), title=r"line 4").style({
        "markers": True,
        "markers_filter": Markers.equallySpaced(0.15, 0.1),
    })

    # no line
    p.plot(Function(fun[5], samples=20, range=(0, 1)), title=r"line 5").style({
        "markers": True,
        "line": False
    })
    # no line

    p.legend("east", "west")
