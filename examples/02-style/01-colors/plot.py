from plotz import *
from math import sin, pi

def test(colormap):
    with Plot(colormap) as p:
        p.title = r"%s colormap" % colormap
        p.x.label = "$x$"
        p.y.label = "$y$"
        p.legend.show = False

        p.style.colormap(colormap)
        p.style.thickness = ["ultra thick"] * 8

        for i in range(8):
            p.plot(Function(lambda x: sin(x-i*pi/8), samples=50, range=(0, pi)),
                   title=r"$\sin(x)$")

for name in ["default", "dark", "paired", "spectral8"]:
    test(name)
